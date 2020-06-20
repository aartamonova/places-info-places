from places import db


class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    type = db.Column(db.String(20))
    description = db.Column(db.String(1024))
    phone = db.Column(db.String(64))
    address = db.Column(db.String(64))
    added_by = db.Column(db.String(20))


class PlaceData:
    @staticmethod
    def get_by_id(place_id):
        place = Place.query.filter_by(id=place_id).first()
        return place

    @staticmethod
    def get_by_name(name):
        place = Place.query.filter_by(name=name).first()
        return place

    @staticmethod
    def get_all(page, size):
        places = Place.query.order_by(Place.id).paginate(page, size, error_out=False).items
        return places

    @staticmethod
    def search(page, size, name):
        place = Place.query.filter(Place.name.ilike('%' + name + '%')).order_by(Place.id).paginate(page, size, error_out=False).items
        return place

    @staticmethod
    def create(name, place_type, description, phone, address, added_by):
        old_place = PlaceData.get_by_name(name)
        if not old_place:
            place = Place(name=name,
                          type=place_type,
                          description=description,
                          phone=phone,
                          address=address,
                          added_by=added_by)
            if place:
                db.session.add(place)
                db.session.commit()
                return place
        return None

    @staticmethod
    def edit(place_id, args):
        place = PlaceData.get_by_id(place_id)
        if place:
            if 'name' in args:
                old_place = PlaceData.get_by_name(args['name'])
                if old_place and place.name != args['name']:
                    return None
                place.name = str(args['name'])

            if 'type' in args:
                place.type = str(args['type'])

            if 'description' in args:
                place.description = str(args['description'])

            if 'address' in args:
                place.address = str(args['address'])

            if 'phone' in args:
                place.phone = str(args['phone'])

            db.session.commit()
        return place

    @staticmethod
    def delete(place_id):
        place = PlaceData.get_by_id(place_id)
        if place:
            db.session.delete(place)
            db.session.commit()
