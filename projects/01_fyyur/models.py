from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue_shows', lazy=True)
    create_at = db.Column(db.DateTime)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist_shows', lazy=True)
    create_at = db.Column(db.DateTime)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)

    artist = db.relationship("Artist", backref='Artist', lazy=True)
    venue = db.relationship("Venue", backref='Venue', lazy=True)

    def __repr__(self):
      return f'{self.id}\n{self.start_datetime}\n'
