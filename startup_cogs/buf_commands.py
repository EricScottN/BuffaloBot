import discord
from discord.ext import commands
from discord import app_commands

from helpers.role_select import RoleView
from helpers.weather import (
    locations,
    get_location_observation,
    generate_forecast_week,
    generate_period_forecast,
)
from buffalobot import BuffaloBot


class BufCommands(commands.Cog, name="Buffalo Commands"):
    def __init__(self, bot: BuffaloBot) -> None:
        self.bot = bot

    wx = app_commands.Group(name="wx", description="Inquire about WNY weather")

    @wx.command(name="current")
    @app_commands.describe(
        location="A location with an observation station to search for"
    )
    async def current(
        self,
        interaction: discord.Interaction,
        location: locations,
    ):
        """
        Get live conditions from an official NWS observation station in WNY
        """
        return await interaction.response.send_message(
            await get_location_observation(self.bot.web_client, location)
        )

    @wx.command(name="forecast")
    @app_commands.describe(when="Time period")
    async def forecast(self, interaction: discord.Interaction, when: str = None):
        """Get a quick summary of the next weeks forecast or pass a time period argument to retrieve a more
        detailed forecast of that time period"""
        url = "https://api.weather.gov/gridpoints/BUF/78,43/forecast"
        async with self.bot.web_client.get(url) as response:
            if response.status != 200:
                return await interaction.response.send_message(
                    "The NWS API doesn't want to talk to me right now. "
                    "Try again later"
                )
            periods = (await response.json())["properties"]["periods"]
        if not when:
            return await interaction.response.send_message(
                await generate_forecast_week(periods)
            )
        return await interaction.response.send_message(
            await generate_period_forecast(periods, when)
        )

    municipality = app_commands.Group(
        name="municipality",
        description="Select your municipality role. "
        "This will grant you access to the server",
    )

    @municipality.command(name="select")
    async def select_municipality(self, interaction: discord.Interaction):
        view = RoleView.create_with_ctx(interaction)
        await interaction.response.send_message(
            embed=view.embed, file=view.file, view=view, ephemeral=True
        )


async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(BufCommands(bot))
