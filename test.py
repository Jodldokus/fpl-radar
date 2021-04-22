import asyncio
import json

import aiohttp

from understat import Understat

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        fixtures = await understat.get_league_results(
            "epl", 2020
        )
        print(json.dumps(fixtures))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())