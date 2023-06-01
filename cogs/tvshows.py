import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from helperclasses.database import Database
from helperclasses.InteractiveButtons import ButtonView
from datetime import datetime

class TVShows(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("tvshows.py is ready!")

    @app_commands.command(name="display", description="Displays your watched TV Shows")
    async def display(self, interaction: discord.Interaction):

        # gathering user information
        userid = interaction.user.id
        username = interaction.user.name

        # accessing SQLite database for my data
        with Database("tv_shows.db") as db:
            db.execute(f'SELECT show_name, show_seasons, show_current_ep FROM user_{userid} ORDER BY timestamp DESC')
            name_data = db.fetchall()
            tv_shows = []
            tv_seasons = []
            tv_episodes = []
            for data in name_data:
                tv_shows.append(data[0])
                tv_seasons.append(data[1])
                tv_episodes.append(data[2])

        # creating the embeds
        # using [i:i+10] in order to create embeds that only store 10 entries per embed
        # this allows me to include buttons later on that go from page to page or embed
        # to embed
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

        # making sure I have an embed, if I don't, return the given message below
        # if i only have 1 embed, I will just display that 1 embed with no buttons attached
        # if theres more than 1, it will add the buttons to go page to page
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

        # trying to create data for the given show name, but if my show is already in the list,
        # it will print out an error and display that the show is already in the list or that
        # the show doesn't exist.
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
            await interaction.response.send_message(f"This show is already in your list or the show doesn't exist!")
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

        # accessing database to delete the given show
        with Database("tv_shows.db") as db:
            db.execute(f'DELETE from user_{userid} where user_id = {userid} and show_id = {showid}')

        # if the deletion doesn't delete anything, it will display that the show wasn't in your list,
        # but if it does delete something, it will show that you removed the show from your list
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

        # basically tells you if the season count is in range of how many seasons the show
        # actually has, then it will execute the following code, otherwise, it will display that
        # it is not a valid season
        # It will also check if anything was updated and if it wasn't, then it will display that
        # the show doesn't exist in your list
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

        # trying to edit database with new episode count, but if the show doesn't exist in your list,
        # it will display an error and output that the show doesn't exist in your list
        try:
            with Database("tv_shows.db") as db:
                db.execute(f'SELECT show_seasons FROM user_{userid} WHERE show_id = {showid}')
                season_data = db.fetchone()
                season_count = season_data[0]
                episode_count = show_info_seasons.json()[season_count - 1]["episodeOrder"]
        
            # if the API gives an empty episode count, we can enter any number of
            # episode count without any restrictions
            if episode_count is None:
                with Database("tv_shows.db") as db:
                    db.execute(
                        f'UPDATE user_{userid} '
                        f'SET timestamp = "{time}", show_current_ep = "{episode}" '
                        f'WHERE show_id = {showid}'
                    )
                await interaction.response.send_message("Entry Updated Successfully.")
            
            # otherwise, it will check if the episode count you entered is a valid count and
            # then run the same code
            elif -1 < episode < episode_count + 1:
                with Database("tv_shows.db") as db:
                    db.execute(
                        f'UPDATE user_{userid} '
                        f'SET timestamp = "{time}", show_current_ep = "{episode}/{episode_count}" '
                        f'WHERE show_id = {showid}'
                    )
                await interaction.response.send_message("Entry Updated Successfully.")
            
            # if the episode count doesn't fit into range, it will output that the count isn't valid
            else:
                await interaction.response.send_message("Please enter a valid episode count!")
        except Exception as e:
            await interaction.response.send_message("The show you are trying to update does not exist in your list.")
            print(e)

async def setup(client):
    await client.add_cog(TVShows(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])
