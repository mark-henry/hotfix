import pystache
import markdown
import argparse
from xml.dom import minidom


def render(instructions):
    pass


def main():
    ap = argparse.ArgumentParser("Renders an instructions document to HTML")
    args = ap.parse_args()

    print(render(open(args.instructions)))


if __name__ == "__main__":
    main()
