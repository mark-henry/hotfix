import unittest
import compile
import yaml


class CompileTest(unittest.TestCase):
    def setUp(self):
        self.spec_fixture_1 = r'''
            title: RPE 1.2.3 Hotfix 999
            build: RPE-3.5.2.25-HF5-121
            app: 10.1.0.181
            issues:
              - number: 12345
                files:
                - chweb.dll
                summary: fixed a thing
              - number: 33321
                files:
                - getCustFinTransactionSrch.sql
                - CaseBusiness.jar
                - deploy_54321.bat
                summary: Optimized somethign probably
        '''


    def test_basic(self):
        spec = yaml.safe_load(self.spec_fixture_1)
        compile.instructions_from_spec(spec)


    def test_copy_trivial(self):
        spec = yaml.safe_load(self.spec_fixture_1)
        inst = {}
        compile.copy_trivial(spec, inst)
        self.assertIn('title', inst)
        self.assertIn('build', inst)
        self.assertIn('issues', inst)
        self.assertIn('files', inst['issues'][0])
        self.assertIn('summary', inst['issues'][0])


    def test_js_handling(self):
        js_spec = '''
        issues:
        - issue:
          files:
          - asdf.js
          - asdf2.JS
        '''
        instructions = compile.instructions_from_spec(yaml.safe_load(js_spec))
        self.assertEqual(True, instructions['javascript'])


    def test_sql_noduplication(self):
        sql_spec = '''
        issues:
        - issue:
          files:
           - asdf.sql
           - asdf.SQL
        '''
        instructions = compile.instructions_from_spec(yaml.safe_load(sql_spec))
        self.assertEqual(1, len(instructions['database']['scripts']))


    def test_smf_handling(self):
        smf_spec = '''
        app: 10.1.0.181
        issues:
        - issue:
          files:
          - RsiFrameworks.Common.dll
        '''
        instructions = compile.instructions_from_spec(yaml.safe_load(smf_spec))
        self.assertEqual(True, instructions['app']['restartiis'])
        self.assertIn('replacements', instructions['app'])
        self.assertIn('admin', instructions)
        self.assertTrue([repl for repl in instructions['app']['replacements']
                         if r'C:\RSI\SMF\RsiFrameworks.Common.dll' in repl['paths']])
        self.assertTrue([repl for repl in instructions['admin']['replacements']
                         if r'C:\RSI\SMF\RsiFrameworks.Common.dll' in repl['paths']])


    def test_dll_handling_and_research(self):
        dll_spec = '''
        app: 10.1.0.181
        issues:
        - files:
          - CHWeb.dll
        '''
        instructions = compile.instructions_from_spec(yaml.safe_load(dll_spec))
        self.assertIn('restartiis', instructions['app'])
        self.assertTrue(instructions['app']['replacements'])
        self.assertTrue([r for r in instructions['app']['replacements']
                         if r'C:\RSI\Web Services\NetWebServices\bin\CHWeb.dll' in r['paths']])


    def test_server_dictionary(self):
        servers_spec = '''
        app: 10.1.0.181
        web: 10.1.0.182
        '''
        server_dict = compile.serverdict(yaml.safe_load(servers_spec))
        self.assertIn('app', server_dict)
        self.assertIn('web', server_dict)
        self.assertNotIn('offline', server_dict)
        self.assertEqual('10.1.0.181', server_dict['app'])


    def test_special_handling(self):
        spec = 'appspecial: special app stuff'
        instructions = compile.instructions_from_spec(yaml.safe_load(spec))
        self.assertIn('special', instructions['app'])


    def test_sorted_sql(self):
        spec = '''
        issues:
        - files: [3.sql, 2.sql, 1.sql]'''
        instructions = compile.instructions_from_spec(yaml.safe_load(spec))
        self.assertEqual(instructions['database']['scripts'], ['1.sql', '2.sql', '3.sql'])
