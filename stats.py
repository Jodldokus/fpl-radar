
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
            
            # add players to DB
            init_players(players)

        # update matches
        await update_player_matches(understat)

def init_players(players):
    # 1. add players to db, clean up team names
    for player in players:
        # 1. splits team names if necessary
        if ',' not in player['team_title']:
            team_title = player['team_title']
        else:
            team_one, team_two = player['team_title'].split(',')
            print(f"{player['player_name']} in {team_one} (1) or {team_two} (2)?")
            decision = input("Enter 1 or 2: ")
            if decision == "1":
                team_title = team_one
            elif decision == "2":
                team_title = team_two
        new_player = Player(id=player['id'], name=player['player_name'], team=team_title)
        # 2. adds player to db
        db.session.add(new_player)

async def update_player_matches(understat):
    players = db.session.query(Player).all()
    teams = await get_teams(understat)
    results = await get_last_x_results(understat, teams)

    for player in players:

        # 1. if player has matches in DB, delete matches
        if db.session.query(Match).filter_by(player_id=player.id).first():
            db.session.query(Match).filter_by(player_id=player.id).delete()
        # 2. add last team matches to players Matches
        for result in results[player.team]:
            team_match = Match(h_team=result['h'], a_team=result['a'], date=result['date'], player=player)
            db.session.add(team_match)
        # 3. get last player matches, check if equal to team matches
        player_matches = await understat.get_player_matches(player.id, season="2020")
        player_matches = player_matches[:3]
        team_matches = db.session.query(Match).filter_by(player_id=player.id).all()
        for player_match in player_matches:
            for team_match in team_matches:
                if player_match['date'] == team_match.date:
                    team_match.xG = player_match['xG']
                    team_match.xA = player_match['xA']
                    team_match.key_passes = player_match['key_passes']
                    team_match.goals = player_match['goals']
                    team_match.assists = player_match['assists']
                    team_match.npg = player_match['npg']
                    team_match.npxG = player_match['npxG']
                    db.session.commit()
                    break

    return db.session.commit()

async def get_teams(understat):
    table = await understat.get_league_table("epl", 2020)
    table = table[1:]
    teams = []
    for team in table:
        teams.append(team[0])
    return teams
    
async def get_last_x_results(understat, teams,x=3 ):
    # takes amount of matches to consider as x as argument
    #
    # returns dictionary { 'Team Name' : [{ 'h' : 'some team', 'a' : 'some team' 
    #                                       'date' : '21-02-02'}, 
    #                                    [{ 'h' : 'some other team' ...}]] }
    last_x = {}
    for team in teams:
        fixtures = await understat.get_team_results(team, 2020)
        fixtures = fixtures[-x:] # get last x results
        dates = []
        for fixture in fixtures:
            result = {}
            result['h'] = fixture['h']['title']
            result['a'] = fixture['a']['title']
            result['date'] = fixture['datetime'][:10]
            dates.append(result)
        last_x[team] = dates
    return last_x

def populate_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    for player in db.session.query(Player):
        player.calc_xgi()
    db.session.commit()

if __name__ == '__main__':
    populate_db()