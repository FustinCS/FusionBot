import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("API_KEY")
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".", intents=intents, application_id=os.getenv("APP_ID"))

@client.event
async def on_ready():
    print("Fusion Bot is Online!")

@client.command()
async def sync(ctx) -> None:
    fmt = await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Synced {len(fmt)} commands.")

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with client:
        await load()
        await client.start(token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Program terminated by user')
