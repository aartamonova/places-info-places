import unittest

from alchemy_mock.mocking import UnifiedAlchemyMagicMock, AlchemyMagicMock

from places.places_model import Place


class TestPlaces(unittest.TestCase):
    def test_get_none(self):
        session = UnifiedAlchemyMagicMock()
        result = session.query(Place).all()
        return self.assertEqual(len(result), 0)

    def test_get_attribute_error(self):
        session = AlchemyMagicMock()
        with self.assertRaises(AttributeError):
            session.query(Place).filter(Place.foo == 1).all()

    def test_get_all(self):
        session = UnifiedAlchemyMagicMock()
        session.add(Place(id=1, name='a', type='b', description='123'))
        result = session.query(Place).all()
        return self.assertEqual(len(result), 1)
