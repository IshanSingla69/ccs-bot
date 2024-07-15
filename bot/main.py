import os

import discord
from config import Config
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

activity = discord.Activity(type=discord.ActivityType.competing, name="Syrinx")

bot = commands.Bot(
    command_prefix="&", intents=intents, activity=activity, status=discord.Status.dnd
)

initial_extensions = [
    "cogs.roles",
    "cogs.admin",
    "cogs.syrinx",
]


async def load_cogs():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Loaded extension: {extension}")
        except Exception as e:
            print(f"Failed to load extension {extension}: {type(e).__name__} - {e}")


@bot.event
async def on_ready():
    await load_cogs()
    print(f"Bot is ready! Logged in as {bot.user}")


bot.run(os.getenv("TOKEN"))
