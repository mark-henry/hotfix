import unittest
import compile
from xml.etree import ElementTree


class CompileTest(unittest.TestCase):
    def setUp(self):
        self.spec_fixture_1 = r'''
            <hotfix>
                <title>RPE 1.2.3 Hotfix 999</title>
                <build>RPE-3.5.2.25-HF5-121</build>
                <buildfolder>\\mh-desktop\hotfixbuilds\RPE-3.5.2.25-HF5-121</buildfolder>
                <app>10.1.0.181</app>
                <issue>
                    <number>12345</number>
                    <file>chweb.dll</file>
                    <summary>fixed a thing</summary>
                </issue>
                <issue>
                    <number>33321</number>
                    <file>getCustFinTransactionSrch.sql</file>
                    <file>CaseBusiness.jar</file>
                    <file>deploy_54321.bat</file>
                    <summary>Optimized somethign probably</summary>
                </issue>
            </hotfix>'''


    def test_copy_trivial(self):
        spec = ElementTree.fromstring(self.spec_fixture_1)
        inst = ElementTree.Element('instructions')
        compile.copy_trivial(spec, inst)
        self.assertNotEqual([], inst.findall('.//title'))
        self.assertNotEqual([], inst.findall('.//build'))
        self.assertNotEqual([], inst.findall('.//issue'))
        self.assertNotEqual([], inst.findall('.//file'))
        self.assertNotEqual([], inst.findall('.//summary'))


    def test_js_handling(self):
        js_xml = '<hotfix><issue><file>asdf.js</file><file>asdf2.JS</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(js_xml))
        self.assertEqual(2, len(instructions.findall('.//javascript')))


    def test_sql_noduplication(self):
        js_xml = '<hotfix><issue><file>asdf.sql</file><file>asdf.SQL</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(js_xml))
        self.assertEqual(1, len(instructions.findall('.//script')))


    def test_sql_handling(self):
        js_sql = '<hotfix><issue><file>asdf.sql</file><file>another.sql</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(js_sql))
        self.assertEqual(1, len(instructions.findall('.//database')))
        self.assertNotEqual([], instructions.findall('.//database/script'))


    def test_smf_handling(self):
        dll_xml = '<hotfix><app>10.1.0.181</app><issue><file>RsiFrameworks.Common.dll</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(dll_xml))
        self.assertIsNotNone(instructions.find('.//app/restartiis'))
        self.assertTrue(instructions.findall('.//replacement'))
        self.assertIsNotNone(instructions.find(r'.//admin'))
        self.assertIsNotNone(instructions.find(r'.//app/replacement[path="C:\RSI\SMF\RsiFrameworks.Common.dll"]'))
        self.assertIsNotNone(instructions.find(r'.//admin/replacement[path="C:\RSI\SMF\RsiFrameworks.Common.dll"]'))


    def test_empty_deployables(self):
        xml = '<hotfix><issue><summary>test summary</summary></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(xml))
        self.assertEqual([], instructions.findall('.//file'))


    def test_dll_handling(self):
        dll_xml = '<hotfix><app>10.1.0.181</app><issue><file>CHWeb.dll</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(dll_xml))
        self.assertIsNotNone(instructions.find('.//restartiis'))
        self.assertTrue(instructions.findall('.//replacement'))
        self.assertTrue(instructions.find(r'.//replacement[path="C:\RSI\Web Services\NetWebServices\bin\CHWeb.dll"]'))


    def test_server_dictionary(self):
        servers_xml = '<hotfix><app>10.1.0.181</app><web>10.1.0.182</web></hotfix>'
        server_dict = compile.server_dictionary(ElementTree.fromstring(servers_xml))
        self.assertIn('app', server_dict)
        self.assertIn('web', server_dict)
        self.assertNotIn('offline', server_dict)
        self.assertEqual('10.1.0.181', server_dict['app'])


    def test_sorted(self):
        # TODO: test that files are sorted
        pass


    def test_special_handling(self):
        spec_xml = '<hotfix><appspecial>special app stuff</appspecial></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(spec_xml))
        self.assertIsNotNone(instructions.find('.//appspecial'))
