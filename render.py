import pystache
import markdown
import argparse
import xmltodict


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
    arg_parser.add_argument('--template', default='hotfix.mustache', help='handlebars-in-markdown template file')
    args = arg_parser.parse_args()

    html = render(
        open(args.instructions).read(),
        open(args.template).read())
    print(html)


if __name__ == "__main__":
    main()
