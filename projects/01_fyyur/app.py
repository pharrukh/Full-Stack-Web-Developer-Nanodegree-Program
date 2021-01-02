#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
Flask,
render_template,
request,
Response,
flash,
redirect,
url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import contains_eager
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from datetime import datetime, timedelta
from collections import defaultdict
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # print(value)
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues_with_area = db.session.query(Venue.state, Venue.city, Venue).all()
  for _, _, venue in venues_with_area:
    num_upcoming_shows = [show for show in venue.shows if show.start_datetime > datetime.now()]
    setattr(venue, 'num_upcoming_shows', len(num_upcoming_shows))
  dictionary = defaultdict(list)
  for state, city, venue in venues_with_area:
    dictionary[f'{state} {city}'].append(venue)
  areas = [{'name':name, 'venues':venues} for name, venues in dictionary.items()]
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  
  for venue in venues:
    num_upcoming_shows = [show for show in venue.shows if show.start_datetime > datetime.now()]
    setattr(venue, 'num_upcoming_shows', len(num_upcoming_shows))

  response = {
    "count": len(venues),
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  setattr(venue, 'upcoming_shows', [show for show in venue.shows if show.start_datetime > datetime.now()])
  setattr(venue, 'past_shows', [show for show in venue.shows if show.start_datetime < datetime.now()])
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  name = request.form['name']

  try:
    venue = Venue()
    form = VenueForm()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash(f'An error occurred. Venue {name} could not be listed.')
    else:
      flash(f"Venue {name} was successfully listed!")

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.with_entities(Artist.id, Artist.name))

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response = {
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  past_shows = [show for show in artist.shows if show.start_datetime < datetime.now()]
  setattr(artist, 'past_shows', past_shows)
  setattr(artist, 'past_shows_count', len(past_shows))

  upcoming_shows = [show for show in artist.shows if show.start_datetime > datetime.now()]
  setattr(artist, 'upcoming_shows', upcoming_shows)
  setattr(artist, 'upcoming_shows_count', len(upcoming_shows))

  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(
    name=artist.name,
    city=artist.city,
    state=artist.state,
    phone=artist.phone,
    image_link=artist.image_link,
    genres=artist.genres,
    facebook_link=artist.facebook_link)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.populate_obj(artist)
  db.session.add(artist)
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(
    name=venue.name,
    city=venue.city,
    state=venue.state,
    address=venue.address,
    phone=venue.phone,
    image_link=venue.image_link,
    genres=venue.genres,
    facebook_link=venue.facebook_link,
    website=venue.website,
    seeking_talent=venue.seeking_talent,
    seeking_description=venue.seeking_description
  )
  return render_template('forms/edit_venue.html', form=form, venue=Venue.query.get(venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  print(request.form['action'])

  if request.form['action'] == 'delete':
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    return render_template('pages/home.html')

  elif request.form['action'] == 'edit':
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

  return render_template('pages/home.html')

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = NewArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  name = request.form['name']

  try:
    artist = Artist()
    form = NewArtistForm()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash(f'An error occurred. Artist {name} could not be listed.')
    else:
      flash(f"Artist {name} was successfully listed!")

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = (db.session.query(Show.start_datetime,
                            Artist.id.label('artist_id'), 
                            Artist.name.label('artist_name'), 
                            Artist.image_link.label('artist_image_link'),
                            Venue.id.label('venue_id'),
                            Venue.name.label('venue_name')
  ).join(Artist)
   .join(Venue)).all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False

  try:
    show = Show()
    form = NewShowForm()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash(f'An error occurred. Show could not be listed.')
    else:
      flash(f"Show was successfully listed!")

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(401)
def server_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def server_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(422)
def server_error(error):
    return render_template('errors/422.html'), 422

@app.errorhandler(405)
def server_error(error):
    return render_template('errors/405.html'), 405

@app.errorhandler(409)
def server_error(error):
    return render_template('errors/405.html'), 409

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
