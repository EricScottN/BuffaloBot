from datetime import datetime, timedelta, UTC
import asyncio
from typing import Dict

from discord import TextChannel

from buffalobot import BuffaloBot


class GameDayThread:
    def __init__(
            self,
            bot: BuffaloBot,
            gdt_channel: TextChannel,
            game_id: str
    ):
        self.bot: BuffaloBot = bot
        self.gdt_channel = gdt_channel
        self.game_id = game_id
        self.play_id = None

    async def start(self):
        while not self.check_game_status():
            await self.update_thread()
            await asyncio.sleep(10)

    async def update_thread(self):
        scoring_plays = await self.get_scoring_plays()
        if not scoring_plays:
            return
        most_recent_scoring_play = scoring_plays[-1]
        play_id = most_recent_scoring_play['id']
        if play_id == self.play_id:
            return
        self.play_id = play_id
        scoring_team_id = most_recent_scoring_play['team']['id']
        if scoring_team_id != 2:
            return
        text = most_recent_scoring_play['text']
        await asyncio.sleep(30)
        await self.gdt_channel.send(text)

    async def check_game_status(self) -> bool:
        url = f'https://cdn.espn.com/core/nfl/game?xhr=1&gameId={self.game_id}'
        async with self.bot.web_client.get(url) as response:
            game_status = (await response.json())['content']['statusState']
        if game_status == 'post':
            return True
        return False

    async def get_scoring_plays(self):
        url = f'https://cdn.espn.com/core/nfl/playbyplay?xhr=1&gameId={self.game_id}'
        async with self.bot.web_client.get(url) as response:
            game_package = (await response.json())['gamepackageJSON']
        scoring_plays = game_package['scoringPlays']
        return scoring_plays


async def update_channel_name(
        bills_nickname: str,
        home_away: str,
        gdt_channel: TextChannel,
        opposing_team: str):
    home_away_str = 'vs'
    if home_away == 'home':
        home_away_str = '@'
    await gdt_channel.edit(name=f'{bills_nickname} {home_away_str} {opposing_team}')


async def check_channel(bills_schedule: Dict, competition: Dict, gdt_channel: TextChannel):
    competitors = competition['competitors']
    bills_nickname = bills_schedule['team']['name']
    for competitor in competitors:
        team = competitor['team']['nickname']
        if team != bills_nickname and team not in gdt_channel.name:
            home_away = competitor['homeAway']
            await update_channel_name(bills_nickname, home_away, gdt_channel, team)
