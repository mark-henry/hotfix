import re
import argparse
from xml.etree import ElementTree as ET
import sys
from research import Research


research = Research()


def get_server_dict(spec):
    """Returns dict of servertype => hostname, like app => 10.1.0.181
    :rtype : dict
    """
    server_dict = {}
    for server_type in ['app', 'web', 'offline']:
        tag = spec.find(server_type)
        if tag is not None:
            server_dict[server_type] = tag.text
    return server_dict


def copy_trivial(spec, instructions):
    """Copies trivial tags which require no processing, such as build, title, and issues."""
    for tag in ['build', 'title', 'issue']:
        for element in spec.findall(tag):
            instructions.append(element)


def ensure_subelement(element, subtag):
    result = element.find('./' + subtag)
    if result is None:
        result = ET.SubElement(element, subtag)
    return result


def addreplacement(instructions, server, filename, paths):
    if not paths or not filename:
        return
    server_tag = ensure_subelement(instructions, server)
    if not server_tag.find('replacement//filename[text="{}"]'.format(filename)):
        repl_tag = ET.SubElement(server_tag, 'replacement')
        ET.SubElement(repl_tag, 'filename').text = filename
        for path in paths:
            ET.SubElement(repl_tag, 'path').text = path


def handle_file(filename, instructions, serverdict):
    """Handles the research and insertion of the file into the instructions, as appropriate.
    Much special casing and business logic here."""
    if re.search('\.js$', filename, re.IGNORECASE):
        instructions.append(ET.Element('javascript'))
    elif re.search('\.sql$', filename, re.IGNORECASE):
        database = ensure_subelement(instructions, 'database')
        if not any(filename.lower() == existing.text.lower() for existing in instructions.findall('.//script')):
            script = ET.SubElement(database, 'script')
            script.text = filename
        return
    elif re.search('\.xlsx$', filename, re.IGNORECASE):
        ensure_subelement(instructions, 'businessrules').text = 'true'
        return
    for server, hostname in serverdict.items():
        paths = research.locationsfor(filename, hostname)
        addreplacement(instructions, server, filename, paths)
        if re.search('\.dll', filename, re.IGNORECASE):
            server_tag = ensure_subelement(instructions, server)
            ensure_subelement(server_tag, 'restartiis').text = 'true'
        smf_paths = [path for path in paths if re.search(r'\\SMF\\', path, re.IGNORECASE)]
        if smf_paths:
            addreplacement(instructions, 'admin', filename, smf_paths)


def research_files(spec, instructions):
    serverdict = get_server_dict(spec)
    for file_tag in spec.findall('.//file'):
        filename = file_tag.text
        handle_file(filename, instructions, serverdict)


def handle_special(spec, instructions):
    for servertype in ['app', 'web', 'offline']:
        special = spec.find('./{}special'.format(servertype))
        if special is not None:
            server_tag = ensure_subelement(instructions, servertype)
            ET.SubElement(server_tag, 'special').text = special.text


def sort_scripts(instructions):
    """Sorts the <database> section by text"""
    db = instructions.find('./database')
    if db:
        db[:] = sorted(db, key=lambda e: e.text)


def validate(spec):
    for servertype in ['app', 'web', 'offline']:
        if spec.find('.//' + servertype) is None:
            print("Warning: no {} server specified!".format(servertype), file=sys.stderr)


def instructions_from_spec(spec):
    instructions = ET.Element('instructions')
    validate(spec)
    copy_trivial(spec, instructions)
    research_files(spec, instructions)
    handle_special(spec, instructions)
    sort_scripts(instructions)
    return instructions


def main():
    arg_parser = argparse.ArgumentParser(description='Creates hotfix instructions from given specifications.')
    arg_parser.add_argument('specfile', help='hotfix specification file')
    args = arg_parser.parse_args()

    specification = ET.parse(args.specfile).getroot()
    instructions = instructions_from_spec(specification)
    print(ET.tostring(instructions, encoding='unicode'))


if __name__ == "__main__":
    main()
