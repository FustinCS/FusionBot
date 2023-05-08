import discord
from discord.ext import commands
from discord import app_commands
import os
from bs4 import BeautifulSoup
import requests

class Weather(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("weather.py is ready!")

    @app_commands.command(name="weather", description="Tells Weather of Specified City")
    async def weather(self, interaction: discord.Interaction, city: str):
        # To be able to fetch correct URL (ex: Daly City = Daly+City)
        city_string = city.replace(" ", "+")
        url = f"https://www.google.com/search?q=weather+{city_string}"

        # To be able to Scrape from Google.com
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        LANGUAGE = "en-US,en;q=0.5"

        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        session.headers['Accept-Language'] = LANGUAGE
        session.headers['Content-Language'] = LANGUAGE

        result = session.get(url)
        doc = BeautifulSoup(result.text, "html.parser")

        # Storing all my scraped information into variables
        city_name = doc.find("span", attrs={"class": "BBwThe"}).text
        fahrenheit = doc.find("span", attrs={"id": "wob_tm"}).text
        celsius = doc.find("span", attrs={"id": "wob_ttm"}).text
        weather_type = doc.find("span", attrs={"id": "wob_dc"}).text
        date = doc.find("div", attrs={"id": "wob_dts"}).text
        wind_mph = doc.find("span", attrs={"id": "wob_ws"}).text
        wind_km = doc.find("span", attrs={"id": "wob_tws"}).text

        # Stores picture of weather to be able to use in discord embed
        input_tag = doc.find("img", attrs={"class": "wob_tci"})
        pfp = f"https:{input_tag['src']}"

        # creating the embed
        embed = discord.Embed(title=city_name, description=weather_type, color=discord.Color.random())
        embed.set_thumbnail(url=f"{pfp}")
        embed.add_field(name="Temperature", value=f"{fahrenheit} °F / {celsius} °C", inline=False)
        embed.add_field(name="Wind Speed", value=f"{wind_mph} / {wind_km}", inline=False)
        embed.set_footer(text=date)
        await interaction.response.send_message(embed=embed)


async def setup(client):
    await client.add_cog(Weather(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])