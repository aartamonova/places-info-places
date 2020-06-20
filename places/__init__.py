from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

api = Api(app)

from places.places_resource import PlaceListResource, PlaceAddResource, PlaceResource, PlaceSearchResource

api.add_resource(PlaceResource, '/places/<int:place_id>')
api.add_resource(PlaceListResource, '/places')
api.add_resource(PlaceAddResource, '/places')
api.add_resource(PlaceSearchResource, '/places/search')

# Migration
from places import places_model
