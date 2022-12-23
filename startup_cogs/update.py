from typing import Dict, List
import logging
import discord
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
    async def update(self, ctx):
        print("updating")
        if ctx.guild.id == self.bot.testing_guild_id:
            await self.stage_testing_guild(ctx)
        else:
            await self.get_roles_in_role_set(ctx, region_delete_roles)

        # replace buffalo roles with new buffalo role
        await self.replace_buffalo_roles(ctx)

        # delete all roles
        await self.delete_all_roles(ctx)

        # reset all role permissions to false
        await self.reset_all_perms(ctx)

        # edit existing roles
        await self.edit_roles(ctx)

    @commands.command(name="stage")
    @commands.is_owner()
    @is_testing_guild()
    async def stage_testing_guild(self, ctx):
        for role_set in [region_delete_roles, change_roles, misc_delete_roles]:
            await self.create_roles(ctx, role_set)
        await self.assign_random_del_roles(ctx)

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

    async def create_roles(self, ctx, role_set: List):
        for role in role_set:
            await self.create_single_role(ctx, role)

    async def create_single_role(self, ctx, role):
        raw_bytes = await self.get_raw_emoji(role)
        colour = role.get('colour')
        new_role = await ctx.guild.create_role(name=role.get("name"),
                                               colour=discord.Colour.from_str(colour) if colour else None,
                                               hoist=True,
                                               display_icon=raw_bytes if "ROLE_ICONS" in ctx.guild.features
                                               else None)
        logger.info(f"Role -{new_role.name}- created with id -{new_role.id}-")
        role["role"] = new_role
        role["id"] = new_role.id

    @commands.command(name="replace")
    @commands.is_owner()
    @is_testing_guild()
    async def replace_buffalo_roles(self, ctx):
        await self.create_roles(ctx, new_roles)
        await self.replace_old_roles(ctx, new_roles)

    @commands.command(name="delete")
    @commands.is_owner()
    @is_testing_guild()
    async def delete_all_roles(self, ctx):
        role_sets = [region_delete_roles, misc_delete_roles]
        if ctx.guild.id == self.bot.testing_guild_id:
            role_sets += [new_roles, change_roles]
        for role_set in role_sets:
            await self.delete_roles(ctx, role_set)

    @staticmethod
    async def reset_all_perms(ctx: commands.Context):
        all_roles = ctx.guild.roles
        for role in all_roles:
            if not role.permissions.administrator:
                await role.edit(permissions=discord.Permissions.none())

    @staticmethod
    async def edit_roles(*roles):
        for role in change_roles:
            edit_role = role.get('role')
            if not edit_role:
                edit_role = ctx.guild.get_role(role['id'])
            no_perms = discord.Permissions.none()
            await edit_role.edit(name=role.get('new_name') if not None else role.get('name'))

    async def delete_roles(self, ctx, role_set: List[Dict]):
        for role in role_set:
            delete_role = role.get("role", await self.validate_role_exists(ctx, None, role))
            if delete_role:
                await delete_role.delete()
                role.pop("role", None)

    async def replace_old_roles(self, ctx, role_set: List[Dict]):
        for role in role_set:

            add_role = role.get("role", self.validate_role_exists(ctx, None, role))
            if add_role:
                all_members = ctx.guild.members
                for member in all_members:
                    result = next((role for role in region_delete_roles if role["role"] in member.roles), None)
                    if result:
                        await member.add_roles(new_roles[0]["role"])

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
        await self.validate_role_exists(ctx, delete_role, role)
        await member.add_roles(role['role'])

    async def validate_role_exists(self, ctx, delete_role, role):
        if not delete_role:
            delete_role = await self.get_role_by_id_or_name(ctx, role)
        return delete_role

    async def get_roles_in_role_set(self, ctx, role_set: List[Dict]):
        for role in role_set:
            await self.get_role_by_id_or_name(ctx, role)

    @staticmethod
    async def get_role_by_id_or_name(ctx, role):
        result = discord.utils.find(lambda r: r.id == role["id"] or r.name == role["name"], ctx.guild.roles)
        return result

    async def get_raw_emoji(self, role_set):
        emoji_id = role_set.get('display_icon')
        emoji = self.bot.get_emoji(emoji_id)
        raw_bytes = await emoji.read() if emoji else None
        return raw_bytes


async def setup(bot):
    await bot.add_cog(Updater(bot))
