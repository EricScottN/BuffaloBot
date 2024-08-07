from typing import Optional, Literal
import logging
import discord
from discord.ext import commands
from discord.ext.commands import Context, Greedy
from discord import app_commands
from helpers.role_select import RoleView
from helpers.utils import generate_welcome_embed
from db.utils import refresh_db

logger = logging.getLogger(__name__)


class ModeratorCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    mod_group = app_commands.Group(
        name="mod", description="Moderator slash commands"
    )

    mod_db_group = app_commands.Group(
        name="db",
        description="Database related commands for moderators",
        parent=mod_group
    )

    @mod_db_group.command(name="refresh")
    @app_commands.checks.has_any_role(
        1246992974097940621,
        1240344954757447690
    )
    async def refresh(
            self,
            interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(
                ephemeral=True, thinking=False
            )
            await refresh_db(self.bot)
            return await interaction.followup.send(
                "Database successfully refreshed",
                ephemeral=True
            )
        except BaseException as e:
            logger.error("Error refreshing database: %s", e)
            return await interaction.followup.send(
                "Error refreshing database",
                ephemeral=True
            )

    @commands.command(name="generate_region_select")
    @commands.guild_only()
    @commands.is_owner()
    async def generate_region_select(
            self, ctx: Context, *channel: commands.GuildChannelConverter
    ):
        if not channel:
            channel = ctx.channel
        message = RoleView.create_with_ctx(ctx)
        await channel.send(embed=message.embed, view=message, file=message.file)

    @commands.command(name="generate_welcome_embed")
    @commands.guild_only()
    @commands.is_owner()
    async def generate_welcome_embed(
            self, ctx: Context, *channel: commands.GuildChannelConverter
    ):
        if not channel:
            channel = ctx.channel
        await generate_welcome_embed(ctx, channel)

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
            self,
            ctx: Context,
            guilds: Greedy[discord.Object],
            spec: Optional[Literal["~", "*", "^", "-"]] = None,
    ) -> None:
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
