import asyncio
from understat import Understat
import json
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        player_matches = await understat.get_player_matches(8720, season="2020")
        print(player_matches)
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

