import logging
import json

from helpers.utils import *

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
        if ctx.guild.id == ctx.bot.testing_guild_id:
            await self.delete_from_test(ctx)
            await self.stage_testing_guild(ctx)

        # Clear all category and channel overwrites
        logger.info("Clearing category and channel overwrites..")
        await clear_channel_overwrites(ctx)

        # Clear all role permissions (except bot managed)
        logger.info("Clearing role permissions..")
        await clear_role_permissions(ctx)

        # TODO Test this with display icon in Buffalo server
        # Create new region roles
        logger.info("Creating roles..")
        await self.create_roles(ctx, update["create"]["roles"])

        # Edit existing roles
        logger.info("Editing roles..")
        await edit_roles(ctx)

        # Replace Existing Buffalo role with new Buffalo role
        logger.info("Replacing Buffalo roles with new Buffalo roles..")
        await self.replace_buffalo_roles(ctx)

        # Delete categories
        logger.info("Deleting categories..")
        await delete_categories(ctx)

        # Create new categories with overwrites
        logger.info("Creating new categories..")
        await create_categories(ctx, update["create"]["categories"])

        # Update existing category overwrites
        logger.info("Editing existing categories..")
        # TODO put some logging in this function
        await edit_categories(ctx)

        # TODO test this with a single forum channel in Buffalo server
        # Create new channels
        logger.info("Creating new channels..")
        await create_channels(update["create"]["channels"], ctx)

        # Move existing channels to correct categories (including archive)
        logger.info("Editing existing channels..")
        await edit_channels(ctx)

        logger.info("Syncing channel perms..")
        await sync_channel_permissions(ctx)

        # Delete roles
        logger.info("Deleting roles..")
        await delete_roles(ctx)

        logger.info("Generating new welcome embed..")
        await generate_welcome_embed(ctx, discord.utils.find(
            lambda c: c.name == "📝-welcome-rules", ctx.guild.channels))

        logger.info("Generating new getting started..")
        await self.create_getting_started(ctx, discord.utils.find(
            lambda c: c.name == "get-started", ctx.guild.channels))

        await create_send_roleview(ctx, discord.utils.find(
            lambda c: c.name == "🪪-bflo-roles", ctx.guild.channels))
        logger.info("UPDATE COMPLETE")

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
            await delete_categories(ctx)
        if "roles" in delete_elements:
            await delete_roles(ctx)

    @commands.command(name="stage")
    @commands.is_owner()
    @is_testing_guild()
    async def stage_testing_guild(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass

        buffalo_guild: discord.Guild = self.bot.get_guild(self.bot.bot_vars["BUFFALO_ID"])

        roles = await copy_roles_from_server(buffalo_guild, update["exclude_copy_from_buf_server"]['roles'])
        await self.create_roles(ctx, roles)
        logger.info("==============================")
        logger.info("ALL ROLES CREATED SUCCESSFULLY")
        logger.info("==============================")

        categories = await copy_categories_from_server(ctx, buffalo_guild,
                                                       update["exclude_copy_from_buf_server"]["categories"])
        await create_categories(ctx, categories)
        logger.info("===================================")
        logger.info("ALL CATEGORIES CREATED SUCCESSFULLY")
        logger.info("===================================")

        channels = await copy_channels_from_server(ctx, categories)
        await create_channels(channels, ctx)
        logger.info("=================================")
        logger.info("ALL CHANNELS CREATED SUCCESSFULLY")
        logger.info("=================================")

        await assign_random_del_roles(ctx, region_delete_roles)
        logger.info("=================================")
        logger.info("======DELETE ROLES ASSIGNED======")
        logger.info("=================================")

    @commands.command(name="replace")
    @commands.is_owner()
    async def replace_buffalo_roles(self, ctx: commands.Context):
        replace_role = await get_by_id_or_name(ctx, update['create']['roles'][2], "role")
        if not replace_role:
            logger.warning(f"Cannot find replace role -{replace_role}- in {ctx.guild.name}.")
            return
        region_replace_roles = [region_delete_role["name"] for region_delete_role in region_delete_roles]
        members = ctx.guild.members
        replace_dict = []
        for member in members:
            member_roles = member.roles
            member_role_names = [role.name for role in member_roles]
            roles = set(member_role_names).intersection(region_replace_roles)
            if not roles:
                continue
            if not replace_role:
                continue
            replace_dict.append({"member_id": member.id,
                                 "member_name": member.name,
                                 "member_roles": [role for role in roles]
                                 })
            await member.add_roles(replace_role)
        with open('files/replaced_buffalo_roles.json', 'w') as f:
            # Write the JSON object to the file
            json.dump(replace_dict, f)

    @commands.command(name="create")
    @commands.is_owner()
    async def create(self, ctx, *element_type):
        if "roles" in element_type:
            await self.create_roles(ctx, update["create"]["roles"])
        if "categories" in element_type:
            await create_categories(ctx, update["create"]["categories"])
        if "channels" in element_type:
            await create_channels(update["create"]["channels"], ctx)

    @commands.command(name="edit")
    @commands.is_owner()
    async def edit(self, ctx, *element_type):
        if "roles" in element_type:
            await edit_roles(ctx)
        if "categories" in element_type:
            await edit_categories(ctx)
        if "channels" in element_type:
            await edit_channels(ctx)

    @commands.command(name="welcome")
    @commands.is_owner()
    async def welcome(self, ctx: commands.Context):
        await generate_welcome_embed(ctx, ctx.channel)

    @commands.command(name="getting_started")
    @commands.is_owner()
    async def create_getting_started(self, ctx: commands.Context,
                                     edit_channel: Union[discord.TextChannel, commands.TextChannelConverter]):
        overwrites = {}
        for role in update["edit"]["roles"] + update["create"]["roles"]:
            overwrite_role = await get_by_id_or_name(ctx, role, "role")
            if overwrite_role:
                overwrites.update({overwrite_role: discord.PermissionOverwrite(read_messages=False)})
        overwrites.update({ctx.guild.default_role: discord.PermissionOverwrite(read_messages=True,
                                                                               read_message_history=True)})

        # Import RoleView to create role select message and send to edit channel
        await create_send_roleview(ctx, edit_channel)
        await edit_channel.edit(overwrites=overwrites)
        # Delete old region role select
        await edit_channel.get_partial_message(699934917378703370).delete()

    @commands.command(name="clear")
    @commands.is_owner()
    async def clear(self, ctx, *clear_elements):
        if "roles" in clear_elements:
            await clear_role_permissions(ctx)
        if "channels" in clear_elements:
            await clear_channel_overwrites(ctx)

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
            display_icon = role.get("display_icon", None)
            if isinstance(display_icon, int):
                display_icon = await self.bot.get_emoji(display_icon).read()
            hoist = role.get('hoist', False)
            perms = role.get("permissions", permissions['regions'])
            new_role = await ctx.guild.create_role(
                name=name,
                colour=colour,
                hoist=hoist,
                display_icon=display_icon,
                permissions=perms)
            logger.info(f"Role -{new_role.name}- created with id -{new_role.id}-\nSleeping for a couple seconds so I"
                        f" don't get rate limited")
            await asyncio.sleep(2)


async def setup(bot):
    await bot.add_cog(Updater(bot))
