import json
import unittest

from pathlib import Path
from modules.Order.Order import Order


class TestOrder(unittest.TestCase):

    def test_order(self):
        path_to_order = Path(r"data\last_closed_order.json")
        with open(path_to_order, "r") as file:
            order_dict = json.load(file)
        order = Order.from_dict(order_dict)
        self.assertEqual(order.symbol, "BTC/EUR")
