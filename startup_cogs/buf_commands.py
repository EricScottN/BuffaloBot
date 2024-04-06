import requests
import json
import calendar
from datetime import date
import discord
from discord.ext import commands
from discord import app_commands

from helpers.role_select import RoleView
from helpers.weather import default_stations, loc_station_map, required_times, locations, weather_types, process_station

class BufCommands(commands.Cog, name='Buffalo Commands'):
    def __init__(self, bot) -> None:
        self.bot = bot

    wx = app_commands.Group(name="wx", description="Inquire about WNY weather")

    @wx.command(name="current")
    @app_commands.describe(condition='A weather condition to search the area for')
    @app_commands.describe(location='A location with an observation station to search for')
    async def current(self, interaction: discord.Interaction, condition: weather_types = None,
                      location: locations = None):
        """ Get current weather conditions """
        if location:
            stations = [loc_station_map[location]]
        else:
            stations = default_stations
        return await process_station(interaction, stations, location, condition)

    @wx.command(name="forecast")
    @app_commands.describe(when='Time period')
    async def forecast(self, interaction: discord.Interaction, when: required_times = None):
        """ Get a quick summary of the next weeks forecast or pass a time period argument to retrieve a more
        detailed forecast of that time period """
        url = 'https://api.weather.gov/gridpoints/BUF/78,43/forecast'
        w = requests.get(url)
        if not w.ok:
            return await interaction.response.send_message("The NWS API doesn't want to talk to me right now. "
                                                           "Try again later")
        result = json.loads(w.content)['properties']
        periods = result['periods']
        w.close()
        forecast = ''
        if when:
            forecast_type = 'detailedForecast'
            if when.lower() == 'today' or calendar.day_name[date.today().weekday()].lower() in when.lower():
                when_list = ['Today', 'This Morning', 'This Afternoon', 'Tonight']
            else:
                when_list = [when]
            for period in periods:
                if period['name'].lower() in [x.lower() for x in when_list]:
                    forecast += f"`{period['name']}: {period[forecast_type]}`\n"
            return await interaction.response.send_message(f'Here is a detailed forecast for `{when}`:\n'
                                                           f'{forecast}')
        else:
            forecast_type = 'shortForecast'
            for period in periods:
                forecast += f"`{period['name']}: {period[forecast_type]}`\n"
            return await interaction.response.send_message(f'Here is a summary forecast for this week:\n'
                                                           f'{forecast}')

    municipality = app_commands.Group(name="municipality",
                                      description="Select your municipality role. "
                                                  "This will grant you access to the server")

    @municipality.command(name="select")
    async def select_municipality(self, interaction: discord.Interaction):
        view = RoleView.create_with_ctx(interaction)
        await interaction.response.send_message(embed=view.embed, file=view.file, view=view, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BufCommands(bot))

