"""Small smoke-test example; run with `python -m unittest discover -s tests`."""
import os
import tempfile
import unittest

# This simple project uses a fixed DATABASE constant. These tests focus on route availability
# for local classroom demonstration rather than full isolated database testing.
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as shop_app


class ShopSmokeTests(unittest.TestCase):
    def setUp(self):
        shop_app.app.config["TESTING"] = True
        self.client = shop_app.app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
