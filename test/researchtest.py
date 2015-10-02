import unittest
from research import Research


class ResearcherTest(unittest.TestCase):
    def setUp(self):
        self.r = Research()

    def test_server_nonexistent(self):
        with self.assertRaises(IOError):
            self.r.locationsfor('CHWeb.dll', '0.0.0.0')

    def test_file_nonexistent(self):
        self.assertEqual(
            [],
            self.r.locationsfor('non existent file.asdf', '10.1.0.181'))

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