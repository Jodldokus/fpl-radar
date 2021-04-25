from app import db

class Player(db.Model):
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
        return f"{self.player_id}"