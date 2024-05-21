from typing import Literal, Dict, List

import aiohttp

loc_station_map = {
    "Buffalo": "KBUF",
    "Niagara Falls": "KIAG",
    "Dunkirk": "KDKK",
    "Jamestown": "KJHW",
}

locations = Literal["Buffalo", "Niagara Falls", "Dunkirk", "Jamestown"]


async def get_location_observation(
    web_client: aiohttp.ClientSession, location: str
) -> str:
    station = loc_station_map.get(location)
    if not station:
        return f"Unable to find {location} in station mapping. Please report to Admin"
    url = f"https://api.weather.gov/stations/{station}/observations/latest"
    async with web_client.get(url) as response:
        if response.status != 200:
            return (
                "The NWS API doesn't want to talk to me right now. " "Try again later"
            )
        observation_result = (await response.json())["properties"]
    temperature = await get_observation_temp(observation_result)
    url = f"https://api.weather.gov/stations/{station}"
    async with web_client.get(url) as response:
        if response.status != 200:
            return (
                "The NWS API doesn't want to talk to me right now. " "Try again later"
            )
        station_result = (await response.json())["properties"]
    result = f"Currently it is `{temperature} degrees`"
    result += (
        f" and `{observation_result['textDescription']}` "
        if observation_result["textDescription"]
        else ""
    )
    result += f" at the `{station_result['name']}`"
    return result


async def get_observation_temp(observation_result: Dict):
    fahrenheit = (
        round(32 + 9 / 5 * observation_result["temperature"]["value"])
        if observation_result["temperature"]["unitCode"] == "wmoUnit:degC"
        else observation_result["temperature"]["value"]
    )
    return fahrenheit


async def generate_forecast_week(periods: List) -> str:
    forecast_str = "\n".join(
        [f"`{period['name']}: {period['shortForecast']}`" for period in periods]
    )
    return (
        f"Here is a summary forecast for this week:\n\n{forecast_str}\n\n"
        f"For a more detailed forecast, pass a time period to `when`. "
        f"For example: \n`/wx forecast when: Friday`"
    )


async def generate_period_forecast(periods: List, when: str) -> str:
    times = []
    result = None
    for period in periods:
        if when.lower() != period["name"].lower():
            times.append(period["name"])
            continue
        result = period["detailedForecast"]
        break
    if not result:
        return (
            f"Could not find `{when}` in time periods. Try one of the following:\n"
            f"```\n{', '.join([f'{time}' for time in times])}```\n"
            f".. or leave empty for a summary forecast for this week"
        )
    return f"Here is a detailed forecast for `{when}`:\n\n" f"`{result}`"
