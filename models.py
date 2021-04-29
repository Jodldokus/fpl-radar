from app import db


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    team_id = db.Column(db.ForeignKey('team.id'))
    position = db.Column(db.String(2), index=True)
    xGi = db.Column(db.Float, index=True)
    performances = db.relationship('Performance', backref="player", lazy="dynamic")

    def calc_xgi(self):
        self.xGi = 0
        for performance in self.performances:
            if performance.xG:
                self.xGi += performance.xG + performance.xA

    def __repr__(self):
        return f"{self.name} of {self.team}"

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)
    xGa = db.Column(db.Float, index=True)
    players = db.relationship('Player', backref="team", lazy="dynamic")
    

    def __repr__(self):
        return f"{self.name}"

    def calc_xGa(self):
        from stats import get_x_latest_results
        self.xGa = 0 
        latest_results = get_x_latest_results(self.id)
        for match in latest_results:
            if match.home_team_id == self.id:
                self.xGa += match.xG_away
                continue
            self.xGa += match.xG_home
        return True
            


  

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    home_team = db.relationship('Team', foreign_keys=[home_team_id])
    away_team = db.relationship('Team', foreign_keys=[away_team_id])
    xG_home = db.Column(db.Float)
    xG_away = db.Column(db.Float)
    date = db.Column(db.String(10))
    performances = db.relationship('Performance', backref="match", lazy="dynamic")

    def __repr__(self):
        return f"{self.home_team} : {self.away_team}, {self.date}"


class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))

    xG = db.Column(db.Float, index=True)
    xA = db.Column(db.Float, index=True)
    time = db.Column(db.Integer, index=True)
    key_passes = db.Column(db.Integer, index=True)
    goals = db.Column(db.Integer, index=True)
    assists = db.Column(db.Integer, index=True)
    npg = db.Column(db.Integer, index=True)
    npxG = db.Column(db.Float, index=True)

    def __repr__(self):
        return f"{self.player_id in self.match_id}"


""" class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    matches = db.relationship('Match', backref='player', lazy='dynamic')
    xgi = db.Column(db.Float, index = True)
    team = db.Column(db.String(40), index=True)

    def __repr__(self):
        return f"{self.name}"

    def calc_xgi(self):
        self.xgi = 0.0
        for match in self.matches:
            if match.xG:
                self.xgi += match.xG + match.xA
        print(f"{self.name} has an xGi of {self.xgi}")

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    

    def __repr__(self):
        return f"{self.name}"

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    xG = db.Column(db.Float, index=True)
    xA = db.Column(db.Float, index=True)
    time = db.Column(db.Integer, index=True)
    h_team = db.Column(db.String(40), index=True)
    a_team = db.Column(db.String(40), index=True)
    date = db.Column(db.String(10), index=True)
    key_passes = db.Column(db.Integer, index=True)
    goals = db.Column(db.Integer, index=True)
    assists = db.Column(db.Integer, index=True)
    npg = db.Column(db.Integer, index=True)
    npxG = db.Column(db.Float, index=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    def __repr__(self):
        return f"{self.player_id}" """