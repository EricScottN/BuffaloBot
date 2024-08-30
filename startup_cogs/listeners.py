import random
import discord
from discord.ext import commands
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.check_for_words(message)
        await self.check_real(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.check_real(after)

    @staticmethod
    def is_real():
        async def predicate(ctx: commands.Context):
            return ctx.author.id == 1180987464077299772
        return commands.check(predicate)

    @is_real()
    async def check_real(self, message: discord.Message):
        if "real" in message.content.lower():
            rdm = random.random()
            if rdm > 0.30:
                return
            await message.delete(delay=random.randint(1, 5))

    async def check_for_words(self, message: discord.Message):
        for check_word in WORD_EMOJI_MAP.keys():
            if check_word in message.content.lower() and check_word in [
                word.lower() for word in message.content.strip(punctuation).split()
            ]:
                reaction = WORD_EMOJI_MAP[check_word]
                await message.add_reaction(reaction)


async def setup(bot: BuffaloBot) -> None:
    await bot.add_cog(Listeners(bot))
