import re
import argparse
from xml.etree import ElementTree as ET
import sys
from research import Research


research = Research()


def serverdict(spec):
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


def removeredundant_caseinsensitive(filenames):
    """For strings that have case-insentitive duplicates in the given list, filters all but the last occurrence."""
    lowered = [f.lower() for f in filenames]
    result = []
    for index, filename in enumerate(filenames):
        if filename.lower() not in lowered[index+1:]:
            result.append(filename)
    return result


def research_files(filenames, serverdict, instructions):
    """
    Handles the research and insertion of the files into the instructions, as appropriate.
    Much special casing and business logic here.
    """
    filenames = removeredundant_caseinsensitive(filenames)

    if any(re.search('\.js$', f, re.IGNORECASE) for f in filenames):
        ensure_subelement(instructions, 'javascript').text = 'true'

    if any(re.search('\.xlsx$', f, re.IGNORECASE) for f in filenames):
        ensure_subelement(instructions, 'businessrules').text = 'true'

    for sql_file in [f for f in filenames if re.search('\.sql$', f, re.IGNORECASE)]:
        database = ensure_subelement(instructions, 'database')
        ET.SubElement(database, 'script').text = sql_file

    for server, hostname in serverdict.items():
        for filename in filenames:
            paths = research.locationsfor(filename, hostname)
            addreplacement(instructions, server, filename, paths)
            smf_paths = [path for path in paths if re.search(r'\\SMF\\', path, re.IGNORECASE)]
            addreplacement(instructions, 'admin', filename, smf_paths)
            if any(re.search('\.dll$', p, re.IGNORECASE) for p in paths):
                server_tag = ensure_subelement(instructions, server)
                ensure_subelement(server_tag, 'restartiis').text = 'true'


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
    # TODO: warn if no issues
    # TODO: warn for issues with no number, no files, or no summary
    # TODO: warn if no build number, title


def allfiles(spec):
    return [a.text for a in spec.findall('.//issue/file')]


def instructions_from_spec(spec):
    instructions = ET.Element('instructions')
    validate(spec)
    copy_trivial(spec, instructions)
    research_files(allfiles(spec), serverdict(spec), instructions)
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
