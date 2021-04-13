
import asyncio
import json
import aiohttp

from app import db
from understat import Understat
from models import Player, Match


async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        if db.session.query(Player).first() == None:
            # if players aren't yet in the database, get them 
            players = await understat.get_league_players("epl", 2020)
            for player in players:
                # get matches for every player, add to database
                new_player = Player(id=player['id'], name=player['player_name'], team=player['team_title'])
                db.session.add(new_player)
                await update_player_matches(new_player.id, understat=understat)
        else:
            # if there are players, just update matches without downloading players again
            players = db.session.query(Player)
            db.session.query(Match).delete()
            for player in players:
                await update_player_matches(id=player.id, understat=understat)

async def update_player_matches(id, understat):
    # takes players id as argument, adds relevant matches to db
    player_matches = await understat.get_player_matches(id, season="2020")
    player_matches = player_matches[:3]
    for match in player_matches:
        #match_player = 
        new_match = Match(xG=match['xG'], 
            xA=match['xA'], time=match['time'], 
            h_team=match['h_team'], a_team=match['a_team'], 
            date=match['date'], key_passes=match['key_passes'], 
            goals=match['goals'], assists=match['assists'], 
            npg=match['npg'], npxG=match['npxG'], player=db.session.query(Player).filter_by(id=id).first())
        db.session.add(new_match)
    return db.session.commit()
            
def populate_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    for player in db.session.query(Player):
        player.calc_xgi()
    db.session.commit()

if __name__ == '__main__':
    populate_db()