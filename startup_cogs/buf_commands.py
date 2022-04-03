import os
import googlemaps
import discord
from discord.ext import commands, menus
from discord.ext.menus import button, First, Last
import requests
import pandas as pd
import numpy as np

key = os.getenv("MAPS_API")


class MyMenuPages(menus.MenuPages, inherit_buttons=False):
    @button('<:track_previous:>', position=First(0))
    async def go_to_first_page(self, payload):
        await self.show_page(0)

    @button('<:arrow_backward:>', position=First(1))
    async def go_to_previous_page(self, payload):
        await self.show_checked_page(self.current_page - 1)

    @button('<:arrow_forward:>', position=Last(1))
    async def go_to_next_page(self, payload):
        await self.show_checked_page(self.current_page + 1)

    @button('<:track_next:>', position=Last(2))
    async def go_to_last_page(self, payload):
        max_pages = self._source.get_max_pages()
        last_page = max(max_pages - 1, 0)
        await self.show_page(last_page)

    @button('<:stop_check:>', position=Last(0))
    async def stop_pages(self, payload):
        self.stop()


class MySource(menus.ListPageSource):
    def __init__(self, entries, search, *, per_page):
        super().__init__(entries, per_page=per_page)
        self.search = search

    async def format_page(self, menu, entries):
        embed = discord.Embed(title='Helpful Phone Numbers',
                              description="A list of helpful phone numbers")
        value = entries.to_markdown(tablefmt="grid", index=False)
        embed.add_field(name=f'Results for "{self.search}"' if self.search else 'All Results',
                        value=f'`{value}`',
                        inline=True)
        return embed


class BufCommands(commands.Cog, name='Buffalo Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wings',
                      help='Get best wing locations for your area. Just pass your city or town! If no location is '
                           'passed, will return results for Buffalo')
    async def wings(self, ctx, *location):
        if not location:
            location = 'Buffalo'
        gmaps = googlemaps.Client(key=key)
        wings_list = gmaps.places(f'wings in {location}, NY')['results']
        if not wings_list:
            return await ctx.send(f'Unable to find any wing spots in {location}')
        sorted_wings_list = sorted(wings_list, key=lambda d: d['rating'], reverse=True)
        response = '\n**TOP THREE RESTAURANTS**\n'
        for x, business in enumerate(sorted_wings_list[:3], start=1):
            if business['business_status'] != 'OPERATIONAL':
                continue
            response += f'```{x}.\n'
            response += f"NAME: {business['name']}\n"
            response += f"ADDRESS: {business['formatted_address']}\n"
            response += f"RATING: {business['rating']}\n"
            response += f"TOTAL RATINGS: {business['user_ratings_total']}```\n"

        await ctx.send(response)

    @commands.command(name='phone',
                      help='Get helpful phone numbers')
    async def phone(self, ctx, *search):
        url = f'https://www3.erie.gov/socialservices/most-frequently-requested-telephone-numbers'
        r = requests.get(url)
        base_df = pd.read_html(r.text)[0]
        if search:
            search = ' '.join(search)
            searched_df = base_df[base_df['SERVICE'].str.contains(search, case=False)]
        else:
            searched_df = base_df
        if search and searched_df.empty:
            return await ctx.send(f'Unable to find a helpful phone number containing `{search}`')
        df_list = np.split(searched_df, np.arange(10, len(searched_df), 5))
        formatter = MySource(df_list, search, per_page=1)
        menu = MyMenuPages(formatter)
        await menu.start(ctx)


def setup(bot):
    bot.add_cog(BufCommands(bot))
