import discord
from discord.ext import commands, tasks
from string import punctuation
import json

from buffalobot import BuffaloBot

WORD_EMOJI_MAP = {
    "tops": "<:tops:698582304297058345>",
    "wegmans": "<:wegmans:698581136204496906>",
    "bills": "<:bills:698581414949552229>",
}


def load_json(json_file):
    try:
        with open(json_file) as jf:
            result_dict = json.load(jf)
            return result_dict
    except Exception as e:
        print(e)


def dump_json(updated_json, json_file):
    with open(json_file, "w") as jf:
        json.dump(updated_json, jf, indent=4)


def more_than(time, time_string):
    return time_string + "s" if time != 1 else time_string


class Listeners(commands.Cog):
    def __init__(self, bot: BuffaloBot):
        self.bot = bot
        self.sent_alerts = []
        self.get_wx_alerts.start()

    @tasks.loop(seconds=5)
    async def get_wx_alerts(self):
        await self.bot.wait_until_ready()
        url = 'https://api.weather.gov/alerts/active/zone/NYC029'
        async with self.bot.web_client.get(url) as response:
            if response.status != 200:
                return
            features = (await response.json())["features"]
        if not features:
            return
        for feature in features:
            properties = feature["properties"]
            if properties["id"] in self.sent_alerts or properties["severity"] not in ["Severe", "Extreme"]:
                continue

            embed = discord.Embed(
                title=properties["headline"],
                description=properties["description"],
                color=discord.Color.dark_red(),

            )
            embed.set_footer(text=properties["id"])
            guild = self.bot.get_guild(1021399801222397983)
            channel = guild.get_channel(1242909661213098005)
            await channel.send(embed=embed)
            self.sent_alerts.append(properties["id"])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.check_for_words(message)

    async def check_for_words(self, message: discord.Message):
        for check_word in WORD_EMOJI_MAP.keys():
            if check_word in message.content.lower() and check_word in [
                word.lower() for word in message.content.strip(punctuation).split()
            ]:
                reaction = WORD_EMOJI_MAP[check_word]
                await message.add_reaction(reaction)


async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(Listeners(bot))
