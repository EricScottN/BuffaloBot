from datetime import datetime, timedelta, UTC
import logging
import asyncio
from typing import Optional, List

import discord
from pydantic import BaseModel, Field, field_validator

from discord import TextChannel, Embed

from buffalobot import BuffaloBot

logger = logging.getLogger(__name__)


class Logo(BaseModel):
    href: str = Field(alias="href")
    width: int = Field(alias="width")
    height: int = Field(alias="height")
    alt: str = Field(alias="alt")
    rel: List[str] = Field(alias="rel")
    last_updated: str = Field(alias="lastUpdated")


class Team(BaseModel):
    team_id: Optional[str] = Field(default=None, alias="id")
    uid: Optional[str] = Field(default=None, alias="uid")
    slug: Optional[str] = Field(default=None, alias="slug")
    location: Optional[str] = Field(default=None, alias="location")
    name: Optional[str] = Field(default=None, alias="name")
    abbreviation: Optional[str] = Field(default=None, alias="abbreviation")
    display_name: Optional[str] = Field(default=None, alias="displayName")
    short_display_name: Optional[str] = Field(default=None, alias="shortDisplayName")
    color: Optional[str] = Field(default=None, alias="color")
    alternate_color: Optional[str] = Field(default=None, alias="alternateColor")
    logo: Optional[str] = Field(default=None, alias="logo")
    logos: Optional[List[Logo]] = Field(default=None, alias="logos")


class Teams(BaseModel):
    team: Team = Field(alias="team")


class CollegeAthlete(BaseModel):
    field_ref: str = Field(..., alias='$ref')


class Status(BaseModel):
    status_id: str = Field(alias="id")
    name: str = Field(alias="name")
    status_type: str = Field(alias="type")
    abbreviation: str = Field(alias="abbreviation")


class Position(BaseModel):
    name: str = Field(alias="name")
    display_name: str = Field(alias="displayName")
    abbreviation: str = Field(alias="abbreviation")


class Link(BaseModel):
    rel: List[str]
    href: str
    text: Optional[str] = Field(default=None)


class Headshot(BaseModel):
    href: str
    alt: str


class Athlete(BaseModel):
    id: Optional[str] = Field(default=None, alias="id")
    uid: Optional[str] = Field(default=None, alias="uid")
    guid: Optional[str] = Field(default=None, alias="guid")
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: str = Field(default=None, alias="lastName")
    full_name: Optional[str] = Field(default=None, alias="fullName")
    display_name: str = Field(default=None, alias="displayName")
    jersey: Optional[str] = Field(default=None, alias="jersey")
    short_name: Optional[str] = Field(default=None, alias="shortName")
    links: Optional[List[Link]] = Field(default=None, alias="links")
    headshot: Optional[Headshot] = Field(default=None, alias="headshot")
    position: Optional[Position] = Field(default=None, alias="position")
    team: Team = Field(default=None, alias="team")
    college_athlete: CollegeAthlete = Field(default=None, alias="collegeAthlete")
    status: Status = Field(default=None, alias="status")


class Statistic(BaseModel):
    name: str = Field(alias="name")
    display_value: Optional[str] = Field(default=None, alias="displayValue")
    label: Optional[str] = Field(default=None, alias="label")
    keys: Optional[List[str]] = Field(default=None, alias="keys")
    text: Optional[str] = Field(default=None, alias="text")
    descriptions: Optional[List[str]] = Field(default=None, alias="descriptions")
    athletes: List[Athlete] = Field(default=None, alias="athletes")
    totals: Optional[List[str]] = Field(default=None, alias="totals")


class Player(BaseModel):
    team: Team = Field(alias="team")
    statistics: List[Statistic] = Field(alias="statistics")
    display_order: int = Field(alias="displayOrder")


class Boxscore(BaseModel):
    teams: List[Teams]
    players: Optional[List[Player]] = Field(default=None)


class Period(BaseModel):
    number: int = Field(alias="number")
    period_type: Optional[str] = Field(default=None, alias="type")


class Clock(BaseModel):
    display_value: str = Field(alias="displayValue")
    value: Optional[int] = Field(default=None, alias="value")


class StartEndDrive(BaseModel):
    period: Period = Field(alias="period")
    clock: Optional[Clock] = Field(default=None, alias="clock")
    yard_line: int = Field(alias="yardLine")
    text: str = Field(alias="text")


class TimeElapsed(BaseModel):
    display_value: str = Field(alias="displayValue")


class PlayType(BaseModel):
    type_id: str = Field(alias="id")
    text: str = Field(alias="text")
    abbreviation: Optional[str] = Field(default=None, alias="abbreviation")


class StartEndPlay(BaseModel):
    down: int = Field(alias="down")
    distance: int = Field(alias="distance")
    yard_line: int = Field(alias="yardLine")
    yards_to_endzone: int = Field(alias="yardsToEndzone")
    team: Optional[Team] = Field(default=None, alias="team")
    down_distance_text: Optional[str] = Field(default=None, alias="downDistanceText")
    short_down_distance_text: Optional[str] = Field(default=None, alias="shortDownDistanceText")
    possession_text: Optional[str] = Field(default=None, alias="possessionText")


class ScoringType(BaseModel):
    name: str = Field(alias="name")
    display_name: str = Field(alias="displayName")
    abbreviation: str = Field(alias="abbreviation")


class Stat(BaseModel):
    name: str = Field(alias="name")
    display_value: str = Field(alias="displayValue")


class Participant(BaseModel):
    athlete: Athlete = Field(alias="athlete")
    stats: List[Stat] = Field(alias="stats")
    participant_type: str = Field(alias="type")


class Play(BaseModel):
    play_id: str = Field(alias="id")
    sequenceNumber: Optional[str] = Field(default=None, alias="sequenceNumber")
    play_type: Optional[PlayType] = Field(alias="type")
    text: str = Field(alias="text")
    away_score: int = Field(alias="awayScore")
    home_score: int = Field(alias="homeScore")
    period: Period = Field(alias="period")
    clock: Clock = Field(alias="clock")
    scoring_play: Optional[bool] = Field(default=None, alias="scoringPlay")
    priority: Optional[bool] = Field(default=None, alias="priority")
    modified: Optional[str] = Field(default=None, alias="modified")
    wallclock: Optional[str] = Field(default=None, alias="wallclock")
    start: Optional[StartEndPlay] = Field(default=None, alias="start")
    end: Optional[StartEndPlay] = Field(default=None, alias="end")
    stat_yardage: Optional[int] = Field(default=None, alias="statYardage")
    score_value: Optional[int] = Field(default=None, alias="scoreValue")
    scoring_type: Optional[ScoringType] = Field(default=None, alias="scoringType")
    participants: Optional[List[Participant]] = Field(default=None, alias="participants")
    team: Optional[Team] = Field(default=None)


class Drive(BaseModel):
    drive_id: str = Field(alias="id")
    description: str = Field(alias="description")
    team: Team = Field(alias="team")
    start: StartEndDrive = Field(alias="start")
    end: Optional[StartEndDrive] = Field(default=None, alias="end")
    time_elapsed: TimeElapsed = Field(alias="timeElapsed")
    yards: int = Field(alias="yards")
    is_score: bool = Field(alias="isScore")
    offensive_plays: int = Field(alias="offensivePlays")
    result: Optional[str] = Field(default=None, alias="result")
    short_display_result: Optional[str] = Field(default=None, alias="shortDisplayResult")
    display_result: Optional[str] = Field(default=None, alias="displayResult")
    plays: List[Play] = Field(alias="plays")


class Drives(BaseModel):
    current: Optional[Drive]
    previous: Optional[List[Drive]]


class Summary(BaseModel):
    boxscore: Boxscore
    drives: Optional[Drives] = Field(default=None)
    scoring_plays: Optional[List[Play]] = Field(default=None, alias="scoringPlays")


class StatusType(BaseModel):
    id: str
    name: str
    state: str
    completed: bool
    description: str
    detail: str
    shortDetail: str


class CompetitionType(BaseModel):
    id: str
    text: str
    abbreviation: str
    slug: str
    competition_type: str = Field(alias="type")


class CompetitionStatus(BaseModel):
    clock: float
    display_clock: str = Field(alias="displayClock")
    period: int
    status_type: StatusType = Field(alias="type")
    is_tbd_flex: bool = Field(alias="isTBDFlex")


class Ticket(BaseModel):
    id: str
    summary: str
    description: str
    max_price: float = Field(alias="maxPrice")
    starting_price: float = Field(alias="startingPrice")
    number_available: int = Field(alias="numberAvailable")
    total_postings: int = Field(alias="totalPostings")
    links: List[Link]


class Address(BaseModel):
    city: str = Field(alias="city")
    state: str = Field(alias="state")
    zip_code: str = Field(alias="zipCode")


class Venue(BaseModel):
    full_name: str = Field(alias="fullName")
    address: Address


class Score(BaseModel):
    value: float
    display_value: str = Field(alias="displayValue")


class Competitor(BaseModel):
    id: str
    competitor_type: str = Field(alias="type")
    order: int
    home_away: str = Field(alias="homeAway")
    winner: Optional[bool] = None
    team: Team
    score: Optional[Score] = None


class Competition(BaseModel):
    id: str
    date: datetime
    attendance: int
    competition_type: CompetitionType = Field(alias="type")
    time_valid: bool = Field(alias="timeValid")
    neutral_site: bool = Field(alias="neutralSite")
    boxscore_available: bool = Field(alias="boxscoreAvailable")
    tickets_available: bool = Field(alias="ticketsAvailable")
    venue: Venue
    competitors: List[Competitor]
    notes: List
    status: CompetitionStatus
    tickets: Optional[List[Ticket]] = None

    @field_validator('date', mode="before")
    def parse_datetime(cls, value: str) -> datetime:
        return datetime.fromisoformat(value)


class Event:
    def __init__(
            self,
            drive: Optional[Drive] = None,
            play: Optional[Play] = None,
            embed: Optional[Embed] = None
    ):
        self.drive: Optional[Drive] = drive
        self.play: Optional[Play] = play
        self.embed: Optional[Embed] = embed


class PreGameDay:
    def __init__(
            self,
            bot: BuffaloBot,
            team_id: int,
            gdt_channel: TextChannel,
            channel_update_delta: int,
    ):
        self.bot: BuffaloBot = bot
        self.team_id: int = team_id
        self.gdt_channel: TextChannel = gdt_channel
        self.channel_update_delta: timedelta = timedelta(
            hours=channel_update_delta
        )

    async def setup(self):
        game: Optional[Competition] = await self.refresh_competition()
        if not game:
            logger.info("No game found..")
            return
        game = await self.sleep_until_thread(game)

    async def refresh_competition(self) -> Optional[Competition]:
        url = (
            'https://site.api.espn.com/apis/site/v2/sports/'
            f'football/nfl/teams/{self.team_id}/schedule'
        )
        logger.info("Getting current game from api: %s", url)
        async with self.bot.web_client.get(url) as response:
            schedule = (await response.json())
            events = schedule["events"]
        for event in events:
            competition = Competition(**event["competitions"][0])
            if competition.status.status_type.name != "STATUS_FINAL":
                return competition

    async def sleep_until_thread(self, game: Competition) -> Competition:
        current_datetime = datetime.now(UTC)
        thread_start = game.date - self.channel_update_delta
        if current_datetime < game.date and current_datetime < thread_start:
            sleep_seconds = (thread_start - current_datetime).seconds
            await asyncio.sleep(sleep_seconds + 180)
            game: Competition = await self.refresh_competition()
            await self.sleep_until_thread(game)
        return game

    async def get_teams(self, game: Competition, team_id: int):
        team: Optional[Team] = None
        opp_team: Optional[Team] = None
        for competitor in game.competitors:
            if competitor.id == team_id:
                team = competitor.team
            else:
                opp_team = competitor.team
        return team, opp_team


class GameDayThread:
    def __init__(
            self,
            bot: BuffaloBot,
            team_id: int,
            gdt_channel: TextChannel,
            channel_update_delta: int,
            cooldown: int = 10,
            game: Optional[Competition] = None
    ):
        self.bot: BuffaloBot = bot
        self.team: Team = Team(id=str(team_id))
        self.gdt_channel: TextChannel = gdt_channel
        self.channel_update_delta: timedelta = timedelta(
            hours=channel_update_delta
        )
        self.cooldown: int = cooldown
        self.game: Optional[Competition] = game
        self.opp_team: Optional[Team] = None

    async def get_competition(self):
        logger.info("Getting current game...")
        url = (
            'https://site.api.espn.com/apis/site/v2/sports/'
            f'football/nfl/teams/{self.team.team_id}/schedule'
        )
        async with self.bot.web_client.get(url) as response:
            schedule = (await response.json())
            events = schedule["events"]
        for event in events:
            competition = Competition(**event["competitions"][0])
            if competition.status.status_type.name == "STATUS_FINAL":
                continue
            self.game = competition
            await self.get_opp_team()
            return

    async def get_opp_team(self):
        for team in self.game.competitors:
            if team.id == self.team.team_id:
                self.team = team.team
            else:
                self.opp_team = team.team

    async def update_channel_name(self):
        await self.sleep_until_thread()
        if self.opp_team.short_display_name.lower() in self.gdt_channel.name:
            return
        await self.gdt_channel.edit(
            name=f'{self.team.short_display_name}-vs-'
                 f'{self.opp_team.short_display_name}'
        )

    async def start(self):
        await self.sleep_until_game_start()
        event = Event()
        while not await self.check_game_status():
            summary = await self.get_game_summary()
            await self.sleep_until_next_update(summary)
            if not summary.drives:
                logger.info("No drives found..")
                continue
            if not summary.drives.current:
                logger.info("No current drives found..")
                continue
            if not event.drive:
                event.drive = summary.drives.current
            if event.drive == summary.drives.current or event.play == summary.drives.current.plays[-1]:
                logger.info("No new plays since last update..")
                continue
            plays_since = []
            if summary.drives.current.drive_id == event.drive.drive_id:
                num_missed_plays = len(summary.drives.current.plays) - len(event.drive.plays)
                if num_missed_plays == 0:
                    logger.info("No new plays since last update..")
                    continue
                plays_since = summary.drives.current.plays[-num_missed_plays:]
                logger.info("Found %s new play(s) since last update..", len(plays_since))
            for play in plays_since:
                logger.info(play)
                event.play = play
                await self.generate_play_embed(event)
            event.drive = summary.drives.current

    async def sleep_until_next_update(self, summary: Summary):
        logger.info("Sleeping for %s seconds until next update..",
                    self.cooldown
                    )
        await asyncio.sleep(self.cooldown)

    async def generate_play_embed(self, event: Event):
        if event.drive.team.abbreviation == self.team.abbreviation:
            # Scoring plays
            if event.play.scoring_play and event.play.scoring_type.abbreviation in ['TD', 'FG']:
                embed = Embed(
                    title=f"{event.play.play_type.text}".upper(),
                    colour=discord.Colour.blue(),
                    description=event.play.text)
                embed.set_footer(text=event.play.play_id)
                return await self.gdt_channel.send(embed=embed)
            if event.play.stat_yardage >= 20 and event.play.play_type.type_id != '60':
                embed = Embed(
                    title=f"EXPLOSIVE PLAY",
                    colour=discord.Colour.blue(),
                    description=event.play.text
                )
                embed.set_footer(text=event.play.play_id)
                return await self.gdt_channel.send(embed=embed)
        if event.drive.team.abbreviation == self.opp_team.abbreviation:
            if event.play.play_type.type_id == '26':
                embed = Embed(
                    title=f"INTERCEPTION",
                    colour=discord.Colour.blue(),
                    description=event.play.text
                )
                embed.set_footer(text=event.play.play_id)
                return await self.gdt_channel.send(embed=embed)
            if event.play.play_type.type_id == '29':
                embed = Embed(
                    title=f"FUMBLE RECOVERY",
                    colour=discord.Colour.blue(),
                    description=event.play.text
                )
                embed.set_footer(text=event.play.play_id)
                return await self.gdt_channel.send(embed=embed)
        if event.play.play_type.abbreviation == "EP":
            embed = Embed(
                title=f"{event.play.text}",
                colour=discord.Colour.blue()
            )
            embed.set_footer(text=event.play.play_id)
            return await self.gdt_channel.send(embed=embed)

    async def get_game_summary(self) -> Summary:
        url = (
            f'https://site.web.api.espn.com/apis/site/v2/sports/'
            f'football/nfl/summary?event={self.game.id}'
        )
        logger.info("Getting game summary from api: %s", url)
        async with self.bot.web_client.get(url) as response:
            r = (await response.json())
            summary = Summary(**r)
        return summary

    async def sleep_until_thread(self):
        current_datetime = datetime.now(UTC)
        thread_start = self.game.date - self.channel_update_delta
        if current_datetime < self.game.date and current_datetime < thread_start:
            sleep_seconds = (thread_start - current_datetime).seconds
            await asyncio.sleep(sleep_seconds + 180)
            await self.sleep_until_thread()

    async def sleep_until_game_start(self):
        current_datetime = datetime.now(UTC)
        if current_datetime <= self.game.date:
            sleep_seconds = (self.game.date - current_datetime).seconds
            logging.info("Sleeping %s seconds until game start...", sleep_seconds)
            await asyncio.sleep(sleep_seconds + 180)
            await self.sleep_until_game_start()

    async def check_game_status(self) -> bool:
        url = ("https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/"
               f"{self.game.id}/competitions/{self.game.id}/status")
        logger.info("Getting game status from api: %s", url)
        async with self.bot.web_client.get(url) as response:
            r = (await response.json())["type"]
            status = StatusType(**r)
        if status.name == "STATUS_FINAL":
            logger.info("Game is over..")
            return True
        logger.info("Game is still ongoing..")
        return False
