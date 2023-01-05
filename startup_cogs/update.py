import asyncio
from typing import Dict, List, Union, Optional, Any
import logging
import json
import discord
from discord.ext import commands

permissions = {
    "regions": discord.Permissions(
        create_instant_invite=True, send_messages=True, send_messages_in_threads=True, add_reactions=True,
        use_external_emojis=True, read_message_history=True, request_to_speak=True, use_voice_activation=True,
        speak=True, connect=True, use_application_commands=True),
    "elevated": discord.Permissions(
        create_instant_invite=True, send_messages=True, send_messages_in_threads=True, add_reactions=True,
        use_external_emojis=True, read_message_history=True, request_to_speak=True, use_voice_activation=True,
        speak=True, connect=True, use_application_commands=True, attach_files=True, change_nickname=True,
        create_private_threads=True, create_public_threads=True, embed_links=True, manage_events=True,
        manage_threads=True, stream=True, use_embedded_activities=True),
    "mods": discord.Permissions(
        create_instant_invite=True, send_messages=True, send_messages_in_threads=True, add_reactions=True,
        use_external_emojis=True, read_message_history=True, request_to_speak=True, use_voice_activation=True,
        speak=True, connect=True, use_application_commands=True, attach_files=True, change_nickname=True,
        create_private_threads=True, create_public_threads=True, embed_links=True, manage_events=True,
        manage_threads=True, kick_members=True, ban_members=True, view_audit_log=True, manage_messages=True,
        manage_emojis_and_stickers=True, moderate_members=True, mention_everyone=True, mute_members=True,
        deafen_members=True, priority_speaker=True, stream=True, use_embedded_activities=True)
}

update = {
    "create": {
        "roles": [
            {"id": None, "name": "Amherst", "colour": "#ff8861", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": 'Aurora', "colour": "#c097d8", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": "Buffalo", "colour": "#002174", "display_icon": 719580209799626812, "hoist": True},
            {"id": None, "name": "Cheektowaga", "colour": "#80c551", "display_icon": "🎲", "hoist": True},
            {"id": None, "name": "Clarence", "colour": "#bebd65", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": "Eden", "colour": "#51c596", "display_icon": "❄", "hoist": True},
            {"id": None, "name": "Evans", "colour": "#9651c5", "display_icon": "❄", "hoist": True},
            {"id": None, "name": "Grand Island", "colour": "#ed7e7e", "display_icon": "🏝️", "hoist": True},
            {"id": None, "name": "Hamburg", "colour": "#4da4d0", "display_icon": "❄", "hoist": True},
            {"id": None, "name": "Lackawanna", "colour": "#afd897", "display_icon": "⚒", "hoist": True},
            {"id": None, "name": "Lancaster", "colour": "#edb57e", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": "Orchard Park", "colour": "#a4d1e7", "display_icon": "❄", "hoist": True},
            {"id": None, "name": "Tonawanda", "colour": "#d0794d", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": "West Seneca", "colour": "#527e34", "display_icon": "🦬", "hoist": True},
            {"id": None, "name": "Nearby", "colour": None, "hoist": True},
            {"id": None, "name": "North Tonawanda", "colour": "#edec7e", "display_icon": "💦", "hoist": True},
            {"id": None, "name": "Lockport", "colour": "#edec7e", "display_icon": "💦", "hoist": True}
        ],
        "categories": [
            {"id": None, "name": "🦬| Buffalo"},
            {"id": None, "name": "Getting Started"},
            {"id": None, "name": "Informational"},
            {"id": None, "name": "Interests and Hobbies"},
            {"id": None, "name": "Archive"}
        ],
        "channels": [
            {"id": None, "name": "🎤-suggestions", "category": "Informational", "type": "forum"},
            {"id": None, "name": "💵-buy-sell-jobs", "category": "🦬| Buffalo", "type": "forum"},
            {"id": None, "name": "🧻-politics", "category": "Interests and Hobbies", "type": "forum"}
        ]
    },
    "edit": {
        "roles": [
            {"id": 699934182822117396, "name": "Niagara Falls", "permissions": permissions['regions'],
             "colour": "#edec7e", "display_icon": "💦"},
            {"id": 699934215684489306, "name": "Expat", "new_name": "Just Visiting", "colour": discord.Colour.default(),
             "permissions": permissions['regions']},
            {"id": 699934108314501150, "name": "Northtowns", "permissions": permissions['regions'],
             "color": discord.Colour.default()},
            {"id": 699934144817528843, "name": "Southtowns", "permissions": permissions['regions'],
             "color": discord.Colour.default()},
            {"id": 696073200987013241, "name": "Admins", "permissions": permissions['mods']},
            {"id": 696078290619990026, "name": "Mods", "permissions": permissions['mods']},
            {"id": 699649445024759899, "name": "Server Booster", "permissions": permissions['elevated']},
            {"id": 1028440757117386892, "name": "Real Ones", "permissions": permissions['elevated']},
            {"id": 978421055297314856, "name": "VIP - Rochester Discord Admin", "permissions": permissions['elevated']},
            {"id": 1007626715918503987, "name": "Regulars", "permissions": permissions['elevated']},
            {"id": 1039255296775815328, "name": "Rochesterian VIP", "permissions": permissions['elevated']},
            {"id": 1029377303920255037, "name": "FoWny", "permissions": permissions['elevated']}
        ],
        "categories": [
            {"id": 1029388594147762198, "name": "Admin", "overwrites": [1021403746326036592]},
            {"id": 1037836509161717790, "name": "TOWNY MODS", "overwrites": [
                1021403746326036592, 1029376856945868810]},
            {"id": 1021399801222397984, "name": "Friends of WNY", "overwrites": [
                1021403746326036592, 1029376856945868810, 1039255296775815328, 1029377303920255037]},
            {"id": 1058585359551836212, "name": "Admin", "overwrites": [
                696073200987013241, 717539403752407061]},
            {"id": 696096508910633000, "name": "Mods", "overwrites": [
                696073200987013241, 696078290619990026, 717539403752407061]},
            {"id": 1028441474255310960, "name": "Real Ones", "overwrites": [
                696073200987013241, 696078290619990026, 1028440757117386892, 717539403752407061]},
            {"id": 1007627422667128932, "name": "Regulars", "overwrites": [
                696073200987013241, 696078290619990026, 1028440757117386892, 1007626715918503987, 717539403752407061]},
        ],
        "channels": [
            {"id": 696171963240022068, "name": "📝-welcome-rules", "category": "Getting Started"},
            {"id": 696075954363301898, "name": "📯-announcements", "category": "Informational"},
            {"id": 699928543798493226, "name": "🦬-set-your-roles-first", "new_name": "get-started", "category": None},
            {"id": 729031489244626954, "name": "introductions", "new_name": "👋-bflo-intros", "category": "🦬| Buffalo"},
            {"id": 696452671598493696, "name": "🎫-things-to-do", "new_name": "🎫-bflo-fun", "category": "🦬| Buffalo"},
            {"id": 696452764427092081, "name": "❓-help-desk", "category": "Informational"},
            {"id": 696071995984707684, "name": "💬-general", "category": "🦬| Buffalo"},
            {"id": 696924737242136689, "name": "🎤-suggestions", "category": "Archive"},
            {"id": 696094626284568788, "name": "💵-buy-sell-jobs", "category": "Archive"},
            {"id": 719626310841925663, "name": "channel-select", "new_name": "🪪-bflo-roles", "category": "🦬| Buffalo"},
            {"id": 969344166922448936, "name": "🤖-bot-spam", "category": "Archive"},
            {"id": 1020542502761136148, "name": "📺-news", "new_name": "📺-bflo-news", "category": "🦬| Buffalo"},
            {"id": 696206515211599912, "name": "🧻-politics", "category": "Archive"},
            {"id": 696081453183926283, "name": "🏒-sabres", "category": "Archive"},
            {"id": 696081227421057105, "name": "🏈-bills", "new_name": "🏈🏒-bflo-sports", "category": "🦬| Buffalo"},
            {"id": 696098329410404413, "name": "🍴food-and-dining", "new_name": "🍴🍺-bflo-food-and-drink",
             "category": "🦬| Buffalo"},
            {"id": 696207813948473394, "name": "🎮-gaming", "category": "Interests and Hobbies"},
            {"id": 696101473515339927, "name": "🐶-buffalo-pets", "new_name": "🐶-bflo-pets", "category": "🦬| Buffalo"},
            {"id": 698249578595614800, "name": "🎨🏎-hobbies", "category": "Archive"},
            {"id": 698705467500920892, "name": "🎧-music-theater-arts", "new_name": "🎧🍿📚-entertainment",
             "category": "Interests and Hobbies"},
            {"id": 698659695577137262, "name": "🖥-tech", "category": "Interests and Hobbies"},
            {"id": 1021958475401658429, "name": "🌱-lawn-and-garden", "new_name": "🌱-lawn-garden-diy",
             "category": "Interests and Hobbies"},
            {"id": 700111188100644934, "name": "🙉-memes", "category": "Interests and Hobbies"},
            {"id": 960855040413802596, "name": "🤷-off-topic", "category": "Archive"},
            {"id": 702544939300683796, "name": "🍿-movies-and-tv", "category": "Archive"},
            {"id": 718347467476697169, "name": "📷-pics", "new_name": "📷-bflo-pics", "category": "🦬| Buffalo"},
            {"id": 1034491595262799992, "name": "📚-books", "category": "Archive"},
            {"id": 697659404497190943, "name": "🚣🏾-sports", "category": "Archive"},
            {"id": 1060316382039920670, "name": "🍺-alcoholic-beverages", "category": "Archive"}
        ]
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
            {"id": 719672353814085663, "name": "Buffalo Professional Sports"},
            {"id": 696077861295226920, "name": "Topics"},
            {"id": 720245201834344568, "name": "Getting Started"}
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
            {"id": 1058585359551836212, "name": "Admin"},
            {"id": 696096508910633000, "name": "Admin"},
            {"id": 1028441474255310960, "name": "Real Ones"},
            {"id": 1007627422667128932, "name": "Regulars"},
            {"id": 696068936483209218, "name": "Voice Channels"},
            {"id": 1041712180141232148, "name": "contest"}
        ]
    },
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

    @commands.command(name="test_delete")
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

    @commands.command(name="delete")
    @commands.is_owner()
    async def delete(self, ctx, *delete_elements):
        if "categories" in delete_elements:
            for category in update["delete"]["categories"]:
                delete_cat = await self.get_by_id_or_name(ctx, category, "category")
                if delete_cat:
                    await delete_cat.delete()
        if "roles" in delete_elements:
            for role in update["delete"]["roles"]:
                delete_role = await self.get_by_id_or_name(ctx, role, "role")

    @commands.command(name="stage")
    @commands.is_owner()
    @is_testing_guild()
    async def stage_testing_guild(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        buffalo_guild: discord.Guild = self.bot.get_guild(self.bot.bot_vars["BUFFALO_ID"])

        roles = await self.copy_roles_from_server(buffalo_guild, update["exclude_copy_from_buf_server"]['roles'])
        await self.create_roles(ctx, roles)
        logger.info("==============================")
        logger.info("ALL ROLES CREATED SUCCESSFULLY")
        logger.info("==============================")

        categories = await self.copy_categories_from_server(ctx, buffalo_guild,
                                                            update["exclude_copy_from_buf_server"]["categories"])
        await self.create_categories(ctx, categories)
        logger.info("===================================")
        logger.info("ALL CATEGORIES CREATED SUCCESSFULLY")
        logger.info("===================================")

        channels = await self.copy_channels_from_server(ctx, categories)
        await self.create_channels(channels, ctx)
        logger.info("=================================")
        logger.info("ALL CHANNELS CREATED SUCCESSFULLY")
        logger.info("=================================")

        await self.assign_random_del_roles(ctx, region_delete_roles)
        logger.info("=================================")
        logger.info("======DELETE ROLES ASSIGNED======")
        logger.info("=================================")

    @commands.command(name="replace")
    @commands.is_owner()
    async def replace_buffalo_roles(self, ctx: commands.Context):
        replace_role = await self.get_by_id_or_name(ctx, update['create']['roles'][2], "role")
        if not replace_role:
            logger.warning(f"Cannot find replace role -{replace_role}- in {ctx.guild.name}.")
            return
        region_replace_roles = [region_delete_role["name"] for region_delete_role in region_delete_roles]
        members = ctx.guild.members
        for member in members:
            member_roles = member.roles
            member_role_names = [role.name for role in member_roles]
            role = set(member_role_names).intersection(region_replace_roles)
            if not role:
                continue
            if not replace_role:
                continue
            await member.add_roles(replace_role)

    @commands.command(name="create")
    @commands.is_owner()
    async def create(self, ctx, *element_type):
        if "roles" in element_type:
            await self.create_roles(ctx, update["create"]["roles"])
        if "categories" in element_type:
            await self.create_categories(ctx, update["create"]["categories"])
        if "channels" in element_type:
            await self.create_channels(update["create"]["channels"], ctx)

    @commands.command(name="edit")
    @commands.is_owner()
    async def edit(self, ctx, *element_type):
        if "roles" in element_type:
            await self.edit_roles(ctx)
        if "categories" in element_type:
            await self.edit_categories(ctx)
        if "channels" in element_type:
            await self.edit_channels(ctx)

    async def edit_channels(self, ctx):
        for channel in update["edit"]["channels"]:
            edit_channel: discord.abc.GuildChannel = discord.utils.find(
                lambda c: c.id == channel.get("id") or
                          c.name == channel.get("name") or
                          c.name == channel.get("new_name"), ctx.guild.channels)
            if not edit_channel:
                logger.info(f"Unable to find channel {channel['name']}.. skipping")
                continue
            if edit_channel.name == "🦬-set-your-roles-first":
                overwrites = {}
                for role in update["edit"]["roles"] + update["create"]["roles"]:
                    overwrite_role = await self.get_by_id_or_name(ctx, role, "role")
                    if overwrite_role:
                        overwrites.update({overwrite_role: discord.PermissionOverwrite(read_messages=False)})
                overwrites.update({ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True,
                                                                                       read_message_history=True)})
                # need to create embed here for new region roles and set permissions
            new_name = channel.get("new_name", edit_channel.name)
            new_category = discord.utils.find(lambda c: c.name == channel.get("category"), ctx.guild.categories)
            if edit_channel.category == new_category \
                    and edit_channel.name == new_name \
                    and (edit_channel.permissions_synced or not edit_channel.category):
                logger.info(f"Channel {edit_channel.name} has already been edited. Skipping..")
                continue
            try:
                logger.info(f"Attempting to edit {edit_channel.name}")
                logger.info(f"Old name - {edit_channel.name} -> {new_name}")
                logger.info(f"Moving to category -> {new_category}")
                new_channel = await edit_channel.edit(name=new_name, category=new_category, sync_permissions=True)
                logger.info(f"Successfully edited {new_channel.name} | Category - {new_channel.category}")
            except Exception as e:
                logger.warning(f"Unable to edit channel -  {e}")
            await asyncio.sleep(2)

    async def edit_categories(self, ctx):
        for category in ctx.guild.categories:
            for overwrite_set in update["edit"]["categories"]:
                if overwrite_set["id"] == category.id:
                    overwrites_list = overwrite_set["overwrites"]
                    break
            else:
                overwrites_list = [
                    1021403746326036592, 1029376856945868810, 1039255296775815328, 1029377303920255037,
                    696073200987013241, 696078290619990026, 1028440757117386892, 1007626715918503987,
                    717539403752407061
                ]
            overwrites = {}
            for overwrite in overwrites_list:
                role = ctx.guild.get_role(overwrite)
                if not role:
                    continue
                overwrites.update({role: discord.PermissionOverwrite(view_channel=True)})
            mute_role = discord.utils.find(lambda c: c.name == "Mute", ctx.guild.roles)
            if mute_role:
                overwrites.update(
                    {mute_role: discord.PermissionOverwrite(
                        add_reactions=False, change_nickname=False, use_application_commands=False,
                        manage_events=False, manage_threads=False, create_public_threads=False,
                        create_private_threads=False, send_messages_in_threads=False,
                        use_embedded_activities=False, connect=False, send_messages=False, ban_members=False,
                        kick_members=False)})
            if category.overwrites == overwrites:
                logger.info(f"Category overwrites for {category.name} already set correctly. Skipping..")
                continue
            await category.edit(overwrites=overwrites)
            await asyncio.sleep(2)

    async def edit_roles(self, ctx: commands.Context):
        lowest_role = float('inf')
        for role in update['edit']['roles']:
            edit_role = await self.get_by_id_or_name(ctx, role, "role")
            if not edit_role:
                logger.warning(f"Unable to find {role['name']} to edit - Does it exist or has it been deleted?")
                continue
            if edit_role:
                name = role.get("new_name", edit_role.name)
                colour = discord.Colour.from_str(role.get('colour')) if role.get('colour') else edit_role.color
                perms = role.get("permissions", None)
                try:
                    await edit_role.edit(name=name,
                                         colour=colour,
                                         permissions=perms)
                    await asyncio.sleep(2)
                    lowest_role = edit_role.position if edit_role.position < lowest_role else lowest_role
                except Exception as e:
                    print(e)
        lowest_role -= 1
        for role in ctx.guild.roles:
            if role.name in [ctx_role["name"] for ctx_role in update['create']['roles']]:
                await role.edit(position=lowest_role if lowest_role >= 1 else 0)
                lowest_role -= 1

    @commands.command(name="clear")
    @commands.is_owner()
    async def clear(self, ctx, *clear_elements):
        if "categories" in clear_elements:
            for cat in ctx.guild.categories:
                logger.info(f"Removing overwrites from category {cat.name}..")
                if cat.overwrites:
                    await cat.edit(overwrites={})
                logger.info(f"Overwrites removed from category {cat.name}. Sleeping for a couple seconds")
                await asyncio.sleep(2)
                for channel in cat.channels:
                    logger.info(f"Removing overwrites from channel {channel.name}..")
                    if cat.overwrites:
                        await channel.edit(overwrites={})
                    logger.info(f"Overwrites removed from channel {channel.name}. Sleeping for a couple seconds")
        if "roles" in clear_elements:
            for role in ctx.guild.roles:
                if role.is_bot_managed():
                    logger.info(f"Role -{role.name} is bot-managed. Skipping")
                    continue
                await self.clear_role_perms(role)

    async def copy_roles_from_server(self, copy_guild: discord.Guild, exclude_roles):
        roles = copy_guild.roles
        not_excluded_roles = [{"name": role.name,
                               "hoist": role.hoist,
                               "display_icon": role.display_icon,
                               "colour": str(role.colour),
                               "permissions": discord.Permissions.none()}
                              for role in roles
                              if not role.is_bot_managed() and role.id not in
                              [exclude_role['id'] for exclude_role in exclude_roles]]
        return not_excluded_roles

    async def copy_categories_from_server(self, ctx, copy_cats: discord.Guild, exclude_cats):
        cats = copy_cats.categories
        not_excluded_cats = [{"name": cat.name,
                              "overwrites": await self.copy_overwrites_from_buf_server(ctx, cat),
                              "channels": cat.channels}
                             for cat in cats if cat.id not in [
                                 exclude_cat['id'] for exclude_cat in exclude_cats]]
        return not_excluded_cats

    async def copy_channels_from_server(self, ctx, copy_cats):
        channel_set = []
        for cat in copy_cats:
            channels = cat["channels"]
            for channel in channels:
                channel_set.append(
                    {
                        "name": channel.name,
                        "type": channel.type.name,
                        "category": {"name": cat["name"]},
                        "overwrites": await self.copy_overwrites_from_buf_server(ctx, channel)
                    }
                )
        return channel_set

    async def create_categories(self, ctx: commands.Context, categories: List[Dict[str, Any]]):
        """Creates categories from a list of dictionaries with attributes"""
        for category in categories:
            # Check for name - move to the next as category can't be created without a name
            name = category.get('name')
            if not name:
                logger.warning(f"Could not find a category name in category set - {category}")
                continue

            # Check to make sure the category doesn't exist in ctx server.
            new_category = discord.utils.find(lambda c: c.name == name, ctx.guild.categories)
            if not new_category:
                # If it doesn't exist, create it.
                try:
                    overwrites = await self.get_overwrites(name, ctx)
                    await ctx.guild.create_category(name=name, overwrites=overwrites)
                except Exception as e:
                    print(e)
                await asyncio.sleep(2)
                logger.info(f"Created category - {name} -- creating channels")
            else:
                logger.info(f"Found category {name} already in {ctx.guild.name} - skipping creation "
                            f"and checking for channels")

    async def get_overwrites(self, name, ctx):
        """Returns the permission overwrites for a category"""
        overwrites = {}
        if name == "Archive":
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    create_private_threads=False,
                    create_public_threads=False,
                )
            }
        else:
            for role in update["create"]["roles"] + update["edit"]["roles"][0:4]:
                find_role = await self.get_by_id_or_name(ctx, role, "role")
                if find_role:
                    overwrites.update({find_role: discord.PermissionOverwrite(view_channel=True)})
        return overwrites

    async def create_channels(self, channels: List[Dict[str, Any]], ctx):
        mapping = {
            "text": ctx.guild.create_text_channel,
            "forum": ctx.guild.create_forum,
            "news": ctx.guild.create_text_channel,
        }
        for channel in channels:
            create_channel = await self.get_by_id_or_name(ctx, channel, "channel")
            if create_channel:
                logger.info(f"Channel - {channel['name']} - found - skipping creation")
                continue
            func = mapping.get(channel['type'])
            if func:
                try:
                    category = await self.get_by_id_or_name(ctx, channel['category'], "category")
                    await func(name=channel["name"],
                               category=category if category else None)
                except Exception as e:
                    logger.warning(f"Cannot create {channel['type']} channel {channel['name']}: {e}")

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
            perms = role.get("permissions", permissions['regions'])
            new_role = await ctx.guild.create_role(
                name=name,
                colour=colour,
                hoist=hoist,
                display_icon=raw_bytes,
                permissions=perms)
            logger.info(f"Role -{new_role.name}- created with id -{new_role.id}-\nSleeping for a couple seconds so I"
                        f" don't get rate limited")
            await asyncio.sleep(2)

    async def assign_random_del_roles(self, ctx, delete_roles):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass

        all_members = ctx.guild.members
        delete_roles = [delete_role["name"] for delete_role in delete_roles]
        for member in all_members:
            if member.bot:
                continue
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
        assign_role = await self.get_by_id_or_name(ctx, role, "role")
        if assign_role:
            await member.add_roles(assign_role)

    async def copy_overwrites_from_buf_server(self,
                                              ctx: commands.Context,
                                              buf_cat: discord.CategoryChannel):
        channel_overrides = {ctx.guild.default_role: buf_cat.overwrites_for(buf_cat.guild.default_role)}
        for role, overwrites in buf_cat.overwrites.items():
            ctx_role = await self.validate_exists(ctx, None, {"name": role.name})
            if ctx_role:
                channel_overrides[ctx_role] = overwrites
        return channel_overrides

    async def validate_exists(self, ctx: commands.Context,
                              validate_role: Optional[Union[None, discord.Object]],
                              identifier: Dict):
        if not validate_role:
            validate_role = await self.get_by_id_or_name(ctx, identifier, 'role')
        return validate_role

    @staticmethod
    async def get_by_id_or_name(ctx, identifier: Dict, element_type) -> Union[discord.Role | discord.abc.GuildChannel]:
        element_map = {
            "role": ctx.guild.roles,
            "channel": ctx.guild.channels,
            "category": ctx.guild.categories
        }
        result = discord.utils.find(lambda r:
                                    r.id == identifier.get("id") or
                                    r.name == identifier.get("name"), element_map[element_type])
        return result

    @staticmethod
    async def clear_role_perms(role):
        if not role.permissions:
            logger.info(f"{role.name} already has no permissions. Skipping..")
            return
        logger.info(f"Removing permissions from role {role.name}..")
        await role.edit(permissions=discord.Permissions.none())
        logger.info(f"Removed permissions from role {role.name}. Sleeping for a couple seconds")
        await asyncio.sleep(2)


async def setup(bot):
    await bot.add_cog(Updater(bot))
