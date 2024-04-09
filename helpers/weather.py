import json
from typing import Literal

import requests

default_stations = {
    "KBUF": "Buffalo International Airport",
    "KDKK": "Dunkirk Airport",
    "KIAG": "Niagara Falls International Airport",
    "KJHW": "Chautauqua County/Jamestown Airport",
}
loc_station_map = {
    "Buffalo": "KBUF",
    "Niagara Falls": "KIAG",
    "Dunkirk": "KDKK",
    "Jamestown": "KJHW",
}
required_times = Literal[
    "Today",
    "This Morning",
    "This Afternoon",
    "Tonight",
    "Sunday",
    "Sunday Night",
    "Monday",
    "Monday Night",
    "Tuesday",
    "Tuesday Night",
    "Wednesday",
    "Wednesday Night",
    "Thursday",
    "Thursday Night",
    "Friday",
    "Friday Night",
    "Saturday",
    "Saturday Night",
]
locations = Literal["Buffalo", "Niagara Falls", "Dunkirk", "Jamestown"]
weather_types = Literal[
    "fog mist",
    "dust storm",
    "dust",
    "drizzle",
    "funnel cloud",
    "fog",
    "smoke",
    "hail",
    "snow pellets",
    "haze",
    "ice crystals",
    "ice pellets",
    "dust whirls",
    "spray",
    "rain",
    "sand",
    "snow grains",
    "snow",
    "squalls",
    "sand storm",
    "thunderstorms",
    "volcanic ash",
]
counties = Literal["Erie", "Niagara", "Allegany", "Cattaraugus", "Chautauqua"]


async def process_station(interaction, stations, location, weather=None):
    weather_dict = {}
    for station in stations:
        url = f"https://api.weather.gov/stations/{station}/observations/latest"
        w = requests.get(url)
        if not w.ok:
            return await interaction.response.send_message(
                "The NWS API doesn't want to talk to me right now. " "Try again later"
            )
        result = json.loads(w.content)["properties"]
        w.close()
        # If a location was entered
        if location:
            # If a weather type was entered
            return await process_with_loc(interaction, weather, result, station)
        # There is no location specified
        else:
            # If there weather specified, check each location for it (similar to early iteration of function)
            if weather:
                for present_weather in result["presentWeather"]:
                    if present_weather["weather"] == weather:
                        weather_dict[default_stations[station]] = present_weather[
                            "intensity"
                        ]
                # If there is no weather in the weather dict, explain that and return out
                if not weather_dict:
                    return await interaction.response.send_message(
                        f"There is no {weather} at any of the local observation stations"
                    )
            # No location and no weather specified. Store text descriptions for each location in weatherdict
            else:
                weather_dict[default_stations[station]] = result["textDescription"]
    reply = generate_reply(weather, weather_dict)
    return await interaction.response.send_message(reply)


async def process_with_loc(interaction, weather, result, station):
    if weather:
        # If there is no present weather return out
        if not result["presentWeather"]:
            return await interaction.response.send_message(
                f"There is currently no {weather} at {default_stations[station]}"
            )
        # Check for the weather type entered
        else:
            # Iterate through present weather list
            for present_weather in result["presentWeather"]:
                # If present weather matches entered weather construct reply, send, and return
                if present_weather == weather:
                    return await interaction.response.send_message(
                        "It sure is! Currently there is:\n"
                        f"{present_weather['intensity']} {weather} "
                        f"at the {default_stations[station]}"
                        if present_weather["intensity"]
                        else f"{weather} at the {default_stations[station]}"
                    )
            # This code will be reached if no match to weather is found
            return await interaction.response.send_message(
                f"There is currently no {weather} "
                f"at the {default_stations[station]}"
            )
    # There is a location entered, but no weather type
    else:
        # Send text description for location
        return await interaction.response.send_message(
            f"Currently it is `{result['textDescription']}` "
            f"at the {default_stations[station]}"
        )


def generate_reply(weather, weather_dict):
    if weather and weather_dict:
        reply = "It sure is! Currently there is:\n"
        for k, v in weather_dict.items():
            reply += f"`{v} {weather} at the {k}`\n" if v else f"{weather} at the {k}\n"
    else:
        reply = "Here are the current weather conditions:\n"
        for k, v in weather_dict.items():
            reply += f"`{v} at the {k}`\n"
    return reply
