import unittest
import re
import render


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.template = render.default_template

        self.instructions_fixture_1 = r'''
            title: test title
            build: test build
            '''

        self.instructions_fixture_2 = r'''
            issues:
             - number: 123
               summary: already been fixed
            '''

        self.instructions_fixture_3 = '''
            issues:
             - number: 1234
               files:
                 - CHWeb.dll
                 - ITPCoreBusiness.dll
                 - BR_mods.xlsx
               summary: a few files
            '''


    def test_basic(self):
        html = render.render(self.instructions_fixture_1, self.template)
        self.assertRegex(html, 'test title')
        self.assertRegex(html, 'test build')
        self.assertNotRegex(html, 'App Server')


    def test_sql(self):
        html = render.render('''
            database:
              scripts:
                - asdf.sql
            ''', self.template)
        self.assertRegex(html, 'asdf.sql')


    def test_emptydeployables(self):
        html = render.render(self.instructions_fixture_2, self.template)
        self.assertRegex(html, 'No deployables')


    def test_restartiis(self):
        html = render.render('''
            app:
                restartiis: true
            ''', self.template)
        self.assertRegex(html, 'Restart IIS')


    def test_withfiles(self):
        html = render.render(self.instructions_fixture_3, self.template)
        self.assertRegex(html, 'CHWeb.dll')
        self.assertRegex(html, 'ITPCoreBusiness.dll')
        self.assertRegex(html, 'BR_mods.xlsx')


    def test_specialchars(self):
        html = render.render('''
            issues:
             - issue:
               files:
                 - br_mods_doc
               summary: less than <
            ''', self.template)
        self.assertRegex(html, 'br_mods_doc')
        self.assertRegex(html, 'less than &lt;')


    def test_special(self):
        html = render.render('''
            app:
                special: special app
            ''', self.template)
        self.assertRegex(html, 'special app')

