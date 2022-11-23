import os
import logging
import discord
import env
from discord.ext import commands

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

intents = discord.Intents.all()


class MyBot(commands.Bot):
    def __init__(self):
        self.bot_vars = env.config
        super().__init__(
            command_prefix=commands.when_mentioned_or(),
            intents=intents,
        )

    async def setup_hook(self):
        for filename in os.listdir('./startup_cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'startup_cogs.{filename[:-3]}')

    async def on_ready(self):
        print(self.user, "is ready.")


if __name__ == '__main__':
    bot = MyBot()
    try:
        bot.run(bot.bot_vars['TOKEN'], log_handler=handler, log_level=logging.DEBUG)
    except Exception as e:
        print(e)

