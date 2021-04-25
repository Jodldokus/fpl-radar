
import asyncio
import json
import aiohttp

from app import db
from understat import Understat
from models import Player, Match


async def main():
    async with aiohttp.ClientSession() as session:
        understat = Understat(session)
        # 1. get teams
        teams = await get_teams(understat)
        # 2. get last three results for each team
        last_x_results = await get_last_x_results(understat, teams)
        if db.session.query(Player).first() == None:
            # if players aren't yet in the database, get them 
            players = await understat.get_league_players("epl", 2020)
            for player in players:
                # get matches for every player, add to database
                if ',' not in player['team_title']:
                    new_player = Player(id=player['id'], name=player['player_name'], team=player['team_title'])
                else:
                    team_one, team_two = player['team_title'].split(',')
                    print(f"{player['player_name']} in {team_one} (1) or {team_two} (2)?")
                    decision = input("Enter 1 or 2: ")
                    if decision == "1":
                        player_team = team_one
                    elif decision == "2":
                        player_team = team_two
                    new_player = Player(id=player['id'], name=player['player_name'], team=player_team)
                db.session.add(new_player)
                await update_player_matches(id=new_player.id, understat=understat, last_x=last_x_results, player_team=new_player.team)
        else:
            # if there are players, update matches
            players = db.session.query(Player)
            db.session.query(Match).delete()
            for player in players:
                await update_player_matches(id=player.id, understat=understat, last_x=last_x_results, player_team=player.team)

async def update_player_matches(id, understat, last_x, player_team):
    # takes players id as argument, adds relevant matches to db
    player_matches = await understat.get_player_matches(id, season="2020")
    player_matches = player_matches[:3]
    player_matches.reverse()
    
    for x in range(len(player_matches)):
        match = player_matches[x]
        team_match = last_x[player_team][x]
        if check_date(match['date'], last_x, player_team):
            # if current match is in last x results of team, add match data
            new_match = Match(xG=match['xG'], 
                xA=match['xA'], time=match['time'], 
                h_team=match['h_team'], a_team=match['a_team'], 
                date=match['date'], key_passes=match['key_passes'], 
                goals=match['goals'], assists=match['assists'], 
                npg=match['npg'], npxG=match['npxG'], player=db.session.query(Player).filter_by(id=id).first())
            
        else:
            # if it is not, add "empty" match with only home and away teams
            new_match = Match(h_team=team_match['h'], a_team=team_match['a'],
            date=team_match['date'], player=db.session.query(Player).filter_by(id=id).first())
    
        db.session.add(new_match)
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
            print(fixture)
            result['h'] = fixture['h']['title']
            result['a'] = fixture['a']['title']
            result['date'] = fixture['datetime'][:10]
            dates.append(result)
        last_x[team] = dates
    print(last_x)
    return last_x

def check_date(date, team_dates, team):
    for fixture in team_dates[team]:
        if fixture['date'] == date:
            return True
    return False

def populate_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    for player in db.session.query(Player):
        player.calc_xgi()
    db.session.commit()

if __name__ == '__main__':
    populate_db()