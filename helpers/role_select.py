from typing import Any
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
            if member_role.name in RoleView.MUNICIPALITIES:
                await interaction.user.remove_roles(member_role)
                removed_role = member_role
                message += f"Removed role {removed_role.mention} | "
        await interaction.user.add_roles(role)
        await interaction.response.send_message(message + f"Added role {role.mention}", ephemeral=True)


class RoleView(discord.ui.View):
    MUNICIPALITIES = ['Amherst', 'Aurora', 'Buffalo', 'Cheektowaga', 'Clarence', 'Evans', 'Grand Island', 'Hamburg',
                      'Lackawanna', 'Lancaster', 'Orchard Park', 'Tonawanda', 'West Seneca', 'Nearby', 'Just Visiting']

    def __init__(self, ctx=None, embed=None, file=None, roles=None):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = embed
        self.file = file
        self.roles = roles
        self.add_item(RoleSelect(self.roles))

    @classmethod
    def create_with_ctx(cls, ctx):
        roles = cls.get_municipality_roles(ctx, cls.MUNICIPALITIES)
        return cls(ctx=ctx,
                   embed=cls.generate_region_embed(),
                   file=discord.File("files/erie_county_map.jpg"),
                   roles=roles)

    @staticmethod
    def get_municipality_roles(ctx, municipalities):
        roles = []
        for role in ctx.guild.roles:
            if role.name in municipalities:
                logger.info(f"adding role {role.name} to role select")
                roles.append(role)
        return roles

    @staticmethod
    def generate_region_embed():
        embed = discord.Embed(
            title="Municipality Selection",
            description="Select a municipality to gain access to the server.\n\n"
                        "Below is a map of cities and towns in WNY to help aide in your selection."
        )
        embed.set_image(url="attachment://erie_county_map.jpg")

        return embed
