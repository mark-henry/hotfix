import pystache
import markdown
import argparse
import xmltodict
from collections import OrderedDict


default_template = r'''
# {{title}} #


{{#issue}}
### Issue {{number}} ###
###### Files included for issue {{number}} ######
{{#file}}
* {{{.}}}
{{/file}}
{{^file}}
This issue is already resolved and there are no deployables.
{{/file}}

###### Summary of issue {{number}} ######
{{{summary}}}
{{/issue}}

*Warning: Back up all files before overwriting or deleting.*


{{#app}}
## App Server ##
{{special}}

{{#replacement}}

Replace {{filename}} in the following locations:

{{#path}}
1. {{{.}}}
{{/path}}
{{/replacement}}

{{#restartiis}}
Restart IIS.
{{/restartiis}}
{{/app}}


{{#web}}
## Web Server ##
{{special}}

{{#replacement}}

Replace {{filename}} in the following locations:

{{#path}}
1. {{{.}}}
{{/path}}
{{/replacement}}

{{#restartiis}}
Restart IIS.
{{/restartiis}}
{{/web}}


{{#offline}}
## Offline Server ##
{{special}}

{{#replacement}}

Replace {{filename}} in the following locations:

{{#path}}
1. {{{.}}}
{{/path}}
{{/replacement}}

{{#restartiis}}
Restart IIS.
{{/restartiis}}
{{/offline}}


{{#admin}}
## Admin Tool ##
Replace these files on any machine running the Admin Tool:
{{#replacement}}

Replace {{filename}} in the following locations:

{{#path}}
1. {{{.}}}
{{/path}}
{{/replacement}}

{{/admin}}


{{#database}}
## Database ##
Have a database administrator run the following scripts.

{{#script}}
1. {{{.}}}
{{/script}}
{{/database}}


{{#javascript}}
## Client Browsers ##
Delete all temporary internet files to remove previous JavaScript file from client browser machines.

1. Open Internet Options from within Internet Explorer.
2. From the General tab, click the Delete... button.
3. Check only the Temporary Internet Files box and click Delete.
{{/javascript}}

{{#businessrules}}
## Business Rules ##
Review all BR modifications spreadsheet documents and make the changes they describe. Then, rebuild and redeploy the object model and .adb files.
{{/businessrules}}

{{#build}}
*Pulled from build {{.}}*
{{/build}}
'''


def render(instructions, template):
    inst = xmltodict.parse(instructions)['instructions']
    templated = pystache.render(template, inst)
    rendered = markdown.markdown(templated)
    return r'''<html><head>
    <link href="https://netdna.bootstrapcdn.com/twitter-bootstrap/2.2.1/css/bootstrap.min.css" rel="stylesheet">
    <style>body {{ margin: 25px }}</style>
    <title>{0}</title>
    <body>{1}</body>
    </html>'''.format(inst.get('title', 'Hotfix Instructions'), rendered)


def main():
    desc = '''
    Renders an HTML page from the given template and instructions.

    Template should be a Mustache template that, when rendered with the given
    template as context, creates a Markdown document.

    --template is optional and is hotfix.mustache by default.
    '''
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('instructions', help='xml instructions file')
    arg_parser.add_argument('--template', help='handlebars-in-markdown template file')
    args = arg_parser.parse_args()

    html = render(
        open(args.instructions).read(),
        open(args.template).read() if args.template else default_template)
    print(html)


if __name__ == "__main__":
    main()
