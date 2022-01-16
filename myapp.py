from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from time import sleep
import requests
import urllib3
import json
import logging
import config
import re
import os

REQUESTS_LIMIT = 20
DELAY_IN_SECONDS = 0.1

app = Flask(__name__)
user = os.getenv('DB_LOGIN', default = config.DB_LOGIN)
password = os.getenv('DB_PASSWORD', default = config.DB_PASSWORD)
host = os.getenv('DB_HOST', default = config.DB_HOST)
dbname = os.getenv('DB_NAME', default = config.DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'mysql+pymysql://{user}:{password}@{host}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Planet(db.Model):
  __tablename__ = 'planet'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text)
  rotation_period = db.Column(db.Integer)
  orbital_period = db.Column(db.Integer)
  diameter     = db.Column(db.Integer)
  climate      = db.Column(db.Text)
  gravity      = db.Column(db.Text)
  terrain      = db.Column(db.Text)
  surface_water = db.Column(db.Text)
  population   = db.Column(db.BigInteger)
  created_date = db.Column(db.DateTime)
  updated_date = db.Column(db.DateTime)
  url          = db.Column(db.Text)
  people       = db.relationship('Person', backref='planet', lazy='dynamic')

  def __repr__(self):
    return '<Planet %r>' % self.name

class Person(db.Model):
  __tablename__ = 'people'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.Text)
  height       = db.Column(db.Integer)
  mass         = db.Column(db.Float)
  hair_color   = db.Column(db.Text)
  skin_color   = db.Column(db.Text)
  eye_color    = db.Column(db.Text)
  birth_year   = db.Column(db.Text)
  gender       = db.Column(db.Text)
  planet_id    = db.Column(db.Integer, db.ForeignKey('planet.id'))
  created_date = db.Column(db.DateTime)
  updated_date = db.Column(db.DateTime)
  url          = db.Column(db.Text)

  def __repr__(self):
    return '<Person %r>' % self.name

@app.route('/')
def index():
  planet_list = Planet.query.all()
  return render_template('planet-list.html', planetList = planet_list)

@app.route('/health')
def health():
  return json.dumps({'healthy':True}), 200, {'ContentType':'application/json'} 
  
@app.route('/planet/<id>')
def planet(id):
  current_planet = Planet.query.filter_by(id=id).first()
  character_list = current_planet.people.all()
  return render_template('character-list.html', planet = current_planet, characterList = character_list)

@app.route('/test_clear_data')
def clear():
  recreate_tables()
  return render_template('cleared.html')

@app.route('/test_fill_data')
def fill():
  fill_tables()
  return render_template('filled.html')

def get_json(url):
  logging.warning(f"Fetching {url}")
  sleep(DELAY_IN_SECONDS)
  return requests.get(url, verify=False).json()

def disable_ssl_warnings():
  urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def insert_planet(planet):
  planet_obj = Planet(
    id = re.search(r'/planets/(\d+)/', planet['url']).group(1),
    name = planet['name'],
    rotation_period = planet['rotation_period'],
    orbital_period = planet['orbital_period'],
    diameter = planet['diameter'],
    climate = planet['climate'],
    gravity = planet['gravity'],
    terrain = planet['terrain'],
    surface_water = planet['surface_water'],
    population = planet['population'],
    created_date = planet['created'][:-1],
    updated_date = planet['edited'][:-1],
    url = planet['url'],
  )
  logging.warning(planet_obj.created_date)
  db.session.add(planet_obj)

def insert_person(person):
  person_obj = Person(
    id = re.search(r'/people/(\d+)/', person['url']).group(1),
    name = person['name'],
    height = person['height'],
    mass = person['mass'].replace(',', ''),
    hair_color = person['hair_color'],
    skin_color = person['skin_color'],
    eye_color = person['eye_color'],
    birth_year = person['birth_year'],
    gender = person['gender'],
    planet_id = re.search(r'/planets/(\d+)/', person['homeworld']).group(1),
    created_date = person['created'][:-1],
    updated_date = person['edited'][:-1],
    url = person['url']
  )
  logging.warning(person_obj.created_date)
  db.session.add(person_obj)

def parse_planets():
  requests_counter = 0
  next_url = "https://swapi.dev/api/planets/"
  while next_url and requests_counter < REQUESTS_LIMIT:
    planets_json = get_json(next_url)
    requests_counter += 1
    for planet in planets_json['results']:
      insert_planet(planet)
    next_url = planets_json['next']
  db.session.commit()

def parse_people():
  requests_counter = 0
  next_url = "https://swapi.dev/api/people/"
  while next_url and requests_counter < REQUESTS_LIMIT:
    people_json = get_json(next_url)
    requests_counter += 1
    for person in people_json['results']:
      insert_person(person)
    next_url = people_json['next']
  db.session.commit()

def recreate_tables():
  db.drop_all()
  db.create_all()

def fill_tables():
  disable_ssl_warnings()
  parse_planets()
  parse_people()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
