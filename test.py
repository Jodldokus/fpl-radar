import asyncio
import aiohttp
from fpl import FPL
from app import db
from models import Player
from stats import get_player_positions

id_to_team_name = {
    1 : "Arsenal",
    2 : "Aston Villa",
    3 : "Brighton",
    4 : "Burnley",
    5 : "Chelsea",
    6 : "Crystal Palace",
    7 : "Everton",
    8 : "Fulham",
    9 : "Leicester",
    10 : "Leeds",
    11 : "Liverpool",
    12 : "Manchester City",
    13 : "Manchester United",
    14 : "Newcastle United",
    15 : "Sheffield United",
    16 : "Southampton",
    17 : "Tottenham",
    18 : "West Bromwich Albion",
    19 : "West Ham",
    20 : "Wolverhampton Wanderers"
}

async def main():
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        await get_player_positions(fpl)

        


asyncio.run(main())