from app import app, db
from models import Player
from flask import request, render_template, flash, redirect, url_for

@app.route('/')
def index():
    top_players = db.session.query(Player).order_by(Player.xgi.desc()).limit(10)
    return render_template('index.html', players=top_players)

@app.route('/player/<player_id>')
def player(player_id):
    player = Player.query.get(player_id)
    return render_template('player.html', player=player)