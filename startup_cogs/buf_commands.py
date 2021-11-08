import os
import googlemaps
from discord.ext import commands

key = os.getenv("MAPS_API")


class BufCommands(commands.Cog, name='Buffalo Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wings',
                      help='Get best wing locations for your area. Just pass your city or town! If no location is '
                           'passed, will return results for Buffalo')
    async def wings(self, ctx, *, location):
        if not location:
            location = 'Buffalo'
        gmaps = googlemaps.Client(key=key)
        wings_list = gmaps.places(f'wings in {location}, NY')['results']
        if not wings_list:
            return await ctx.send(f'Unable to find any wing spots in {location}')
        sorted_wings_list = sorted(wings_list, key=lambda d: d['rating'], reverse=True)
        response = '\n**TOP FIVE RESTAURANTS**\n'
        for x, business in enumerate(sorted_wings_list[:3], start=1):
            if business['business_status'] != 'OPERATIONAL':
                continue
            response += f'```{x}.\n'
            response += f"NAME: {business['name']}\n"
            response += f"ADDRESS: {business['formatted_address']}\n"
            response += f"RATING: {business['rating']}\n"
            response += f"TOTAL RATINGS: {business['user_ratings_total']}```\n"

        await ctx.send(response)

def setup(bot):
    bot.add_cog(BufCommands(bot))
