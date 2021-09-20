
import asyncio
import json
import aiohttp
import time

from app import db
from understat import Understat
from models import Player, Match, Team, Performance
from sqlalchemy import or_
from datetime import date
from fpl import FPL

async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        fpl = FPL(session)

        if not db.session.query(Player).first():
            # 1. initialise teams
            
            await init_teams(understat)
            # 2. initialise players
            await init_players(understat, fpl)

        # 1. initialise current matches
        await init_matches(understat)
        # 2. initialise player performances
        await init_performances(understat)
        
        

async def init_teams(understat):
    # get PL teams into DB
    teams = await understat.get_teams("epl", 2021)
    for team in teams:
        new_team = Team(name=team["title"])
        db.session.add(new_team)
    return db.session.commit()

async def init_players(understat, fpl):
    # get all PL players into DB
    players = await understat.get_league_players("epl", 2021)
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
    # add FPL positions from FPL api
    await get_player_positions(fpl)
    return db.session.commit()

async def get_player_positions(fpl):
    fpl_players = await fpl.get_players()
    for player in fpl_players:
        player_like_query = Player.query.filter(Player.name.like(f"%{player.web_name}%")).all()
        if player_like_query:
            for db_player in player_like_query:
                if db_player.team.name == get_team_name(player.team):
                    db_player.position = get_position(player.element_type)
    players = Player.query.filter(Player.position==None).all()
    for player in players:
        player.position = input(f"{player.name} of {player.team}?")
        


    return db.session.commit()

async def init_matches(understat, x=3):
    # get recent matches 
    teams = db.session.query(Team).all()
    for team in teams:
        start_time=time.time()
        fixtures = await understat.get_team_results(team.name, 2021)
        fixtures = fixtures[-x:] 
        print(f"getting team results took {time.time()-start_time}s")
        for fixture in fixtures:
            start_time = time.time()
            is_in_db = db.session.query(Match).filter_by(home_team_id=get_team_id(fixture['h']['title']), away_team_id=get_team_id(fixture['a']['title'])).first()
            print(f"is match in db query takes {time.time()-start_time}s")
            if is_in_db:
                # if match is in db already, continue
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
    team = db.session.query(Team).filter_by(name=name).first()
    if not team:
        return 420
    return team.id

def get_position(id):
    positions = {
        1 : "GK",
        2 : "DF",
        3 : "MF",
        4 : "FW"
    }
    return positions[id]

def get_team_name(id):
    id_to_team_name = {
        1 : "Arsenal", 2 : "Aston Villa",3 : "Brentford",4 : "Brighton",5 : "Burnley",6 : "Chelsea",7 : "Crystal Palace",8 : "Everton",9 : "Leicester",10 : "Leeds",11 : "Liverpool",12 : "Manchester City",13 : "Manchester United",14 : "Newcastle United",15 : "Norwich",16 : "Southampton",17 : "Tottenham",18 : "Watford",19 : "West Ham",20 : "Wolverhampton Wanderers"
    }
    return id_to_team_name[id]

async def init_performances(understat):
    # 1. delete stored performances
    if db.session.query(Performance).first():
        db.session.query(Performance).delete()

    recent_matches = {}
    for team in db.session.query(Team).all():
        recent_matches[team.id] = get_x_latest_results(team.id)

    # 2. iterate through players:
    #    1. get past player performances
    for player in db.session.query(Player).all():
      
        player_matches = await understat.get_player_matches(player.id)
        player_matches = player_matches[:3]
        
        #    2. set player performances equal to teams matches

        if player_matches[0]['date'] < recent_matches[player.team_id][0].date:
            for match in recent_matches[player.team_id]:
                new_performance = Performance(
                    player_id=player.id,
                    match_id=match.id,
                )
                db.session.add(new_performance)
            print(f"{player.name} no feature recently")
            continue
        
        for match in recent_matches[player.team_id]:
            # if this match equals a match in most recent player performances, 
            # add player stats to performance, else fill as blank
            featured = player_featured(match, player_matches)
            if featured:
                new_performance = Performance(
                    player_id=player.id,
                    match_id=match.id,
                    xG=featured["xG"],
                    xA=featured["xA"],
                    time=featured["time"],
                    shots=featured["shots"],
                    key_passes=featured["key_passes"],
                    goals=featured["goals"],
                    assists=featured["assists"],
                    npg = featured["npg"],
                    npxG = featured["npxG"]
                )
            else:
                new_performance = Performance(
                    player_id=player.id,
                    match_id=match.id
                )
            db.session.add(new_performance)
    return db.session.commit()
                
            
        

def player_featured(match, player_matches):
        # returns true if player did feature in specified match
        for played_match in player_matches:
            # for each match the player has played, 
            # check if it is equal to the provided match,
            # i. e. that home and away teams are equal 
            
            if get_team_id(played_match["h_team"]) == match.home_team_id and get_team_id(played_match["a_team"]) == match.away_team_id:
                return played_match
        return False

def get_x_latest_results(team_id, x=3):
    team_matches = db.session.query(Match).filter(or_(Match.home_team_id==team_id, Match.away_team_id==team_id)).all()
    team_matches.sort(key=lambda match: match.date)
    return team_matches[-x:]

def populate_db():
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    middle_time = time.time()
    print(f"main loop takes {middle_time-start_time}s")
    for player in db.session.query(Player):
        player.calc_xgi()
    for team in db.session.query(Team):
        team.calc_xGa()
    end_time = time.time()
    print(f"player xgi and team xga calculation take {end_time-middle_time}")
    db.session.commit()

if __name__ == '__main__':
    populate_db()