from typing import Any

import discord
from discord import Interaction


class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        super().__init__(custom_id="role_select", min_values=1, max_values=1,
                         placeholder="Select roles to be added/removed")
        for role in roles:
            self.add_option(label=role.name, value=str(role.id))

    async def callback(self, interaction: Interaction) -> Any:
        role = interaction.guild.get_role(int(self.values[0]))
        if role in interaction.user.roles:
            await interaction.response.send_message(f"You already have the role {role.mention}", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        await interaction.response.send_message(f"Added role {role.mention}", ephemeral=True)


class RoleView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))
