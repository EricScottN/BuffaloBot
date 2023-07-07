import random
import discord
from discord.ext import commands
from string import punctuation
import json

WORD_EMOJI_MAP = {"tops": "<:tops:698582304297058345>",
                  "wegmans": "<:wegmans:698581136204496906>",
                  "bills": "<:bills:698581414949552229>"}

def load_json(json_file):
    try:
        with open(json_file) as jf:
            result_dict = json.load(jf)
            return result_dict
    except Exception as e:
        print(e)


def dump_json(updated_json, json_file):
    with open(json_file, 'w') as jf:
        json.dump(updated_json, jf, indent=4)


def more_than(time, time_string):
    return time_string + 's' if time != 1 else time_string


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        check_for = self.bot.bot_vars['JIVE_ID']
        if message.author.id == check_for:
            random_number = random.randint(1, 5)
            if random_number == 5:
                await message.add_reaction("<:really:1108941725881352263>")
        # VERIFY CHANGE

    async def check_for_words(self, message):
        for check_word in WORD_EMOJI_MAP.keys():
            if check_word in message.content.lower() and \
                    check_word in [word.lower() for word in message.content.strip(punctuation).split()]:
                reaction = WORD_EMOJI_MAP[check_word]
                await message.add_reaction(reaction)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
