import pystache
import markdown
import argparse
import xmltodict


def render(instructions, template):
    inst = xmltodict.parse(instructions)['instructions']
    templated = pystache.render(template, inst)
    rendered = markdown.markdown(templated)
    return rendered


def main():
    desc = '''
    Renders an HTML page from the given template and instructions.

    Template should be a Mustache template that, when rendered with the given
    template as context, creates a Markdown document.
    '''
    arg_parser = argparse.ArgumentParser(description=desc)
    arg_parser.add_argument('instructions', help='xml instructions file')
    arg_parser.add_argument('template', default='hotfix.mustache', help='handlebars-in-markdown template file')
    args = arg_parser.parse_args()

    html = render(
        open(args.instructions).read(),
        open(args.template).read())
    print(html)


if __name__ == "__main__":
    main()
