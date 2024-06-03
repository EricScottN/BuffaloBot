import time
import datetime
import logging
import asyncio
from discord import Embed, Color
from discord.ext import tasks, commands

from buffalobot import BuffaloBot
from db.utils import refresh_db

logger = logging.getLogger(__name__)

utc = datetime.timezone.utc
refresh_db_time = datetime.time(hour=0, minute=0, tzinfo=utc)


class BuffaloLoops(commands.Cog):
    def __init__(self, bot: BuffaloBot):
        self.bot = bot
        self.sent_alerts = []
        self.loops = [self.get_wx_alerts, self.refresh_db]
        self.get_wx_alerts.start()
        self.refresh_db.start()

    async def cog_unload(self) -> None:
        """
        Discord.py method for unloading Cog
        """
        self.refresh_db.stop()
        self.get_wx_alerts.stop()

    @tasks.loop(time=refresh_db_time)
    async def refresh_db(self):
        """
        Discord.py task to refresh database on init and every 24 hours
        """
        await self.bot.wait_until_ready()
        await refresh_db(self.bot)

    @tasks.loop(seconds=5)
    async def get_wx_alerts(self):
        await self.bot.wait_until_ready()
        url = 'https://api.weather.gov/alerts/active/zone/NYC029'
        async with self.bot.web_client.get(url) as response:
            if response.status != 200:
                logger.warning(f"Bad Status Thrown: {response.status}")
                await asyncio.sleep(60)
                return
            features = (await response.json())["features"]
        if not features:
            return
        color_map = {
            "Extreme": Color.red(),
            "Severe": Color.yellow()
        }
        for feature in features:
            properties = feature["properties"]
            if (
                    properties["id"] in self.sent_alerts
                    or properties["severity"] not in ["Severe", "Extreme"]
                    or properties["status"] != "Actual"
            ):
                continue
            logger.info("Alert Found")
            logger.info(f"Alert ID: {properties['id']}")
            logger.info(f"Severity: {properties['severity']}")
            logger.info(f"Headline: {properties['headline']}")
            logger.info(f"Description: {properties['description']}")
            color = color_map.get(properties["severity"])
            if not color:
                color = Color.default()
            embed = Embed(
                title=properties["headline"],
                description=properties["description"],
                color=color,
            )
            embed.set_footer(text=properties["id"])
            # TODO - Create channel directory table add weather-alerts to it so it's not testing guild
            guild = self.bot.get_guild(1021399801222397983)
            channel = guild.get_channel(1242909661213098005)
            await channel.send(embed=embed)
            self.sent_alerts.append(properties["id"])


async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(BuffaloLoops(bot))
