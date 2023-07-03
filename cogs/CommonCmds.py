import discord
from discord.ext import commands
from discord import app_commands
import random
import os

class CommonCmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("CommonCmds.py is ready!")

    @app_commands.command(name="ping", description="Shows the bot's latency in ms.")
    async def ping(self, interaction: discord.Interaction) -> None:

        # multiplying latency to be able to get ms equivalent
        bot_latency = round(self.client.latency * 1000)
        await interaction.response.send_message(f"Test: {bot_latency} ms")

    @app_commands.command(name="roll", description="Rolls a dice from 1 - 6.")
    async def roll(self, interaction: discord.Interaction):
        roll_message = str(random.randint(1, 6))
        await interaction.response.send_message(f"You rolled: `{roll_message}`")

async def setup(client):
    await client.add_cog(CommonCmds(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])
    