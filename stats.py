
import asyncio
import json
import aiohttp

from app import db
from understat import Understat
from models import Player, Match, Team, Performance
from sqlalchemy import or_
from datetime import date

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        if db.session.query(Player).first() == None:
            # 1. initialise teams
            if not db.session.query(Team).first():
                await init_teams(understat)
            # 2. initialise players
            await init_players(understat)

        # 1. initialise current matches
        await init_matches(understat)
        # 2. initialise player performances
        await init_performances(understat)
        

async def init_teams(understat):
    # get PL teams into DB
    teams = await understat.get_teams("epl", 2020)
    for team in teams:
        new_team = Team(name=team["title"])
        db.session.add(new_team)
    return db.session.commit()

async def init_players(understat):
    # get all PL players into DB
    players = await understat.get_league_players("epl", 2020)
    for player in players:
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
        new_player = Player(id=player['id'], name=player['player_name'], team=db.session.query(Team).filter_by(name=team_title).first())
        # 2. adds player to db
        db.session.add(new_player) 
    return db.session.commit()

async def init_matches(understat, x=3):
    # get recent matches 
    teams = db.session.query(Team).all()
    for team in teams:
        fixtures = await understat.get_team_results(team.name, 2020)
        fixtures = fixtures[-x:] 
        for fixture in fixtures:
            if db.session.query(Match).filter_by(home_team_id=get_team_id(fixture['h']['title']), away_team_id=get_team_id(fixture['a']['title'])).first():
                continue
            new_match = Match(
                home_team = db.session.query(Team).filter_by(name=fixture['h']['title']).first(),
                away_team = db.session.query(Team).filter_by(name=fixture['a']['title']).first(),
                xG_home = fixture['xG']['h'],
                xG_away = fixture['xG']['a'],
                date = fixture['datetime'][:10]
            )
            db.session.add(new_match)
    return db.session.commit()

def get_team_id(name):
    return db.session.query(Team).filter_by(name=name).first().id

def get_performance_date(match_id):
    return db.session.query(Match).filter_by(id=match_id).first().date

async def init_performances(understat):
    # 1. delete stored performances
    if db.session.query(Performance).first():
        db.session.query(Performance).all().delete()

    # 2. iterate through players:
    #    1. get past player performances
    for player in db.session.query(Player).all():
        player_matches = await understat.get_player_matches(player.id)
        #    2. set player performances equal to teams matches
        team_matches = get_x_latest_results(player.team_id)
        for match in team_matches:
            new_performance = Performance(
                player_id=player.id,
                match_id=match.id,
            )
            db.session.add(new_performance)
        #    3. iterate over past player performances:
        for match in player_matches:
            for performance in player.performances:
                if match['date'] == get_performance_date(performance.match_id):
                    performance.xG = match['xG']
                    performance.xA = match['xA']
                    performance.time = match['time']
                    performance.key_passes = match['key_passes']
                    performance.goals = match['goals']
                    performance.assists = match['assists']
                    performance.npg = match['npg']
                    performance.npxG = match['npxG']
                    db.session.commit()
                    break

    #       - if past player performance == player performance,
    #         update player performance data
   


    # 3. add into db, provided they are up to date

def get_x_latest_results(team_id, x=3):
    team_matches = db.session.query(Match).filter(or_(Match.home_team_id==team_id, Match.away_team_id==team_id)).all()
    team_matches.sort(key=lambda match: match.date)
    return team_matches[-x:]

""" def init_players(players):
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
    return last_x """

def populate_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    for player in db.session.query(Player):
        player.calc_xgi()
    for team in db.session.query(Team):
        team.calc_xGa()
    db.session.commit()

if __name__ == '__main__':
    populate_db()