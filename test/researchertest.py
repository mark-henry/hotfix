import unittest
from researcher import Researcher


class ResearcherTest(unittest.TestCase):
    def setUp(self):
        self.r = Researcher()

    def testCHWeb(self):
        locations = [r"C:\RSI\Web Services\NetWebServices\bin\CHWeb.dll"]
        self.assertEqual(locations, self.r.locationsfor('CHWeb.dll', '10.1.0.181'))

    def testQuickCHWeb(self):
        print("looking up first...")
        self.r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("looking up second...")
        self.r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("looking up third...")
        self.r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("done!")