import unittest
import render
from xml.etree import ElementTree as ET


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.template = open("hotfix.mustache").read()
        self.instructions_fixture_1 = r'''
            <instructions>
                <title>test title</title>
                <build>test build</build>
            </instructions>
            '''

        self.instructions_fixture_2 = r'''
            <instructions>
                <issue>
                    <number>123</number>
                    <summary>already been fixed</summary>
                </issue>
            </instructions>
            '''

        self.instructions_fixture_3 = r'''
            <instructions>
                <issue>
                    <number>1234</number>
                    <file>CHWeb.dll</file>
                    <file>ITPCoreBusiness.dll</file>
                    <summary>a few files</summary>
                </issue>
            </instructions>
            '''

    def test_basic(self):
        html = render.render(self.instructions_fixture_1, self.template)
        self.assertRegex(html, "test title")
        self.assertRegex(html, "test build")
        self.assertNotRegex(html, "App Server")

    def test_emptydeployables(self):
        html = render.render(self.instructions_fixture_2, self.template)
        self.assertRegex(html, "there are no deployables")


    def test_withfiles(self):
        html = render.render(self.instructions_fixture_3, self.template)
        self.assertRegex(html, "CHWeb.dll")
        self.assertRegex(html, "ITPCoreBusiness.dll")