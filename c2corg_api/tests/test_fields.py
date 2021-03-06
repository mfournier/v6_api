import unittest

from c2corg_common.fields_waypoint import fields_waypoint
from c2corg_common.fields_route import fields_route
from c2corg_common.attributes import waypoint_types, activities
from c2corg_api.models.waypoint import Waypoint, WaypointLocale
from c2corg_api.models.route import Route, RouteLocale
from c2corg_api.models.document import DocumentGeometry


class TestFields(unittest.TestCase):

    def test_waypoint_fields(self):
        """Test that the fields listed for a waypoint type are correct.
        """
        for type in fields_waypoint:
            self.assertIn(
                type, waypoint_types, 'invalid waypoint type: %s' % (type))
            self._test_fields_for_type(
                type, fields_waypoint, Waypoint, WaypointLocale)

    def test_route_fields(self):
        """Test that the fields listed for a route activity are correct.
        """
        for type in fields_route:
            self.assertIn(
                type, activities, 'invalid route type: %s' % (type))
            self._test_fields_for_type(
                type, fields_route, Route, RouteLocale)

    def _test_fields_for_type(
            self, waypoint_type, fields, model, model_locale):
        fields_info = fields.get(waypoint_type)
        self._test_fields(fields_info.get('fields'), model, model_locale)
        self._test_fields(fields_info.get('required'), model, model_locale)

    def _test_fields(self, fields, model, model_locale):
        for field in fields:
            if '.' in field:
                field_parts = field.split('.')
                self.assertEquals(
                    len(field_parts), 2, 'only checking the next level')
                self.assertTrue(
                    hasattr(model, field_parts[0]),
                    '%s in %s' % (field_parts[0], model))

                if field_parts[0] == 'locales':
                    sub_model = model_locale
                elif field_parts[0] == 'geometry':
                    sub_model = DocumentGeometry
                else:
                    self.assertTrue(
                        False, '%s not expected' % (field_parts[0]))
                self.assertTrue(
                    hasattr(sub_model, field_parts[1]),
                    '%s not in %s' % (field_parts[1], sub_model))
            else:
                self.assertTrue(
                    hasattr(model, field),
                    '%s not in %s' % (field, model))
