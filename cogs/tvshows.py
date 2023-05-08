import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from database import Database
from InteractiveButtons import ButtonView
from datetime import datetime

class TVShows(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("tvshows.py is ready!")

    @app_commands.command(name="display", description="Displays your watched TV Shows")
    async def display(self, interaction: discord.Interaction):
        userid = interaction.user.id
        username = interaction.user.name

        with Database("tv_shows.db") as db:
            db.execute(f'SELECT show_name, show_seasons, show_current_ep FROM user_{userid} ORDER BY timestamp DESC')
            name_data = db.fetchall()
            tv_shows = []
            tv_seasons = []
            tv_episodes = []
            for rows in name_data:
                tv_shows.append(rows[0])
                tv_seasons.append(rows[1])
                tv_episodes.append(rows[2])

        embeds = []
        for i in range(0, len(tv_shows), 10):
            embed = discord.Embed(title=username, color=discord.Color.random())
            list_of_shows = tv_shows[i:i+10]
            list_of_seasons = tv_seasons[i:i+10]
            list_of_episodes = tv_episodes[i:i+10]

            tv_shows_str = map(str, list_of_shows)
            tv_seasons_str = map(str, list_of_seasons)
            tv_episodes_str = map(str, list_of_episodes)
            embed.add_field(
                name="Title",
                value="\n".join(tv_shows_str),
                inline=True
            )
            embed.add_field(
                name="Season",
                value="\n".join(tv_seasons_str),
                inline=True
            )
            embed.add_field(
                name="Episode",
                value="\n".join(tv_episodes_str),
                inline=True
            )
            embeds.append(embed)

        if len(embeds) == 0:
            await interaction.response.send_message("No entries in your list.")
        elif len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0])
        else:
            # creating the buttons
            view = ButtonView(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view)

    @app_commands.command(name="addshow", description="adds a show into your list")
    async def addshow(self, interaction: discord.Interaction, name: str):
        # get information about user and time
        userid = interaction.user.id
        username = interaction.user.name
        time = datetime.now()

        # requesting information from REST API
        response = requests.get(f"https://api.tvmaze.com/search/shows?q={name}")
        showid = response.json()[0]["show"]["id"]
        show_info = requests.get(f"https://api.tvmaze.com/shows/{showid}")
        show_info_seasons = requests.get(f"https://api.tvmaze.com/shows/{showid}/seasons")

        # getting the information we need from the API
        show_name = show_info.json()["name"]
        episode_count = show_info_seasons.json()[0]["episodeOrder"]

        try:
            with Database("tv_shows.db") as db:
                db.execute(f'''CREATE TABLE IF NOT EXISTS user_{userid} (
                user_id integer, 
                user_name text, 
                timestamp text,
                show_id integer PRIMARY KEY,
                show_name text,
                show_seasons integer,
                show_current_ep text
                )''')
                db.execute(f'INSERT INTO user_{userid} VALUES(?, ?, ?, ?, ?, ?, ?)', (
                    userid,
                    username,
                    time,
                    showid,
                    show_name,
                    1,
                    f'0/{episode_count}'))

            await interaction.response.send_message(f"`{show_name}` has been added to your list.")
        except Exception as e:
            await interaction.response.send_message(f"This show is already in your list!")
            print(e)

    @app_commands.command(name="removeshow", description="removes a show into your list")
    async def removeshow(self, interaction: discord.Interaction, name: str):
        # get information about user
        userid = interaction.user.id

        # requesting information from REST API
        response = requests.get(f"https://api.tvmaze.com/search/shows?q={name}")
        showid = response.json()[0]["show"]["id"]
        show_info = requests.get(f"https://api.tvmaze.com/shows/{showid}")

        # getting the information we need
        show_name = show_info.json()["name"]

        with Database("tv_shows.db") as db:
            db.execute(f'DELETE from user_{userid} where user_id = {userid} and show_id = {showid}')

        if db.rowcount() == 0:
            await interaction.response.send_message("The given show is not in your list!")
        else:
            await interaction.response.send_message(f"`{show_name}` has been removed from your list.")

    @app_commands.command(name="editseason", description="Edits the season of a listing in your list")
    async def editseason(self, interaction: discord.Interaction, name: str, season: int):
        # get information about user and time
        userid = interaction.user.id
        time = datetime.now()

        # requesting information from REST API
        response = requests.get(f"https://api.tvmaze.com/search/shows?q={name}")
        showid = response.json()[0]["show"]["id"]
        show_info_seasons = requests.get(f"https://api.tvmaze.com/shows/{showid}/seasons")

        # getting the information we need
        season_amount = len(show_info_seasons.json())

        if 0 < season < season_amount+1:
            episode_count = show_info_seasons.json()[season-1]["episodeOrder"]
            with Database("tv_shows.db") as db:
                db.execute(
                    f'UPDATE user_{userid} '
                    f'SET timestamp = "{time}", show_seasons = {season}, show_current_ep = "0/{episode_count}" '
                    f'WHERE show_id = {showid}'
                )

            if db.rowcount() == 0:
                await interaction.response.send_message("The show you are trying to update does not exist in your list.")
            else:
                await interaction.response.send_message("Entry Updated Successfully.")
        else:
            await interaction.response.send_message("Please enter a valid season!")

    @app_commands.command(name="editep", description="Edits the episode count of a listing in your list")
    async def editep(self, interaction: discord.Interaction, name: str, episode: int):
        # get information about user and time
        userid = interaction.user.id
        time = datetime.now()

        # requesting information from REST API
        response = requests.get(f"https://api.tvmaze.com/search/shows?q={name}")
        showid = response.json()[0]["show"]["id"]
        show_info_seasons = requests.get(f"https://api.tvmaze.com/shows/{showid}/seasons")

        try:
            with Database("tv_shows.db") as db:
                db.execute(f'SELECT show_seasons FROM user_{userid} WHERE show_id = {showid}')
                season_data = db.fetchone()
                season_count = season_data[0]
                episode_count = show_info_seasons.json()[season_count - 1]["episodeOrder"]

            if episode_count is None:
                with Database("tv_shows.db") as db:
                    db.execute(
                        f'UPDATE user_{userid} '
                        f'SET timestamp = "{time}", show_current_ep = "{episode}" '
                        f'WHERE show_id = {showid}'
                    )
                await interaction.response.send_message("Entry Updated Successfully.")
            elif -1 < episode < episode_count + 1:
                with Database("tv_shows.db") as db:
                    db.execute(
                        f'UPDATE user_{userid} '
                        f'SET timestamp = "{time}", show_current_ep = "{episode}/{episode_count}" '
                        f'WHERE show_id = {showid}'
                    )
                await interaction.response.send_message("Entry Updated Successfully.")
            else:
                await interaction.response.send_message("Please enter a valid episode count!")
        except Exception as e:
            await interaction.response.send_message("The show you are trying to update does not exist in your list.")
            print(e)

async def setup(client):
    await client.add_cog(TVShows(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])
