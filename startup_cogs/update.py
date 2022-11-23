import discord
from discord import app_commands
from discord.ext.commands import Context, Greedy
from discord.ext import commands


update = {
    "remove": {
        "channels": {
            "channel-select": 719626310841925600,
            "severe_weather_alerts": 719889462074802200,
            "online_dispatcher": 1006173711805722800,
            "r_buffalo_hot_posts": 720414229110194200,
            "🎨🏎-hobbies": 698249578595614800,
            "🤷-off-topic": 960855040413802600,
            "🏒-sabres": 696081453183926300
        },
        "categories": {
            "Visiting Buffalo": 696068936483209200,
            "Alerts and Feeds": 719888960645627900,
            "Buffalo Professional Sports": 719672353814085600,
            "Sports": 696088544430653400,
            "General": 719675429614518400
        },
        "roles": {
            "owner of a lonely heart": 1038666998936256532,
            "VIP - Toronto Admin": 1020758923302678529,
            "r_Buffalo Hot Posts": 720608051090030683,
            "Severe Weather": 719889343241519175,
            "Alerts and Feeds": 719889204045414401,
            "Buffalo Sports": 719614411794415647,
            "Local News": 719604297834299485,
            "Local Politics": 719604247490068532,
            "Professional Buffalo Sports": 719603969399324732,
            "Local News and Politics": 719603900688236544,
            "All Channels": 719603773194109020,
            "Online DIspatcher": 1006545113549385748
        }
    },
    "add": {
        "categories": [
            "🦬| Buffalo",
            "📜| Informational"
        ],
        "roles": [
            "Nearby",
            "Just Visiting"
        ]
    },
    "change": {
        "channels": [
            {
                "name": "🎫-things-to-do",
                "new_name": "🎫-bflo-fun"
            },
            {
                "name": "introductions",
                "new_name": "👋-introductions"
            },

        ]
    }
}


class Updater(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="update")
    @commands.is_owner()
    async def update(self, ctx):
        guild = ctx.guild
        if guild == self.bot.bot_vars['FOWNY_ID']:
            # add categories

            # add channels
            new_channels = []
            for k, v in update['remove']['channels']:
                new_channels.append(await guild.create_text_channel(name=k))
        pass

async def setup(bot):
    await bot.add_cog(Updater(bot))
