import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from startup_cogs.buf_commands import weather_types, locations, required_times

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

command_prefix = 'buf '
intents = discord.Intents.all()


class Args:
    def __init__(self, name, required, choices):
        self.name = name
        self.required = required
        self.choices = choices


class MyHelp(commands.HelpCommand):
    args_dict = {'wx': [
                        {'name': 'weather type', 'required': False, 'choices': weather_types},
                        {'name': 'location', 'required': False, 'choices': locations}
                        ],
                 'forecast': [
                        {'name': 'time period', 'required': False, 'choices': required_times}
                        ]}

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Buffalo Bot Help')
        for cog, commands in mapping.items():
            value = ''
            cog_name = getattr(cog, "qualified_name", "No Category")
            filtered = await self.filter_commands(commands, sort=True)
            for command in filtered:
                value += f"`{command_prefix}{command} "
                if command.name in MyHelp.args_dict:
                    params = {}
                    for param in MyHelp.args_dict[command.name]:
                        params[param['name']] = Args(param['name'], param['required'], None)
                else:
                    params = command.clean_params
                for name, param in params.items():
                    if not param.required:
                        value += f"<{name}> "
                    else:
                        value += f"[{name}] "
                value += "`\n"
            embed.add_field(name=cog_name, value=value, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    # !help <command>
    async def send_command_help(self, command):
        embed = discord.Embed(title=f"{command_prefix}{command}")
        value = ''
        embed.add_field(name="Help", value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)
        if command.name in MyHelp.args_dict:
            params = {}
            for param in MyHelp.args_dict[command.name]:
                params[param['name']] = Args(param['name'], param['required'], param['choices'])
        else:
            params = command.clean_params
        if params:
            for name, param in params.items():
                value += f"**{name}** "
                if param.required:
                    value += f"*(required)*\n"
                else:
                    value += f"*(optional)*\n"
                if hasattr(param, 'choices'):
                    value += f"**choices:** `{'`, `'.join(x for x in param.choices)}`\n\n"
            embed.add_field(name="Arguments", value=value, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    # !help <group>
    async def send_group_help(self, group):
        pass

    # !help <cog>
    async def send_cog_help(self, cog):
        pass


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=MyHelp()
        )

    async def setup_hook(self):
        for filename in os.listdir('./startup_cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'startup_cogs.{filename[:-3]}')

    async def on_ready(self):
        print(self.user, "is ready.")


if __name__ == '__main__':
    bot = MyBot()
    bot.run(os.getenv('TOKEN'))

