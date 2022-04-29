import discord
from discord.ext import commands


class ModeratorCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_role('Admins')
    @commands.command(name='sync',
                      help='Syncs slash commands')
    async def sync(self, ctx):
        sync = await self.bot.tree.sync(guild=discord.Object(id=696068936034156624))
        print(sync)


def setup(bot):
    bot.add_cog(ModeratorCommands(bot))