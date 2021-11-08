import os
import googlemaps
from discord.ext import commands

key = os.getenv("maps_api")


class BufCommands(commands.Cog, name='Buffalo Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wings',
                      help='Get best wing locations for your area. Just pass your location!')
    async def wings(self, ctx, location):
        if not location:
            location = 'Buffalo'

        gmaps = googlemaps.Client(key=key)
        wings_list = gmaps.places(f'wings in {location}, NY')
