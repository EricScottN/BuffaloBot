import logging
import asyncio
from typing import Tuple, Dict, Union, Optional, List, Any

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


async def create_channel_embed(ctx: commands.Context) -> discord.Embed:
    logger.info(f"Creating channel directoy embed..")
    embed = discord.Embed(
        title="Channel Directory"
    )
    for category in ctx.guild.categories:
        if category.id in [cat["id"] for cat in update["edit"]["categories"]] or category.name != "Archive":
            continue
        value = ""
        for channel in category.channels:
            topic = channel.topic if channel.type.name != 'voice' else "voice channel"
            value += f"{channel.mention} - {topic}\n"
        embed.add_field(name=category.name,
                        value=value,
                        inline=False)
    return embed


async def sync_channel_permissions(ctx: commands.Context) -> None:
    for channel in ctx.guild.channels:
        logger.info(f"Checking if channel {channel.name} permissions are synced..")
        if not channel.permissions_synced:
            await channel.edit(sync_permissions=True)
            await asyncio.sleep(5)

async def edit_channels(ctx: commands.Context) -> None:
    for channel in update["edit"]["channels"]:
        edit_channel: discord.abc.GuildChannel = discord.utils.find(
            lambda c: c.id == channel.get("id") or
                      c.name == channel.get("name") or
                      c.name == channel.get("new_name"), ctx.guild.channels)
        if not edit_channel:
            logger.info(f"Unable to find channel {channel['name']}.. skipping")
            continue

        new_name = channel.get("new_name", edit_channel.name)
        new_category = discord.utils.find(lambda c: c.name == channel.get("category"), ctx.guild.categories)
        new_topic = channel.get("topic", edit_channel.topic)
        if edit_channel.category == new_category \
                and edit_channel.name == new_name \
                and (edit_channel.permissions_synced or not edit_channel.category):
            logger.info(f"Channel {edit_channel.name} has already been edited. Skipping..")
            continue
        try:
            logger.info(f"Attempting to edit {edit_channel.name}")
            logger.info(f"Old name - {edit_channel.name} -> {new_name}")
            logger.info(f"Moving to category -> {new_category}")
            new_channel = await edit_channel.edit(name=new_name, category=new_category, topic=new_topic,
                                                  sync_permissions=True)
            await asyncio.sleep(5)
            logger.info(f"Successfully edited {new_channel.name} | Category - {new_channel.category}")
        except Exception as e:
            logger.warning(f"Unable to edit channel -  {e}")
        await asyncio.sleep(5)


async def create_rules_embed() -> discord.Embed:
    logger.info(f"Generating rules embed..")
    embed = discord.Embed(
        title="Rules",
        description="1️⃣ Be respectful of others' opinions and ideas. No Personal Attacks.\n"
                    "2️⃣ No NSFW or NSFL material.\n"
                    "3️⃣ No racism, sexism, etc. This includes promoting racial supremacy, nazism, "
                    "terrorism or other hateful ideas.\n "
                    "4️⃣ No spamming. Repeated postings of the same/similar content in a time frame that "
                    "prevents other members from engaging with the server. "
                    "Rehashing topics, especially when asked to stop, is considered spam\n"
                    "5️⃣ No soliciting or scams.\n"
                    "6️⃣ No doxxing. This includes posting identifying personal images or non-public "
                    "information of people without consent.\n "
                    "7️⃣ No threats of any kind, or advocating for the death or injury of others.\n "
                    "8️⃣ No alt accounts.\n "
                    "9️⃣ No low effort/shit-posting. Contributing nothing of value towards conversation "
                    "and/or derailing discussions to get a reaction is a violating this rule.\n "
                    "🔟 Do not send repeated unsolicited DMs or friend requests to any member(s) of this "
                    "server.\n ")
    return embed


async def create_welcome_embed() -> Tuple[discord.Embed, discord.File]:
    logger.info("Generating welcome embed..")
    embed = discord.Embed(
        title="WELCOME TO THE BUFFALO DISCORD SERVER!",
        description="Our mission statement is simple: Connect locals and transplants in the City of Good "
                    "Neighbors together, both in real life and on the server, and provide help and "
                    "resources members need to live a fulfilling life in Buffalo and around WNY!"
    )
    file = discord.File("files/Flag_of_Buffalo,_New_York.png")
    embed.set_image(url="attachment://Flag_of_Buffalo,_New_York.png")

    return embed, file


async def create_staff_embed(ctx: commands.Context) -> discord.Embed:
    logger.info(f"Creating staff embed..")
    embed = discord.Embed(
        title="Staff Members"
    )
    mod_roles = [ctx.guild.get_role(696073200987013241), ctx.guild.get_role(696078290619990026),
                 ctx.guild.get_role(1021403746326036592), ctx.guild.get_role(1029376856945868810)]
    for role in mod_roles:
        if not role:
            continue
        value = ""
        for member in role.members:
            value += f"{member.mention}\n"
        embed.add_field(name=role.name,
                        value=value,
                        inline=False)
    return embed


async def create_send_roleview(ctx: commands.Context, edit_channel: discord.abc.GuildChannel) -> None:
    from helpers.role_select import RoleView
    message = RoleView.create_with_ctx(ctx)
    await edit_channel.send(embed=message.embed, view=message, file=message.file)


async def edit_categories(ctx: commands.Context) -> None:
    for category in ctx.guild.categories:
        logger.info(f"Checking category {category.name} for edit possibilities..")
        for overwrite_set in update["edit"]["categories"]:
            if overwrite_set["id"] == category.id:
                logger.info(f"Found overwrites for {category.name}.. adding to list")
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
            logger.info(f"Role found - Allowing role to view channel")
            overwrites.update({role: discord.PermissionOverwrite(view_channel=True)})
        mute_role = discord.utils.find(lambda c: c.name == "Mute", ctx.guild.roles)
        if mute_role:
            logger.info(f"Mute role found - Setting mute role overwrites")
            overwrites.update(
                {mute_role: discord.PermissionOverwrite(
                    add_reactions=False, change_nickname=False, use_application_commands=False,
                    manage_events=False, manage_threads=False, create_public_threads=False,
                    create_private_threads=False, send_messages_in_threads=False,
                    use_embedded_activities=False, connect=False, send_messages=False, ban_members=False,
                    kick_members=False)})
        logger.info(f"Overwrites constructed. Checking if {category.name} overwrites already set..")
        if category.overwrites == overwrites:
            logger.info(f"Category overwrites for {category.name} already set correctly. Skipping..")
            continue
        logger.info(f"Editing {category.name} overwrites..")
        await category.edit(overwrites=overwrites)
        logger.info(f"Category {category.name} overwrites edited successfully..")
        await asyncio.sleep(5)

        logger.info(f"Checking channels in category {category.name} to make sure they are synced..")
        for channel in category.channels:
            logger.info(f"Checking to see if channel {channel.name} is synced..")
            if channel.permissions_synced:
                logger.info(f"{channel.name} is already synced - Skipping..")
                continue
            logger.info(f"Syncing {channel.name} permissions to category {category.name}..")
            await channel.edit(sync_permissions=True)
            logger.info(f"{channel.name} synced successfully. Sleeping for a bit..")
            await asyncio.sleep(5)


async def clear_channel_overwrites(ctx: commands.Context) -> None:
    for channel in ctx.guild.channels:
        logger.info(f"Removing overwrites from channel {channel.name}..")
        if not channel.overwrites:
            logger.info(f"Channel {channel.name} has no overwrites. Skipping..")
            continue
        await channel.edit(overwrites={})
        logger.info(f"Overwrites removed from channel {channel.name}. Sleeping for a couple seconds..")
        await asyncio.sleep(5)


async def copy_roles_from_server(copy_guild: discord.Guild, exclude_roles):
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
            {"id": None, "name": "Buffalo", "colour": "#1a5ee6", "display_icon": 719580209799626812, "hoist": True},
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
            {"id": None, "name": "Getting Started"},
            {"id": None, "name": "Informational"},
            {"id": None, "name": "🦬| Buffalo"},
            {"id": None, "name": "Interests and Hobbies"},
            {"id": None, "name": "Archive"}
        ],
        "channels": [
            {"id": None, "name": "🎤-suggestions", "category": "Informational", "type": "forum",
             "topic": "Have a suggestion for the server? Drop a post and we can discuss it!"},
            {"id": None, "name": "🐶-bflo-pets", "category": "🦬| Buffalo", "type": "forum",
             "topic": "Post pictures of your pets!"},
            {"id": None, "name": "💵-bflo-ads-n-jobs", "category": "🦬| Buffalo", "type": "forum",
             "topic": "Classified ads and job postings in the WNY area. *NO CRYPTO OR SCAMS ALLOWED OR YOU WILL BE BANNED*"},
            {"id": None, "name": "🧻-politics", "category": "Interests and Hobbies", "type": "forum",
             "topic": "Politics 2.0 - Heavily moderated - Discuss national politics"},
            {"id": None, "name": "🎲-dice-board-gaming", "category": "Interests and Hobbies", "type": "text",
             "topic": "Nerd out and talk about all things board and dice games"}
        ]
    },
    "edit": {
        "roles": [
            {"id": 699934182822117396, "name": "Niagara Falls", "permissions": permissions['regions'],
             "colour": "#edec7e", "display_icon": "💦"},
            {"id": 699934215684489306, "name": "Expat", "new_name": "Just Visiting", "colour": "#0",
             "permissions": permissions['regions']},
            {"id": 699934108314501150, "name": "Northtowns", "permissions": permissions['regions'],
             "color": "#0"},
            {"id": 699934144817528843, "name": "Southtowns", "permissions": permissions['regions'],
             "color": "#0"},
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
            {"id": 696452764427092081, "name": "❓-help-desk", "category": "Informational"},
            {"id": 699928543798493226, "name": "🦬-set-your-roles-first", "new_name": "get-started", "category": None},
            {"id": 696071995984707684, "name": "💬-general", "category": "🦬| Buffalo"},
            {"id": 729031489244626954, "name": "introductions", "new_name": "👋-bflo-intros", "category": "🦬| Buffalo"},
            {"id": 719626310841925663, "name": "channel-select", "new_name": "🪪-bflo-roles", "category": "🦬| Buffalo",
             "topic": "Get some character and pick up fun server roles here"},
            {"id": 696452671598493696, "name": "🎫-things-to-do", "new_name": "🎫-bflo-fun", "category": "🦬| Buffalo",
             "topic": "Discuss fun stuff to do, or things that you have done, in this channel"},
            {"id": 696098329410404413, "name": "🍴food-and-dining", "new_name": "🍴🍺-bflo-food-and-drink",
             "category": "🦬| Buffalo",
             "topic": "Discuss all things food and drink here. Cooking, restaurants, food, and booze - it's all on the table!"},
            {"id": 696081227421057105, "name": "🏈-bills", "new_name": "🏈🏒-bflo-sports", "category": "🦬| Buffalo",
             "topic": "Your home for Bills/Sabres/Bandits/Bisons talk!"},
            {"id": 1020542502761136148, "name": "📺-news", "new_name": "📺-bflo-news", "category": "🦬| Buffalo",
             "topic": "News stories and discussion that pertain to Buffalo or WNY"},
            {"id": 696101473515339927, "name": "🐶-buffalo-pets", "new_name": "🐶-bflo-pets", "category": "Archive"},
            {"id": 718347467476697169, "name": "📷-pics", "new_name": "📷-bflo-pics", "category": "🦬| Buffalo"},
            {"id": 696207813948473394, "name": "🎮-gaming", "category": "Interests and Hobbies"},
            {"id": 698249578595614800, "name": "🎨🏎-hobbies", "new_name": "🏎-car-talk",
             "category": "Interests and Hobbies", "topic": "Vroom-Vroom - Talk about cars here"},
            {"id": 698705467500920892, "name": "🎧-music-theater-arts", "new_name": "🎧🍿📚-entertainment",
             "category": "Interests and Hobbies", "topic": "Your one stop shop for music, movies, and books"},
            {"id": 698659695577137262, "name": "🖥-tech", "category": "Interests and Hobbies",
             "topic": "Talk about software, networking, IT, whatever it may be. Just don't ask for help fixing your printer"},
            {"id": 1021958475401658429, "name": "🌱-lawn-and-garden", "new_name": "🌱-lawn-garden-diy",
             "category": "Interests and Hobbies",
             "topic": "Post about your DIY projects, your garden, home improvements, etc, here"},
            {"id": 700111188100644934, "name": "🙉-memes", "category": "Interests and Hobbies"},
            {"id": 960855040413802596, "name": "🤷-off-topic", "category": "Archive"},
            {"id": 702544939300683796, "name": "🍿-movies-and-tv", "category": "Archive"},
            {"id": 1034491595262799992, "name": "📚-books", "category": "Archive"},
            {"id": 697659404497190943, "name": "🚣🏾-sports", "category": "Archive"},
            {"id": 1060316382039920670, "name": "🍺-alcoholic-beverages", "category": "Archive"},
            {"id": 696924737242136689, "name": "🎤-suggestions", "category": "Archive"},
            {"id": 696094626284568788, "name": "💵-buy-sell-jobs", "category": "Archive"},
            {"id": 969344166922448936, "name": "🤖-bot-spam", "category": "Archive"},
            {"id": 696206515211599912, "name": "🧻-politics", "category": "Archive"},
            {"id": 696081453183926283, "name": "🏒-sabres", "category": "Archive"}
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
            {"id": 696096508910633000, "name": "Mods"},
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


async def generate_welcome_embed(ctx, edit_channel: discord.TextChannel):
    logger.info(f"Deleting old welcome messages..")
    async for message in edit_channel.history(limit=200):
        await message.delete()
        await asyncio.sleep(5)

    embed, file = await create_welcome_embed()
    logger.info(f"Sending welcome embed to {edit_channel.name}..")
    await edit_channel.send(embed=embed, file=file)
    await asyncio.sleep(5)
    logger.info(f"Sending rules embed to {edit_channel.name}")
    embed = await create_rules_embed()
    await edit_channel.send(embed=embed)
    await asyncio.sleep(5)
    logger.info(f"Sending channel directory embed to {edit_channel.name}")
    embed = await create_channel_embed(ctx)
    await edit_channel.send(embed=embed)
    await asyncio.sleep(5)
    logger.info(f"Sending staff embed to {edit_channel.name}")
    embed = await create_staff_embed(ctx)
    await edit_channel.send(embed=embed)
    await asyncio.sleep(5)


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


async def clear_role_perms(role):
    if not role.permissions:
        logger.info(f"{role.name} already has no permissions. Skipping..")
        return
    logger.info(f"Removing permissions from role {role.name}..")
    await role.edit(permissions=discord.Permissions.none())
    logger.info(f"Removed permissions from role {role.name}. Sleeping for a couple seconds")
    await asyncio.sleep(5)


async def validate_exists(ctx: commands.Context,
                          validate_role: Optional[Union[None, discord.Object]],
                          identifier: Dict):
    if not validate_role:
        validate_role = await get_by_id_or_name(ctx, identifier, 'role')
    return validate_role


async def copy_overwrites_from_buf_server(ctx: commands.Context,
                                          buf_cat: discord.CategoryChannel):
    channel_overrides = {ctx.guild.default_role: buf_cat.overwrites_for(buf_cat.guild.default_role)}
    for role, overwrites in buf_cat.overwrites.items():
        ctx_role = await validate_exists(ctx, None, {"name": role.name})
        if ctx_role:
            channel_overrides[ctx_role] = overwrites
    return channel_overrides


async def pick_random_role_and_assign(ctx, member: discord.Member):
    import random
    role = random.choice(update["delete"]["roles"])
    assign_role = await get_by_id_or_name(ctx, role, "role")
    if assign_role:
        await member.add_roles(assign_role)


async def assign_random_del_roles(ctx, delete_roles):
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
        await pick_random_role_and_assign(ctx, member)


async def create_channels(channels: List[Dict[str, Any]], ctx):
    mapping = {
        "text": ctx.guild.create_text_channel,
        "forum": ctx.guild.create_forum,
        "news": ctx.guild.create_text_channel,
    }
    for channel in channels:
        create_channel = await get_by_id_or_name(ctx, channel, "channel")
        if create_channel and create_channel.type.name == channel['type']:
            logger.info(f"Channel - {channel['name']} - found - skipping creation")
            continue
        func = mapping.get(channel['type'])
        if func:
            try:
                category = await get_by_id_or_name(ctx, {"name": channel['category']}, "category")
                logger.info(f"Creating channel {channel['name']}..")
                new_channel = await func(name=channel["name"],
                                         category=category if category else None,
                                         topic=channel.get("topic"))
                logger.info(f"New channel {new_channel.name} created with id - {new_channel.id} and "
                            f"type - {new_channel.type.name}. Sleeping..")
                await asyncio.sleep(5)
            except Exception as e:
                logger.warning(f"Cannot create {channel['type']} channel {channel['name']}: {e}")


async def get_overwrites(name, ctx):
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
            find_role = await get_by_id_or_name(ctx, role, "role")
            if find_role:
                overwrites.update({find_role: discord.PermissionOverwrite(view_channel=True)})
    return overwrites


async def create_categories(ctx: commands.Context, categories: List[Dict[str, Any]]):
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
                overwrites = await get_overwrites(name, ctx)
                await ctx.guild.create_category(name=name, overwrites=overwrites)
            except Exception as e:
                print(e)
                logger.info(f"Created category - {name}.. Sleeping")
            await asyncio.sleep(5)
        else:
            logger.info(f"Found category {name} already in {ctx.guild.name} - skipping creation "
                        f"and checking for channels")


async def copy_channels_from_server(ctx, copy_cats):
    channel_set = []
    for cat in copy_cats:
        channels = cat["channels"]
        for channel in channels:
            channel_set.append(
                {
                    "name": channel.name,
                    "type": channel.type.name,
                    "category": {"name": cat["name"]},
                    "topic": channel.topic,
                    "overwrites": await copy_overwrites_from_buf_server(ctx, channel)
                }
            )
    return channel_set


async def copy_categories_from_server(ctx, copy_cats: discord.Guild, exclude_cats):
    cats = copy_cats.categories
    not_excluded_cats = [{"name": cat.name,
                          "overwrites": await copy_overwrites_from_buf_server(ctx, cat),
                          "channels": cat.channels}
                         for cat in cats if cat.id not in [
                             exclude_cat['id'] for exclude_cat in exclude_cats]]
    return not_excluded_cats


async def clear_role_permissions(ctx):
    for role in ctx.guild.roles:
        if role.is_bot_managed():
            logger.info(f"Role -{role.name} is bot-managed. Skipping")
            continue
        await clear_role_perms(role)
        await asyncio.sleep(5)


async def edit_roles(ctx: commands.Context):
    for role in update['edit']['roles']:
        edit_role = await get_by_id_or_name(ctx, role, "role")
        if not edit_role:
            logger.warning(f"Unable to find {role['name']} to edit - Does it exist or has it been deleted?")
            continue
        if edit_role:
            name = role.get("new_name", edit_role.name)
            colour = discord.Colour.from_str(role.get('colour')) if role.get('colour') else edit_role.color
            perms = role.get("permissions", None)
            logger.info(f"Editing role {edit_role.name}")
            try:
                await edit_role.edit(name=name,
                                     colour=colour,
                                     permissions=perms)
                logger.info(f"Role {edit_role.name} edited successfully")
                logger.info(f"Sleeping for a few seconds..")
                await asyncio.sleep(5)
            except Exception as e:
                print(e)


async def delete_categories(ctx):
    for category in update["delete"]["categories"]:
        delete_cat = await get_by_id_or_name(ctx, category, "category")
        if delete_cat:
            logger.info(f"Deleting category - {delete_cat.name}..")
            await delete_cat.delete()
            logger.info(f"Category {delete_cat.name} deleted successfully.. Sleeping")
            await asyncio.sleep(5)


async def delete_roles(ctx):
    for role in update["delete"]["roles"]:
        delete_role = await get_by_id_or_name(ctx, role, "role")
        if not delete_role:
            continue
        logger.info(f"Deleting role {delete_role.name}..")
        await delete_role.delete()
        logger.info(f"Role {delete_role.name} deleted successfully. Sleeping..")
        await asyncio.sleep(5)
