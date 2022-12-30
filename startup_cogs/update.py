import asyncio
from typing import Dict, List, Union, Optional, Any
import logging
import json
import discord
from discord.ext import commands

update = {
    "create": {
        "roles": [
            {"id": None, "name": "Buffalo", "colour": "#cdffff", "display_icon": 719580209799626812},
            {"id": None, "name": 'Nearby', "colour": "#eca145", "display_icon": 1051974816300798034}
        ],
        "categories": [
            {"id": None, "name": "🦬| Buffalo"},
            {"id": None, "name": "Archive"}
        ],
        "channels": [
            {"id": None, "name": "#🎲dice-board-gaming"}
        ]
    },
    "edit": {
        "roles": [],
        "categories": [],
        "channels": []
    },
    "delete": {
        "roles": [
            {"id": 744659197366501416, "name": "VIP\u2014Food Editor, Buffalo News"},
            {"id": 719604297834299485, "name": "Local News"},
            {"id": 719604247490068532, "name": "Local Politics"},
            {"id": 719603969399324732, "name": "Professional Buffalo Sports"},
            {"id": 719603900688236544, "name": "Local News and Politics"},
            {"id": 719603773194109020, "name": "All Channels"},
            {"id": 699934072750866514, "name": "Buffalo - South Buffalo"},
            {"id": 699934015146295357, "name": "Buffalo - Downtown"},
            {"id": 699933976000725024, "name": "Buffalo - North Buffalo"},
            {"id": 700031315960922133, "name": "Buffalo - West Side"},
            {"id": 699933919600181386, "name": "Buffalo - East Side"},
            {"id": 699933874230132807, "name": "Buffalo - Elmwood Village"},
            {"id": 699933697704591442, "name": "Buffalo - Allentown"},
            {"id": 965332115627585547, "name": "Buf Photo Club"}
        ],
        "categories": [
            {"id": 696068936483209217, "name": "Visiting Buffalo"},
            {"id": 719675429614518354, "name": "General"},
            {"id": 719628984735760445, "name": "News and Politics"},
            {"id": 719672353814085663, "name": "Buffalo Professional Sports"}
        ]
    },
    # exclude_copy will contain things from Buffalo server that shouldn't be copied to test server.
    "exclude_copy_from_buf_server": {
        "roles": [
            {"id": 696073200987013241, "name": "Admins"},
            {"id": 696085627971567766, "name": "Bots"},
            {"id": 696078290619990026, "name": "Mods"},
            {"id": 699649445024759899, "name": "Server Booster"},
            {"id": 1028440757117386892, "name": "Real Ones"},
            {"id": 978421055297314856, "name": "VIP - Rochester Discord Admin"},
            {"id": 1007626715918503987, "name": "Regulars"},
            {"id": 696068936034156624, "name": "@everyone"},
            {"id": 1012774854115725412, "name": "He/Him"},
            {"id": 1012774853624995881, "name": "She/Her"},
            {"id": 1012774853058768946, "name": "They/Them"},
            {"id": 1012774852429627423, "name": "Pronouns: Ask Me"},
            {"id": 1012774851695616080, "name": "Any Pronouns"}
        ],
        "categories": [
            {"id": 696096508910633000, "name": "Admin"},
            {"id": 1028441474255310960, "name": "Real Ones"},
            {"id": 1007627422667128932, "name": "Regulars"},
            {"id": 696068936483209218, "name": "Voice Channels"},
            {"id": 1041712180141232148, "name": "contest"}
        ]
    },
    # Channels to archive
    "archive": [
        {"id": 719626310841925663, "name": "channel-select"},
        {"id": 969344166922448936, "name": "\ud83e\udd16-bot-spam"},
        {"id": 719630341375262790, "name": "\ud83d\udcfa-news"},
        {"id": 696081453183926283, "name": "\ud83c\udfd2-sabres"},
        {"id": 698249578595614800, "name": "\ud83c\udfa8\ud83c\udfce-hobbies"},
        {"id": 1034491595262799992, "name": "\ud83d\udcda-books"}
    ]
}


region_delete_roles = [{"id": 699933697704591442, "name": "Buffalo - Allentown"},
                       {"id": 699933874230132807, "name": "Buffalo - Elmwood Village"},
                       {"id": 699933919600181386, "name": "Buffalo - East Side"},
                       {"id": 700031315960922133, "name": "Buffalo - West Side"},
                       {"id": 699933976000725024, "name": "Buffalo - North Buffalo"},
                       {"id": 699934015146295357, "name": "Buffalo - Downtown"},
                       {"id": 699934072750866514, "name": "Buffalo - South Buffalo"}]

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

    @commands.command(name="save")
    @commands.is_owner()
    @is_testing_guild()
    async def save(self, ctx: commands.Context):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        info = {}
        for server_name, server in {"buffalo": self.bot.get_guild(self.bot.bot_vars["BUFFALO_ID"]),
                                    "fowny": ctx.guild}.items():
            info[server_name] = {"roles": [], "categories": []}
            info[server_name]["roles"] = [
                {"id": role.id,
                 "name": role.name}
                for role in server.roles
            ]
            info[server_name]["categories"] = [
                {"id": category.id,
                 "name": category.name,
                 "channels": [
                     {"id": channel.id,
                      "name": channel.name}
                     for channel in category.channels
                 ]}
                for category in server.categories]
        with open("servers_info.json", "w") as json_file:
            json.dump(info, json_file, indent=1)

    @commands.command(name="update")
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        await ctx.message.delete()
        if ctx.guild.id == self.bot.testing_guild_id:
            await self.stage_testing_guild(ctx)

        # replace buffalo roles with new buffalo role
        await self.replace_buffalo_roles(ctx)

        # reset all role permissions to false
        await self.reset_all_perms(ctx)

    @commands.command(name="stage")
    @commands.is_owner()
    @is_testing_guild()
    async def stage_testing_guild(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        buffalo_guild: discord.Guild = self.bot.get_guild(self.bot.bot_vars["BUFFALO_ID"])
        buffalo_roles = buffalo_guild.roles
        not_excluded_roles = [{"name": role.name,
                               "hoist": role.hoist,
                               "display_icon": role.display_icon,
                               "colour": str(role.colour)}
                              for role in buffalo_roles
                              if not role.is_bot_managed() and role.id not in
                              [exclude_role['id'] for exclude_role in update["exclude_copy_from_buf_server"]['roles']]]
        await self.create_roles(ctx, not_excluded_roles)
        logger.info("==============================")
        logger.info("ALL ROLES CREATED SUCCESSFULLY")
        logger.info("==============================")

        buffalo_categories = buffalo_guild.categories
        not_excluded_categories = [category for category in buffalo_categories
                                   if category.id not in
                                   [exclude_category["id"] for exclude_category
                                    in update["exclude_copy_from_buf_server"]['categories']]]
        await self.create_categories(ctx, not_excluded_categories)
        logger.info("===================================")
        logger.info("ALL CATEGORIES CREATED SUCCESSFULLY")
        logger.info("===================================")
        await self.assign_random_del_roles(ctx)

    async def create_categories(self, ctx, categories: List[discord.CategoryChannel]):
        for category in categories:
            new_category = discord.utils.find(lambda c: c.name == category.name, ctx.guild.categories)
            if not new_category:
                overwrites = await self.prepare_overwrites(ctx, category)
                new_category = await ctx.guild.create_category(name=category.name, overwrites=overwrites)
                logger.info(f"Created category - {category.name} -- creating channels")
                await asyncio.sleep(2)
            else:
                logger.info(f"Category - {category.name} - found - skipping creation")
            channels = category.channels
            logger.info(f"Checking channels..")
            await self.create_channels(channels, ctx, new_category)
            logger.info("=================================")
            logger.info("ALL CHANNELS CREATED SUCCESSFULLY")
            logger.info("=================================")

    async def create_channels(self, channels: List[discord.CategoryChannel], ctx, new_category):
        mapping = {
            "text": ctx.guild.create_text_channel,
            "forum": ctx.guild.create_forum,
            "news": ctx.guild.create_text_channel,
        }
        for channel in channels:
            if discord.utils.find(lambda c: c.name == channel.name, ctx.guild.channels):
                logger.info(f"Channel - {channel.name} - found - skipping creation")
                continue
            overwrites = await self.prepare_overwrites(ctx, channel)
            func = mapping.get(channel.type.name)
            if func:
                try:
                    await func(name=channel.name,
                               category=new_category,
                               overwrites=overwrites)
                except Exception as e:
                    logger.warning(f"Cannot create {channel.type.name} channel {channel.name}: {e}")

    async def create_roles(self, ctx, roles: List[Dict[str, Any]]):
        for role in roles:
            name = role.get('name')
            if not name:
                logger.warning(f"Could not find a role name in role set - {role}")
                continue
            if discord.utils.find(lambda c: c.name == name, ctx.guild.roles):
                logger.info(f"Found role {name} already in {ctx.guild.name} - skipping creation")
                continue
            colour = discord.Colour.from_str(role.get('colour')) if role.get('colour') else None
            raw_bytes = await self.bot.get_emoji(role.get("display_icon")).read() \
                if role.get("display_icon") and "ROLE_ICONS" in ctx.guild.features else None
            hoist = role.get('hoist', False)
            new_role = await ctx.guild.create_role(
                name=name,
                colour=colour,
                hoist=hoist,
                display_icon=raw_bytes)
            logger.info(f"Role -{new_role.name}- created with id -{new_role.id}-\nSleeping for a couple seconds so I"
                        f"don't get rate limited")
            await asyncio.sleep(2)

    async def prepare_overwrites(self,
                                 ctx: commands.Context,
                                 buf_cat: discord.CategoryChannel):
        channel_overrides = {ctx.guild.default_role: buf_cat.overwrites_for(buf_cat.guild.default_role)}
        for role, overwrites in buf_cat.overwrites.items():
            ctx_role = await self.validate_exists(ctx, None, {"name": role.name})
            if ctx_role:
                channel_overrides[ctx_role] = overwrites
        return channel_overrides

    @commands.command(name="assign")
    @commands.is_owner()
    @is_testing_guild()
    async def assign_random_del_roles(self, ctx, delete_roles):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass

        all_members = ctx.guild.members
        delete_roles = [delete_role["name"] for delete_role in update["delete"]["roles"]]
        for member in all_members:
            member_roles = member.roles
            member_role_names = [role.name for role in member_roles]
            role = set(member_role_names).intersection(delete_roles)
            if role:
                logger.info(f"Member {member.name} has delete role {role} - skipping")
                continue
            await self.pick_random_role_and_assign(ctx, member)

    async def pick_random_role_and_assign(self, ctx, member: discord.Member):
        import random
        role = random.choice(update["delete"]["roles"])
        assign_role = discord.utils.find(lambda r: r.name == role["name"], ctx.guild.roles)
        if assign_role:
            await member.add_roles(assign_role)

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

    async def get_roles_in_role_set(self, ctx, role_set: List[Dict]):
        for role in role_set:
            await self.get_by_id_or_name(ctx, role)

    @commands.command(name="replace")
    @commands.is_owner()
    @is_testing_guild()
    async def replace_buffalo_roles(self, ctx):
        await self.create_roles(ctx, update["create"]["roles"])

    async def new_replace_roles(self, ctx: commands.Context):
        members = ctx.guild.members
        region_replace_roles = [region_delete_role["name"] for region_delete_role in region_delete_roles]

        for member in members:
            member_roles = member.roles
            member_role_names = [role.name for role in member_roles]
            role = set(member_role_names).intersection(region_delete_roles)
            if role:
                pass



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
    async def delete_from_test(self, ctx: commands.Context):
        with open("servers_info.json", "r") as read_file:
            fowny_info = json.load(read_file)["fowny"]

        delete_roles = [role for role in ctx.guild.roles
                        if not role.is_bot_managed() and role.id not in
                        [delete_role['id'] for delete_role in fowny_info['roles']]]
        for role in delete_roles:
            await role.delete()
            await asyncio.sleep(2)
            logger.info(f"Deleted role: {role.name}")

        delete_cats = [cat for cat in ctx.guild.categories
                       if cat.id not in [delete_cat['id']
                                         for delete_cat in fowny_info['categories']]]
        for cat in delete_cats:
            channels = cat.channels
            for channel in channels:
                await channel.delete()
                await asyncio.sleep(2)
                logger.info(f"Deleted channel: {channel.name}")
            await cat.delete()
            await asyncio.sleep(2)

            logger.info(f"Deleted category: {cat.name}")

        await self.save(ctx)

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
