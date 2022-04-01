import json
import unittest

from pathlib import Path
from modules.Order.Order import Order


class TestOrder(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestOrder, self).__init__(*args, **kwargs)
        path_to_order = Path(r"data\last_closed_order.json")
        with open(path_to_order, "r") as file:
            order_dict = json.load(file)
        self.order = Order.from_dict(order_dict)

    def test_order_properties(self):
        order = self.order
        self.assertEqual(order.gross_value, 198.5265152)
        self.assertEqual(order.net_value, 198.2287254272)
        assert False
