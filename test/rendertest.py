import unittest
import render


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.test1_instructions_fixture = minidom.parseString(r'''
            <instructions>
                <title>RPE 1.2.3 Hotfix 999</title>
                <build>RPE-3.5.2.25-HF5-121</build>
            </instructions>
            ''')

    def test_render_1(self):
        pass