import os

root_dir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Database settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(root_dir, 'places_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Services settings
    AUTH_SERVICE_URL = 'https://places-info-auth.herokuapp.com'

    # Other settings
    SOURCE_APP = 'gui'
    REQUEST_APP = 'places'
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True
