import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from helperclasses.InteractiveButtons import ButtonView

class Anilist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("anilist.py is ready!")

    @app_commands.command(name="profile", description="Displays anime profile.")
    async def profile(self, interaction: discord.Interaction, username: str):

        # fetching data using GraphQL for anilist
        url = 'https://graphql.anilist.co'

        # creating query to only retrieve the information I want
        query = '''
            query ($username: String) {
                MediaListCollection (userName: $username, type: ANIME, status: COMPLETED, sort: SCORE_DESC) {
                    user {
                        name
                    }
                    lists {
                        entries {
                            progress
                            score(format: POINT_10_DECIMAL)
                            media {
                                title {
                                    english
                                    romaji
                                }
                                format
                            }
                        }
                    }
                }
            }
        '''

        # creating username variable to be able to specify someone's username in the query
        variables = {
            'username': username
        }

        # gathering all the information from my query and storing it in variables via requests library
        response = requests.post(url, json={'query': query, 'variables': variables})
        json_data = response.json()

        user_name = json_data['data']['MediaListCollection']['user']['name']
        all_anime_list = json_data['data']['MediaListCollection']['lists'][0]['entries']

        # need to create a list of titles, scores, and format to be able to create multiple embeds
        # so you can go from page to page with each page only displaying 10 animes
        anime_titles = []
        anime_scores = []
        anime_format = []
        for titles in all_anime_list:
            individual_anime = titles['media']['title']['english']
            if individual_anime is None:
                individual_anime = titles['media']['title']['romaji']
            if len(individual_anime) > 50:
                individual_anime = individual_anime[:50-3] + "..."
            anime_titles.append(individual_anime)
            anime_scores.append(titles['score'])
            anime_format.append(titles['media']['format'])

        # creating the embeds
        # using [i:i+10] in order to store 10 entries per page
        embeds = []
        for i in range(0, len(anime_titles), 10):
            embed = discord.Embed(title=user_name, color=discord.Color.random())
            list_of_anime = anime_titles[i:i+10]
            list_of_anime_format = anime_format[i:i+10]
            list_of_scores_int = anime_scores[i:i+10]
            list_of_scores_string = map(str, list_of_scores_int)

            embed.add_field(
                name="Title",
                value="\n".join(list_of_anime),
                inline=True
            )
            embed.add_field(
                name="Score",
                value= "\n".join(list_of_scores_string),
                inline=True
            )
            embed.add_field(
                name="Type",
                value="\n".join(list_of_anime_format),
                inline=True
            )
            embeds.append(embed)

        # creating the buttons
        view = ButtonView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)

async def setup(client):
    await client.add_cog(Anilist(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])
