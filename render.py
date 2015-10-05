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
    ap = argparse.ArgumentParser("Renders an instructions document to HTML")
    args = ap.parse_args()

    html = render(
        open(args.instructions).read(),
        open(args.template).read())
    print(html)


if __name__ == "__main__":
    main()
