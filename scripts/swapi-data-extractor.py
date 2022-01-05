import requests
import urllib3
import json
import logging
import config
import re
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, BigInteger, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

REQUESTS_LIMIT = 20
SQLALCHEMY_DATABASE_URI = \
    'mysql+pymysql://{user}:{password}@{host}/{dbname}'.format( \
    user = config.DB_LOGIN, password = config.DB_PASSWORD, \
    host = config.DB_HOST, dbname = config.DB_NAME)
session = None
Base = declarative_base()

def get_json(url):
  logging.warning(f"Fetching {url}")
  return requests.get(url, verify=False).json()

def disable_ssl_warnings():
  urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Planet(Base):
  __tablename__ = 'planet'
  id = Column(Integer, primary_key=True)
  name = Column(Text)
  rotation_period = Column(Integer)
  orbital_period = Column(Integer)
  diameter     = Column(Integer)
  climate      = Column(Text)
  gravity      = Column(Text)
  terrain      = Column(Text)
  surface_water = Column(Text)
  population   = Column(BigInteger)
  created_date = Column(DateTime)
  updated_date = Column(DateTime)
  url          = Column(Text)
  people       = relationship('Person', backref='planet', lazy='dynamic')

  def __repr__(self):
    return '<Planet %r>' % self.name

class Person(Base):
  __tablename__ = 'people'
  id = Column(Integer, primary_key=True)
  name = Column(Text)
  height       = Column(Integer)
  mass         = Column(Float)
  hair_color   = Column(Text)
  skin_color   = Column(Text)
  eye_color    = Column(Text)
  birth_year   = Column(Text)
  gender       = Column(Text)
  planet_id    = Column(Integer, ForeignKey('planet.id'))
  created_date = Column(DateTime)
  updated_date = Column(DateTime)
  url          = Column(Text)

  def __repr__(self):
    return '<Person %r>' % self.name

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
    created_date = planet['created'],
    updated_date = planet['edited'],
    url = planet['url'],
  )
  session.add(planet_obj)
  session.commit()

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
    created_date = person['created'],
    updated_date = person['edited'],
    url = person['url']
  )
  session.add(person_obj)
  session.commit()

def parse_planets():  
  requests_counter = 0
  next_url = "https://swapi.dev/api/planets/"
  while next_url and requests_counter < REQUESTS_LIMIT:
    planets_json = get_json(next_url)
    requests_counter += 1
    for planet in planets_json['results']:
      insert_planet(planet)
    next_url = planets_json['next']

def parse_people():
  requests_counter = 0
  next_url = "https://swapi.dev/api/people/"
  while next_url and requests_counter < REQUESTS_LIMIT:
    people_json = get_json(next_url)
    requests_counter += 1
    for person in people_json['results']:
      insert_person(person)
    next_url = people_json['next']

def main():
  global session
  engine = create_engine(SQLALCHEMY_DATABASE_URI)
  Session = sessionmaker(bind=engine)
  session = Session()
  #Base.metadata.create_all(engine)
  disable_ssl_warnings()
  parse_planets()
  parse_people()

if __name__ == "__main__":
  main()
