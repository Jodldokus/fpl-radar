from app import app, db
from models import Player, Team
from flask import request, render_template, flash, redirect, url_for

@app.route('/')
def index():
    top_players = db.session.query(Player).order_by(Player.xGi.desc()).limit(10)
    top_teams = db.session.query(Team).order_by(Team.xGa.asc()).limit(5)
    return render_template('index.html', players=top_players, teams=top_teams)

@app.route('/player/<player_id>')
def player(player_id):
    player = Player.query.get(player_id)
    # list of tuplets, match ID + against
    """ home_or_away = []
    for performance in player.performances: """

    return render_template('player.html', player=player)