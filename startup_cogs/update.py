from typing import Dict, List, Union, Optional, Sequence
import logging
import json
import os
import discord
from discord import app_commands
from discord.ext import commands

new_roles = [{"id": None, "name": "Buffalo", "colour": "#cdffff", "display_icon": 719580209799626812},
             {"id": None, "name": 'Nearby', "colour": "#eca145", "display_icon": 1051974816300798034}]
region_delete_roles = [{"id": 699933697704591442, "name": "Buffalo - Allentown"},
                       {"id": 699933874230132807, "name": "Buffalo - Elmwood Village"},
                       {"id": 699933919600181386, "name": "Buffalo - East Side"},
                       {"id": 700031315960922133, "name": "Buffalo - West Side"},
                       {"id": 699933976000725024, "name": "Buffalo - North Buffalo"},
                       {"id": 699934015146295357, "name": "Buffalo - Downtown"},
                       {"id": 699934072750866514, "name": "Buffalo - South Buffalo"}]
misc_delete_roles = [{"id": 719604297834299485, "name": "Local News"},
                     {"id": 719604247490068532, "name": "Local Politics"},
                     {"id": 719603969399324732, "name": "Professional Buffalo Sports"},
                     {"id": 719603900688236544, "name": "Local News and Politics"},
                     {"id": 719603773194109020, "name": "All Channels"}]
change_roles = [{"id": 699934182822117396, "name": "Niagara Falls", "new_name": "Niagara"},
                {"id": 699934215684489306, "name": "Expat", "new_name": "Just Visiting", "colour": "#eed8ff"}]
exclude_cats = [{"id": 696096508910633000, "name": "Admin"}, {"id": 1028441474255310960, "name": "Real Ones"},
                {"id": 1007627422667128932, "name": "Regulars"}, {"id": 696068936483209218, "name": "Voice Channels"},
                {"id": 1041712180141232148, "name": "contest"}, {"id": 1029388594147762198, "name": "admin"},
                {"id": 1037836509161717790, "name": "TOWNY MODS"},
                {"id": 1021399801222397984, "name": "Friends of WNY"},
                {"id": 1021399801222397985, "name": "USE YOUR WORDS"}]

logger = logging.getLogger(__name__)


class Updater(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def is_testing_guild():
        def predicate(ctx):
            return ctx.guild.id == ctx.bot.testing_guild_id

        return commands.check(predicate)

    @commands.command(name="update")
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        await ctx.message.delete()
        await self.backup_server(ctx)
        if ctx.guild.id == self.bot.testing_guild_id:
            await self.stage_testing_guild(ctx)
        else:
            await self.get_roles_in_role_set(ctx, region_delete_roles)

        # replace buffalo roles with new buffalo role
        await self.replace_buffalo_roles(ctx)

        # delete all roles
        await self.delete_all(ctx)

        # edit existing roles
        await self.edit_roles(ctx, change_roles)

        # reset all role permissions to false
        await self.reset_all_perms(ctx)

        # Create new categories
        # Will need all role objects to set perms

    @commands.command(name="stage")
    @commands.is_owner()
    @is_testing_guild()
    async def stage_testing_guild(self, ctx, *saves):
        await ctx.message.delete()
        role_sets = [region_delete_roles, change_roles, misc_delete_roles]
        for role_set in role_sets:
            await self.create_roles(ctx, role_set)
        await self.assign_random_del_roles(ctx)
        await self.copy_cat_and_channels(ctx)

    @commands.command(name="backup")
    @commands.is_owner()
    @is_testing_guild()
    async def backup_server(self, ctx: commands.Context):
        backup_mapping = {
            "members": ctx.guild.members,
            "roles": ctx.guild.roles,
            "cats": ctx.guild.categories,
            "channels": ctx.guild.channels
        }




    @commands.command(name="copy")
    @commands.is_owner()
    @is_testing_guild()
    async def copy_cat_and_channels(self, ctx: commands.Context):
        buf_cats: List[discord.CategoryChannel] = self.buffalo_guild.categories
        for buf_cat in buf_cats:
            if not any(exclude_cat['id'] == buf_cat.id for exclude_cat in exclude_cats):
                overwrites = await self.prepare_overwrites(ctx, buf_cat)
                new_category = await ctx.guild.create_category(
                    name=buf_cat.name,
                    overwrites=overwrites)
                for channel in buf_cat.channels:
                    overwrites = await self.prepare_overwrites(ctx, channel)
                    if channel.type.name == "text":
                        await ctx.guild.create_text_channel(name=channel.name,
                                                            category=new_category,
                                                            overwrites=overwrites)
                    if channel.type.name == "forum":
                        await ctx.guild.create_forum(name=channel.name,
                                                     category=new_category,
                                                     overwrites=overwrites)

    async def prepare_overwrites(self,
                                 ctx: commands.Context,
                                 buf_cat: discord.CategoryChannel):
        channel_overrides = {ctx.guild.default_role: buf_cat.overwrites_for(buf_cat.guild.default_role)}
        for role, overwrites in buf_cat.overwrites.items():
            ctx_role = await self.validate_exists(ctx, None, {"name": role.name})
            if ctx_role:
                channel_overrides[ctx_role] = overwrites
        return channel_overrides

    async def create_roles(self, ctx, role_set: List):
        for role in role_set:
            await self.create_single_role(ctx, role)

    async def create_single_role(self, ctx, role):
        raw_bytes = await self.get_raw_emoji(role)
        colour = role.get('colour')
        new_role = await ctx.guild.create_role(
            name=role.get("name"),
            colour=discord.Colour.from_str(colour) if colour else None,
            hoist=True,
            display_icon=raw_bytes if "ROLE_ICONS" in ctx.guild.features
            else None)
        logger.info(f"Role -{new_role.name}- created with id -{new_role.id}-")
        role["role"] = new_role
        role["id"] = new_role.id

    async def get_raw_emoji(self, role_set):
        emoji_id = role_set.get('display_icon')
        emoji = self.bot.get_emoji(emoji_id)
        raw_bytes = await emoji.read() if emoji else None
        return raw_bytes

    @commands.command(name="assign")
    @commands.is_owner()
    @is_testing_guild()
    async def assign_random_del_roles(self, ctx):
        all_members = ctx.guild.members
        for member in all_members:
            await self.pick_random_role_and_assign(ctx, member)

    async def pick_random_role_and_assign(self, ctx, member):
        import random
        role = random.choice(region_delete_roles + misc_delete_roles)
        delete_role = role.get('role')
        await self.validate_exists(ctx, delete_role, role)
        await member.add_roles(role['role'])

    async def validate_exists(self, ctx: commands.Context,
                              validate_role: Optional[Union[None, discord.Object]],
                              identifier: Dict):
        if not validate_role:
            validate_role = await self.get_by_id_or_name(ctx, identifier)
        return validate_role

    @staticmethod
    async def get_by_id_or_name(ctx, identifier: Dict):
        result = discord.utils.find(lambda r:
                                    r.id == identifier.get("id") or
                                    r.name == identifier.get("name"), ctx.guild.roles)
        return result

    async def check_replace_role(self, member):
        result = next((role for role in region_delete_roles if role["role"] in member.roles), None)
        if result:
            await self.replace_member_role(member)

    @staticmethod
    async def replace_member_role(member):
        buffalo_role = new_roles[0]["role"]
        await member.add_roles(buffalo_role)

    async def get_roles_in_role_set(self, ctx, role_set: List[Dict]):
        for role in role_set:
            await self.get_by_id_or_name(ctx, role)

    @commands.command(name="replace")
    @commands.is_owner()
    @is_testing_guild()
    async def replace_buffalo_roles(self, ctx):
        await self.create_roles(ctx, new_roles)
        await self.replace_old_roles(ctx, new_roles)

    async def replace_old_roles(self, ctx, role_set: List[Dict]):
        for role in role_set:
            await self.get_and_replace_role(ctx, role)

    async def get_and_replace_role(self, ctx, role):
        add_role = role.get("role", await self.validate_exists(ctx, None, role))
        if add_role:
            await self.get_members_and_replace_roles(ctx)

    async def get_members_and_replace_roles(self, ctx):
        all_members = ctx.guild.members
        for member in all_members:
            await self.check_replace_role(member)

    @commands.command(name="delete")
    @commands.is_owner()
    @is_testing_guild()
    async def delete_all(self, ctx, *discord_object_type):
        await ctx.message.delete()
        if discord_object_type == 'roles' or not discord_object_type:
            await self.delete_all_roles(ctx)
            print("Deleted all roles")
        if discord_object_type == 'cats' or not discord_object_type:
            await self.delete_all_cats(ctx)
            print("Deleted all categories")

    async def delete_all_cats(self, ctx):
        for cat in ctx.guild.categories:
            if not any(exclude_cat['id'] == cat.id for exclude_cat in exclude_cats):
                await cat.delete()

    async def delete_all_roles(self, ctx):
        role_sets = [region_delete_roles, misc_delete_roles]
        if ctx.guild.id == self.bot.testing_guild_id:
            role_sets += [new_roles, change_roles]
        for role_set in role_sets:
            await self.delete_roles(ctx, role_set)

    async def delete_roles(self, ctx, role_set: List[Dict]):
        await self.get_del_role_and_delete(ctx, role_set)

    async def get_del_role_and_delete(self, ctx, role_set):
        for role in role_set:
            await self.get_and_del_role(ctx, role)

    async def get_and_del_role(self, ctx, role):
        delete_role = role.get("role", await self.validate_exists(ctx, None, role))
        if delete_role:
            await self.delete_del_role(delete_role, role)

    @staticmethod
    async def delete_del_role(delete_role, role):
        await delete_role.delete()
        role.pop("role", None)

    async def edit_roles(self, ctx, role_set: List[Dict]):
        for role in role_set:
            await self.get_and_edit_role(ctx, role)

    async def get_and_edit_role(self, ctx, role):
        edit_role = role.get('role', await self.validate_exists(ctx, None, role))
        if edit_role:
            await edit_role.edit(name=role.get('new_name') if not None else role.get('name'))

    @commands.command(name="create")
    @commands.is_owner()
    @is_testing_guild()
    async def create(self, ctx, discord_object, *role_sets):
        if discord_object == "roles":
            if "new" in role_sets or not role_sets:
                await self.create_roles(ctx, new_roles)
            if "regions" in role_sets or not role_sets:
                await self.create_roles(ctx, region_delete_roles)
            if "change" in role_sets or not role_sets:
                await self.create_roles(ctx, change_roles)
            if "delete" in role_sets or not role_sets:
                await self.create_roles(ctx, misc_delete_roles)

    async def reset_all_perms(self, ctx: commands.Context):
        all_roles = ctx.guild.roles
        for role in all_roles:
            await self.clear_role_perms(role)

    @staticmethod
    async def clear_role_perms(role):
        if not role.permissions.administrator:
            await role.edit(permissions=discord.Permissions.none())


async def setup(bot):
    await bot.add_cog(Updater(bot))
