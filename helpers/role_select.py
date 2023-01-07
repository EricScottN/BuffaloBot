from typing import Any, List
import logging
import discord
from discord import Interaction

# TODO get these values from a database of region roles


logger = logging.getLogger(__name__)


class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        self.roles = roles
        super().__init__(custom_id="role_select", min_values=1, max_values=1,
                         placeholder="Select roles to be added/removed")

        if self.roles:
            for role in self.roles:
                self.add_option(label=role.name, value=str(role.id))

    async def callback(self, interaction: Interaction) -> Any:
        role = interaction.guild.get_role(int(self.values[0]))
        message = ''
        if role in interaction.user.roles:
            await interaction.response.send_message(f"You already have the role {role.mention}", ephemeral=True)
            return
        for member_role in interaction.user.roles:
            if member_role.name in municipalities:
                await interaction.user.remove_roles(member_role)
                removed_role = member_role
                message += f"Removed role {removed_role.mention} | "
        await interaction.user.add_roles(role)
        await interaction.response.send_message(message + f"Added role {role.mention}", ephemeral=True)


class RoleView(discord.ui.View):

    def __init__(self, ctx=None, embed=None, file=None, roles=None):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = embed
        self.file = file
        self.roles = roles
        self.add_item(RoleSelect(self.roles))

    @classmethod
    def create_with_ctx(cls, ctx):
        roles = get_municipality_roles(ctx, municipalities)
        embed = generate_region_embed(roles)
        return cls(ctx=ctx,
                   embed=embed,
                   file=discord.File("files/erie_county_map.jpg"),
                   roles=roles)


municipalities = ['Amherst', 'Aurora', 'Buffalo', 'Cheektowaga', 'Clarence', "Eden", 'Evans', 'Grand Island',
                  'Hamburg', 'Lackawanna', 'Lancaster', 'Lockport', 'Niagara Falls', 'North Tonawanda',
                  'Orchard Park', 'Tonawanda', 'West Seneca', 'Nearby', 'Just Visiting']


def get_municipality_roles(ctx, municipalities):
    roles = []
    for role in ctx.guild.roles:
        if role.name in municipalities:
            logger.info(f"adding role {role.name} to role select")
            roles.append(role)
    return roles


def generate_region_embed(roles):
    embed = discord.Embed(
        title="Municipality Selection",
        description="Select a municipality to gain access to the server.\n\n"
                    "If you don't currently reside in Buffalo, you can select a Miscellaneous role."
    )
    embed.set_image(url="attachment://erie_county_map.jpg")
    embed.add_field(name="Buffalo Cities and Towns",
                    value=construct_embed_values(
                        roles, ['Nearby', 'Just Visiting', 'Lockport', 'North Tonawanda', 'Niagara Falls'], False),
                    inline=False)
    embed.add_field(name="Niagara County Cities",
                    value=construct_embed_values(
                        roles, ['Lockport', 'North Tonawanda', 'Niagara Falls'], True),
                    inline=False)
    embed.add_field(name="Miscellaneous",
                    value=construct_embed_values(
                        roles, ['Nearby', 'Just Visiting'], True),
                    inline=False)
    return embed


def construct_embed_values(roles: List[discord.Role], valid: List, in_list: bool):
    if in_list:
        valid_roles = [role.name for role in roles if role.name in valid]
    else:
        valid_roles = [f"`{role.name}`" for role in roles if role.name not in valid]
    if not valid_roles:
        return "No roles found"
    return " | ".join(valid_roles)
