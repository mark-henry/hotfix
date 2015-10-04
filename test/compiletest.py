import unittest
import compile
from xml.etree import ElementTree


class CompilerTest(unittest.TestCase):
    def setUp(self):
        self.spec_fixture_1 = r'''
            <hotfix>
                <title>RPE 1.2.3 Hotfix 999</title>
                <build>RPE-3.5.2.25-HF5-121</build>
                <buildfolder>\\mh-desktop\hotfixbuilds\RPE-3.5.2.25-HF5-121</buildfolder>
                <app>10.1.0.181</app>
                <web>10.1.0.182</web>
                <offline>10.1.0.183</offline>
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


    def test_js_noduplication(self):
        js_xml = '<hotfix><issue><file>asdf.js</file><file>asdf.JS</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(js_xml))
        self.assertEqual(1, len(instructions.findall('.//script')))


    def test_sql_handling(self):
        js_sql = '<hotfix><issue><file>asdf.sql</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(js_sql))
        self.assertNotEqual([], instructions.findall('.//database'))
        self.assertNotEqual([], instructions.findall('.//database/script'))


    def test_smf_handling(self):
        pass  # TODO


    def test_empty_deployables(self):
        xml = '<hotfix><issue><summary>test summary</summary></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(xml))
        self.assertEqual([], instructions.findall('.//file'))


    def test_dll_handling(self):
        dll_xml = '<hotfix><issue><file>CHWeb.dll</file></issue></hotfix>'
        instructions = compile.instructions_from_spec(ElementTree.fromstring(dll_xml))
        self.assertNotEqual([], instructions.findall('.//restartiis'))
        self.assertNotEqual([], instructions.findall('.//replace'))
        # TODO: assert a file path


    def test_server_dictionary(self):
        servers_xml = '<hotfix><app>10.1.0.181</app><web>10.1.0.182</web></hotfix>'
        server_dict = compile.server_dictionary(ElementTree.fromstring(servers_xml))
        self.assertIn('app', server_dict)
        self.assertIn('web', server_dict)
        self.assertNotIn('offline', server_dict)
        self.assertEqual('10.1.0.181', server_dict['app'])


    def test_compile_spec(self):
        compile.instructions_from_spec(ElementTree.fromstring(self.spec_fixture_1))