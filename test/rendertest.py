import unittest
import render


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.template = render.default_template

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
                    <file>BR_mods_doc.xlsx</file>
                    <summary>a few files</summary>
                </issue>
            </instructions>
            '''


    def test_basic(self):
        html = render.render(self.instructions_fixture_1, self.template)
        self.assertRegex(html, "test title")
        self.assertRegex(html, "test build")
        self.assertNotRegex(html, "App Server")


    def test_sql(self):
        html = render.render('''<instructions><database><script>asdf.sql</script></database></instructions>''',
                             self.template)
        self.assertRegex(html, 'asdf.sql')


    def test_emptydeployables(self):
        html = render.render(self.instructions_fixture_2, self.template)
        self.assertRegex(html, "there are no deployables")


    def test_restartiis(self):
        html = render.render('''<instructions><app><restartiis>true</restartiis></app></instructions>''', self.template)
        self.assertRegex(html, 'Restart IIS')


    def test_withfiles(self):
        html = render.render(self.instructions_fixture_3, self.template)
        self.assertRegex(html, "CHWeb.dll")
        self.assertRegex(html, "ITPCoreBusiness.dll")
        self.assertRegex(html, "BR_mods_doc.xlsx")


    def test_htmlescapes(self):
        html = render.render(r"<instructions><issue><file>br_mods_doc</file></issue></instructions>",
                             self.template)
        self.assertRegex(html, "br_mods_doc")