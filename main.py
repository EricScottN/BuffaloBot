import os
import logging
import googlemaps
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='buf ', intents=intents)

@bot.event
async def on_ready():
    try:
        print(f'{bot.user.name} has connected to Discord!')
        for filename in os.listdir('./startup_cogs'):
            if filename.endswith('.py'):
                bot.load_extension(f'startup_cogs.{filename[:-3]}')
        print('Start up cogs loaded successfully')
    except Exception as e:
        print(e)

if __name__ == '__main__':
    bot.run(os.getenv('TOKEN'))

