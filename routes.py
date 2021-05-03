from app import app, db
from models import Player, Team
from flask import request, render_template, flash, redirect, url_for

@app.route('/')
def index():
    top_forwards = db.session.query(Player).filter_by(position="FW").order_by(Player.xGi.desc()).limit(10)
    top_midfielders = db.session.query(Player).filter_by(position="MF").order_by(Player.xGi.desc()).limit(10)
    top_defenders = db.session.query(Player).filter_by(position="DF").order_by(Player.xGi.desc()).limit(10)
    players = {
        "Top 10 Forwards" : top_forwards,
        "Top 10 Mids" : top_midfielders,
        "Top 10 Defenders" : top_defenders
    }
    top_teams = db.session.query(Team).order_by(Team.xGa.asc()).limit(5)
    return render_template('index.html', players=players, teams=top_teams)

@app.route('/player/<player_id>')
def player(player_id):
    player = Player.query.get(player_id)
    # list of tuplets, match ID + against
    """ home_or_away = []
    for performance in player.performances: """

    return render_template('player.html', player=player)