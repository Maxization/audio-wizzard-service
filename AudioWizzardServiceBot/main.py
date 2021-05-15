import os
import requests

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='hello', help='Hello from AWS')
async def hello(ctx):
    response = requests.get(API_URL + '/hello')
    await ctx.send(response.text)

bot.run(TOKEN)
