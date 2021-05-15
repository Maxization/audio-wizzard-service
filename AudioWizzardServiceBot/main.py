import asyncio
import os

import discord
import requests

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
API_URL = os.getenv('API_URL')

bot = commands.Bot(command_prefix='!')

q_list = [
    'Your name',
    'Your age',
    'Number of songs you listen to per day']


def get_song_title(message):
    start = message.find('*')
    end = message.find('*', start + 1)
    if start == -1 or end == -1:
        return ""
    return message[(start+1):end]


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    title = get_song_title(message.content)
    print(title)
    await bot.process_commands(message)


action_types = ['delete', 'set']
param_types = ['age, listening-behaviour']

@bot.command(name='account', help='Manage your account')
async def account(ctx, action, param=None, value=None):

    def check():
        if action == 'delete' or param is None or value is None or
            return

    if action == 'delete':
        # TODO: delete information from database
        await ctx.send(f'Information about {ctx.message.author.mention} deleted')
    elif action == 'set':
        check()

        await ctx.send(action)


@bot.command(name='hello', help='Hello from AWS')
async def hello(ctx):
    response = requests.get(API_URL + '/hello')
    await ctx.send(response.text)


@bot.command(name='interview', help='Collects basic information')
async def interview(ctx):
    await ctx.send("You will be asked a series of questions to create your Profile. If you accidentally typed this "
                   "wait 5 seconds after first question to cancel.")

    a_list = []
    channel = await ctx.author.create_dm()

    def check(m):
        return m.content is not None and m.channel == channel

    await asyncio.sleep(3)

    for question in q_list:
        await channel.send(question)
        await asyncio.sleep(0.5)

        try:
            msg = await bot.wait_for('message', check=check, timeout=5)
        except asyncio.TimeoutError:
            await channel.send("Canceled")
            return

        a_list.append(msg.content)

    await channel.send('You have completed the interview, type ``submit`` to confirm or anything to cancel')
    await asyncio.sleep(0.5)
    msg = await bot.wait_for('message', check=check)
    if "submit" in msg.content.lower():
        answers = "\n".join(f'{a}. {b}' for a, b in enumerate(a_list, 1))
        submit_msg = f'''**Submission - Created by {msg.author.mention}** \n{answers}'''
        await channel.send(submit_msg)
    else:
        submit_msg = f'''**Submission - Canceled by {msg.author.mention}**'''
        await channel.send(submit_msg)


bot.run(TOKEN)
