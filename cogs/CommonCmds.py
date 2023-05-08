import discord
from discord.ext import commands
from discord import app_commands
import random
import os
from datetime import datetime

class CommonCmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("CommonCmds.py is ready!")

    @app_commands.command(name="ping", description="Shows the bot's latency in ms.")
    async def ping(self, interaction: discord.Interaction) -> None:
        bot_latency = round(self.client.latency * 1000)
        await interaction.response.send_message(f"Test: {bot_latency} ms")

    @app_commands.command(name="roll", description="Rolls a dice from 1 - 6.")
    async def roll(self, interaction: discord.Interaction):
        roll_message = str(random.randint(1, 6))
        await interaction.response.send_message(f"You rolled: `{roll_message}`")

    @app_commands.command(name="time", description="Tells time in integer form")
    async def time(self, interaction: discord.Interaction):
        time = datetime.now()
        time_int = 10000000000 * time.year + 100000000 * time.month + 1000000 * time.day + 10000 * time.hour + 100 * time.minute + time.second
        await interaction.response.send_message(time_int)

async def setup(client):
    await client.add_cog(CommonCmds(client), guilds=[discord.Object(id=os.getenv("GUILD_ID"))])
