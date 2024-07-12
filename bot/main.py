import discord
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("No BOT_TOKEN environment variable set")

# Initialize intents
intents = discord.Intents.default()
intents.guilds = True
intents.reactions = True
intents.members = True
intents.message_content = True
intents.messages = True

# Create bot instance
bot = commands.Bot(command_prefix='&', intents=intents)

# Load cogs
initial_extensions = [
    'cogs.roles',
    'cogs.admin',
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
    print(f'Bot is ready! Logged in as {bot.user}')

bot.run(TOKEN)