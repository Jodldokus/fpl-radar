from app import app, db

from flask import request, render_template, flash, redirect, url_for

@app.route('/')
def index():
    return render_template('index.html', players=['kebim sbacey', 
    'capitano anoose', 'arschlecken'])