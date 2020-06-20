import functools
import json
import logging

import requests
from flask import request, make_response, jsonify
from flask_api.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_400_BAD_REQUEST, \
    HTTP_403_FORBIDDEN
from flask_restful import fields, marshal, Resource

from config import Config
from places.places_model import PlaceData

place_fields = {'id': fields.Integer,
                'name': fields.String,
                'type': fields.String,
                'description': fields.String,
                'phone': fields.String,
                'address': fields.String,
                'added_by': fields.String}

place_list_fields = {'count': fields.Integer,
                     'places': fields.List(fields.Nested(place_fields))}

logging.basicConfig(filename="log_data.log", level=logging.WARNING, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def access_token_required(foo):
    @functools.wraps(foo)
    def wrapper(*args, **kwargs):
        if 'Gui-Token' in request.headers:
            access_token = request.headers['Gui-Token']
            # Проверить токен
            try:
                response = requests.get(Config.AUTH_SERVICE_URL + '/token/validate', 'source_app=' +
                                        str(Config.SOURCE_APP) + '&request_app=' + str(Config.REQUEST_APP) +
                                        '&access_token=' + str(access_token))
            except:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            if response.status_code != HTTP_200_OK:
                return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

            return foo(*args, **kwargs)
        else:
            return make_response(jsonify({'error': 'Invalid authorization data'}), HTTP_403_FORBIDDEN)

    return wrapper


class PlaceResource(Resource):
    @staticmethod
    @access_token_required
    def get(place_id):
        place = PlaceData.get_by_id(place_id)
        logging.warning('Поиск места с id %s' % place_id)

        if not place:
            return make_response(jsonify({'error': 'The place with the selected name does not exist'}),
                                 HTTP_404_NOT_FOUND)
        else:
            try:
                content = make_response(marshal(place, place_fields), HTTP_200_OK)
            except:
                return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)

    @staticmethod
    @access_token_required
    def put(place_id):
        place = PlaceData.get_by_id(place_id)
        if not place:
            return make_response(jsonify({'error': 'The place with the selected id does not exist'}),
                                 HTTP_404_NOT_FOUND)

        try:
            args = json.loads(request.data.decode("utf-8"))
        except:
            return make_response(jsonify({'error': 'Invalid place data'}),
                                 HTTP_400_BAD_REQUEST)

        place = PlaceData.edit(place_id, args)
        logging.warning('Редактирование места с id %s' % place_id)

        if not place:
            return make_response(jsonify({'error': 'The place with the selected name already exists'}),
                                 HTTP_400_BAD_REQUEST)
        try:
            content = make_response(marshal(place, place_fields), HTTP_200_OK)
        except:
            return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)
        return make_response(content, HTTP_200_OK)

    @staticmethod
    @access_token_required
    def delete(place_id):
        place = PlaceData.get_by_id(place_id)
        logging.warning('Удаление места с id %s' % place_id)
        if not place:
            return make_response(jsonify({'error': 'The place with the selected id does not exist'}),
                                 HTTP_404_NOT_FOUND)
        else:
            PlaceData.delete(place_id)
            return make_response(jsonify({'message': 'Place was deleted successfully'}), HTTP_200_OK)


class PlaceAddResource(Resource):
    @staticmethod
    @access_token_required
    def post():
        try:
            name = json.loads(request.data.decode("utf-8"))['name']
            place_type = json.loads(request.data.decode("utf-8"))['type']
            description = json.loads(request.data.decode("utf-8"))['description']
            phone = json.loads(request.data.decode("utf-8"))['phone']
            address = json.loads(request.data.decode("utf-8"))['address']
            added_by = json.loads(request.data.decode("utf-8"))['added_by']
        except:
            return make_response(jsonify({'error': 'Invalid place data'}), HTTP_400_BAD_REQUEST)

        place = PlaceData.create(name, place_type, description, phone, address, added_by)
        logging.warning('Создание места с названием %s' % name)

        if not place:
            return make_response(jsonify({'error': 'The place not created'}), HTTP_404_NOT_FOUND)
        else:
            try:
                make_response(marshal(place, place_fields), HTTP_200_OK)
            except:
                return make_response(jsonify({'error': 'Corrupted database data'}), HTTP_500_INTERNAL_SERVER_ERROR)
            return make_response(marshal(place, place_fields), HTTP_200_OK)


class PlaceListResource(Resource):
    @staticmethod
    @access_token_required
    def get():
        page = request.args.get('page', type=int, default=1)
        size = 6
        if page <= 0:
            page = 1

        places = PlaceData.get_all(page, size)
        logging.warning('Просмотр всех мест')
        if not places:
            return make_response(jsonify({'error': 'The place database is empty'}), HTTP_404_NOT_FOUND)
        else:
            try:
                content = marshal({'count': len(places), 'places': [marshal(p, place_fields) for p in places]},
                                  place_list_fields)
            except:
                return make_response({'error': 'Corrupted database data'}, HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)


class PlaceSearchResource(Resource):
    @staticmethod
    @access_token_required
    def get():
        page = request.args.get('page', type=int, default=1)
        name = request.args.get('name', type=str, default='')
        size = 6
        if page <= 0:
            page = 1

        places = PlaceData.search(page, size, name)
        logging.warning('Просмотр мест по запросу %s' % name)
        if not places:
            return make_response(jsonify({'error': 'The place database is empty'}), HTTP_404_NOT_FOUND)
        else:
            try:
                content = marshal({'count': len(places), 'places': [marshal(p, place_fields) for p in places]},
                                  place_list_fields)
            except:
                return make_response({'error': 'Corrupted database data'}, HTTP_500_INTERNAL_SERVER_ERROR)

            return make_response(content, HTTP_200_OK)
