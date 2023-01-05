from typing import Any
import logging
import discord
from discord.ext import commands
from discord import Interaction, app_commands


# TODO get these values from a database of region roles
municipalities_values = ['Amherst', 'Aurora', 'Buffalo', 'Cheektowaga', 'Clarence', 'Evans', 'Grand Island',
                         'Hamburg', 'Lackawanna', 'Lancaster', 'Orchard Park', 'Tonawanda', 'West Seneca',
                         'Nearby', 'Just Visiting']

logger = logging.getLogger(__name__)


def generate_region_embed():
    embed = discord.Embed(
        title="Municipality Selection",
        description="Select a municipality to gain access to the server.\n\n"
                    "Below is a map of cities and towns in WNY to help aide in your selection."
    )
    f = discord.File("files/Erie_County_NY_map_labeled.png")
    embed.set_image(url="attachment://Erie_County_NY_map_labeled.png")

    return f, embed


async def get_municipality_roles(ctx):
    roles = []
    for role in ctx.guild.roles:
        if role.name in municipalities_values:
            logger.info(f"adding role {role.name} to role select")
            roles.append(role)
    return roles


class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        super().__init__(custom_id="role_select", min_values=1, max_values=1,
                         placeholder="Select roles to be added/removed")
        if roles:
            for role in roles:
                self.add_option(label=role.name, value=str(role.id))

    async def callback(self, interaction: Interaction) -> Any:
        role = interaction.guild.get_role(int(self.values[0]))
        message = ''
        if role in interaction.user.roles:
            await interaction.response.send_message(f"You already have the role {role.mention}", ephemeral=True)
            return
        for member_role in interaction.user.roles:
            if member_role.name in municipalities_values:
                await interaction.user.remove_roles(member_role)
                removed_role = member_role
                message += f"Removed role {removed_role.mention} | "
        await interaction.user.add_roles(role)
        await interaction.response.send_message(message + f"Added role {role.mention}", ephemeral=True)



class RoleView(discord.ui.View):
    def __init__(self, roles=None):
        self.roles = roles
        super().__init__(timeout=None)
        self.add_item(RoleSelect(self.roles))

    @classmethod
    async def construct_view(cls, ctx):
        roles = await get_municipality_roles(ctx)
        if roles:
            return cls(roles)

