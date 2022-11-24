import discord
from discord import app_commands
from discord.ext.commands import Context, Greedy
from discord.ext import commands


class Updater(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stage")
    @commands.is_owner()
    async def stage(self, ctx):
        pass
        if ctx.guild.id == self.bot.bot_vars["FOWNY_ID"]:
            buffalo_guild = self.bot.get_guild(self.bot.bot_vars["BUFFALO_ID"])
            categories = buffalo_guild.by_category()
            for category in categories:
                if category[0]
                pass
                # if category[0].name in []

    @commands.command(name="update")
    @commands.is_owner()
    async def update(self, ctx):
        guild = ctx.guild
        if guild == self.bot.bot_vars['FOWNY_ID']:
            # add categories

            # add channels
            new_channels = []
            for k, v in update['remove']['channels']:
                new_channels.append(await guild.create_text_channel(name=k))
        pass

async def setup(bot):
    await bot.add_cog(Updater(bot))
