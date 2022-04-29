import os
import requests
import json
import googlemaps
from typing import Literal
import calendar
from datetime import date
import discord
from discord.ext import commands
from discord import app_commands

key = os.getenv("MAPS_API")


default_stations = {"KBUF": "Buffalo International Airport",
                    "KDKK": "Dunkirk Airport",
                    "KIAG": "Niagara Falls International Airport",
                    "KJHW": "Chautauqua County/Jamestown Airport"}
loc_station_map = {'Buffalo': 'KBUF',
                   'Niagara Falls': 'KIAG',
                   'Dunkirk': 'KDKK',
                   'Jamestown': 'KJHW'}

required_times = Literal['Today', 'This Morning', 'This Afternoon', 'Tonight', 'Sunday', 'Sunday Night', 'Monday',
                         'Monday Night', 'Tuesday', 'Tuesday Night', 'Wednesday', 'Wednesday Night', 'Thursday',
                         'Thursday Night', 'Friday', 'Friday Night', 'Saturday', 'Saturday Night']
locations = Literal['Buffalo', 'Niagara Falls', 'Dunkirk', 'Jamestown']
weather_types = Literal['fog mist', 'dust storm', 'dust', 'drizzle', 'funnel cloud', 'fog', 'smoke', 'hail',
                 'snow pellets', 'haze', 'ice crystals', 'ice pellets', 'dust whirls', 'spray', 'rain', 'sand',
                 'snow grains', 'snow', 'squalls', 'sand storm', 'thunderstorms', 'volcanic ash']


async def process_station(interaction, stations, location, weather=None):
    weather_dict = {}
    for station in stations:
        url = f"https://api.weather.gov/stations/{station}/observations/latest"
        w = requests.get(url)
        if not w.ok:
            return await interaction.response.send_message("The NWS API doesn't want to talk to me right now. "
                                                           "Try again later")
        result = json.loads(w.content)['properties']
        w.close()
        # If a location was entered
        if location:
            # If a weather type was entered
            return await process_with_loc(interaction, weather, result, station)
        # There is no location specified
        else:
            # If there weather specified, check each location for it (similar to early iteration of function)
            if weather:
                for present_weather in result['presentWeather']:
                    if present_weather['weather'] == weather:
                        weather_dict[default_stations[station]] = present_weather['intensity']
                # If there is no weather in the weather dict, explain that and return out
                if not weather_dict:
                    return await interaction.response.send_message(f"There is no {weather} at any of the local observation stations")
            # No location and no weather specified. Store text descriptions for each location in weatherdict
            else:
                weather_dict[default_stations[station]] = result['textDescription']
    reply = generate_reply(weather, weather_dict)
    return await interaction.response.send_message(reply)


async def process_with_loc(interaction, weather, result, station):
    if weather:
        # If there is no present weather return out
        if not result['presentWeather']:
            return await interaction.response.send_message(f'There is currently no {weather} at {default_stations[station]}')
        # Check for the weather type entered
        else:
            # Iterate through present weather list
            for present_weather in result['presentWeather']:
                # If present weather matches entered weather construct reply, send, and return
                if present_weather == weather:
                    return await interaction.response.send_message('It sure is! Currently there is:\n'
                                          f"{present_weather['intensity']} {weather} "
                                          f"at the {default_stations[station]}"
                                          if present_weather['intensity']
                                          else f"{weather} at the {default_stations[station]}")
            # This code will be reached if no match to weather is found
            return await interaction.response.send_message(f"There is currently no {weather} "
                                  f"at the {default_stations[station]}")
    # There is a location entered, but no weather type
    else:
        # Send text description for location
        return await interaction.response.send_message(f"Currently it is `{result['textDescription']}` "
                                                       f"at the {default_stations[station]}")


def generate_reply(weather, weather_dict):
    if weather and weather_dict:
        reply = 'It sure is! Currently there is:\n'
        for k, v in weather_dict.items():
            reply += f'`{v} {weather} at the {k}`\n' if v else f'{weather} at the {k}\n'
    else:
        reply = 'Here are the current weather conditions:\n'
        for k, v in weather_dict.items():
            reply += f'`{v} at the {k}`\n'
    return reply


class BufCommands(commands.Cog, name='Buffalo Commands'):
    def __init__(self, bot) -> None:
        self.bot = bot

    wx = app_commands.Group(name="wx", description="Inquire about WNY weather", guild_ids=[696068936034156624])

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

    @commands.command(name='wings',
                      help='Get best wing locations for your area. Just pass your city or town! If no location is '
                           'passed, will return results for Buffalo')
    async def wings(self, ctx, location=None):
        try:
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
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(BufCommands(bot))
