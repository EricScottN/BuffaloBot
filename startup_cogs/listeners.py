from datetime import datetime
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
    async def on_message(self, message):
        check_for = self.bot.bot_vars['DEKEMA_ID']
        if message.author.id == check_for and \
                any(ele in message.content for ele in ['girl', 'woman', 'women', 'date', 'dating', 'girls']):
            tracker = load_json("files/tracker.json")
            last_mentioned = datetime.fromisoformat(tracker["last_mentioned"])
            elapsed = message.created_at - last_mentioned
            days, hours, minutes, seconds = elapsed.days, elapsed.seconds // 3600, \
                                            elapsed.seconds // 60 % 60, elapsed.seconds % 60
            streak = tracker['streak']
            if days > streak:
                tracker["streak"] = days
            await message.channel.send(f"It's been {days} {more_than(days, 'day')}")
            tracker["last_mentioned"] = str(message.created_at)
            tracker["mentioned"] += 1
            dump_json(tracker, "files/tracker.json")

        await self.check_for_words(message)

    async def check_for_words(self, message):
        for check_word in WORD_EMOJI_MAP.keys():
            if check_word in message.content.lower() and \
                    check_word in [word.lower() for word in message.content.strip(punctuation).split()]:
                reaction = WORD_EMOJI_MAP[check_word]
                await message.add_reaction(reaction)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
