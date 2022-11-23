from datetime import datetime, timedelta
from discord.ext import commands
from env import config
import json


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
        check_for = int(config['DEKEMA_ID'])
        if message.author.id == check_for and \
                any(ele in message.content for ele in ['girl', 'woman', 'women', 'date', 'dating', 'girls']):
            tracker = load_json("startup_cogs/tracker.json")
            last_mentioned = datetime.fromisoformat(tracker["last_mentioned"])
            elapsed = message.created_at - last_mentioned
            days, hours, minutes, seconds = elapsed.days, elapsed.seconds // 3600, \
                                            elapsed.seconds // 60 % 60, elapsed.seconds % 60
            streak = tracker['streak']
            to_send = f"<@{check_for}> It has been {days} {more_than(days, 'day')} {hours} " \
                      f"{more_than(hours, 'hour')} {minutes} {more_than(minutes, 'minute')} and {seconds} " \
                      f"{more_than(seconds, 'second')} since you last talked about girls or dating.\n\n"
            if days > streak:
                to_send += f"You have beat your streak of {streak} days without talking about this stuff. Congrats, " \
                           f"but you have still mentioned it {tracker['mentioned']} times and need to refrain from " \
                           f"talking about it as you have been told numerous times to stop."
                tracker["streak"] = days
            else:
                to_send += f"You have now talked about this stuff {tracker['mentioned']} " \
                          f"times already. Please refrain from speaking about it further as you have been told " \
                          f"numerous times to stop."
            await message.channel.send(to_send)
            tracker["last_mentioned"] = str(message.created_at)
            tracker["mentioned"] += 1
            dump_json(tracker, "startup_cogs/tracker.json")

        if 'wegmans' in message.content.lower() and 'wegmans' in [word.lower() for word in message.content.split()]:
            await message.add_reaction("<:wegmans:698581136204496906>")
        if 'tops' in message.content.lower() and 'tops' in [word.lower() for word in message.content.split()]:
            await message.add_reaction("<:tops:698582304297058345>")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Listeners(bot))
