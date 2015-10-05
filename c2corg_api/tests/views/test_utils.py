import unittest

from c2corg_api.views.utils import rest_to_dict


class TestUtils(unittest.TestCase):

    def test_put_success_all(self):
        url = 'http://c2c/outings/list/summits/639674-41487-40127/orderby/act/order/asc'  # noqa
        d = rest_to_dict(url)
        self.assertEqual(d['outings'], 'list')
        self.assertEqual(d['order'], 'asc')
        self.assertEqual(len(d), 4)
