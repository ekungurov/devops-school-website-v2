from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import config
import os

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
  planetList = Planet.query.all()
  return render_template('planet-list.html', planetList = planetList)
  
@app.route('/planet/<id>')
def planet(id):
  current_planet = Planet.query.filter_by(id=id).first()
  characterList = current_planet.people.all()
  return render_template('character-list.html', planet = current_planet, characterList = characterList)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
