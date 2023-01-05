from typing import Optional, Literal
import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
from helpers.role_select import RoleView, RegionMessage

class ModeratorCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="generate_region_select")
    @commands.guild_only()
    @commands.is_owner()
    async def generate_region_select(self, ctx: Context, *channel: commands.GuildChannelConverter):
        if not channel:
            channel = ctx.channel
        message = RegionMessage()
        view = await RoleView.construct_view(ctx)
        file, embed = generate_region_embed()
        await channel.send(embed=embed, view=view, file=file)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^", "-"]] = None) -> None:
        if not guilds:
            if spec == "~":
                # sync current guild
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                # copies all global app commands to current guild and syncs
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                # clears all commands from the current guild target and syncs (removes guild commands)
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            elif spec == "-":
                # clears global app commands and syncs globally
                ctx.bot.tree.clear_commands(guild=None)
                await ctx.bot.tree.sync()
                synced = []
            else:
                # Global sync
                synced = await ctx.bot.tree.sync()
            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot):
    await bot.add_cog(ModeratorCommands(bot))
