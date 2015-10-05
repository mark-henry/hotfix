import unittest
from research import Research


r = Research()


class ResearchTest(unittest.TestCase):
    def test_server_nonexistent(self):
        with self.assertRaises(IOError):
            r.locationsfor('CHWeb.dll', '0.0.0.0')

    def test_file_nonexistent(self):
        self.assertEqual(
            [],
            r.locationsfor('non existent file.asdf', '10.1.0.181'))

    def testCHWeb(self):
        locations = [r"C:\RSI\Web Services\NetWebServices\bin\CHWeb.dll"]
        self.assertEqual(locations, r.locationsfor('CHWeb.dll', '10.1.0.181'))

    def test_caseinsensitive(self):
        self.assertTrue(r.locationsfor('CHWeb.dll', '10.1.0.181'))
        self.assertTrue(r.locationsfor('chweb.dll', '10.1.0.181'))

    def testQuickCHWeb(self):
        print("looking up first...")
        r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("looking up second...")
        r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("looking up third...")
        r.locationsfor('CHWeb.dll', '10.1.0.181')
        print("done!")