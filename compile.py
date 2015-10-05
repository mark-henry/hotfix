import re, sys, argparse
from xml.etree import ElementTree as ET
from research import Research

research = Research()


def instruct_file(filename, instructions, hostname):
    '''Researches file and adds it to the instructions.
    Much decision-making and special-casing is done here.'''
    if re.match('.dll$', filename):
        locations = research.locationsfor(filename, hostname)


def server_dictionary(spec):
    '''Returns dictionary of servertype => hostname, like app => 10.1.0.181
    :rtype : dict
    '''
    server_dict = {}
    for server_type in ['app', 'web', 'offline']:
        tag = spec.find(server_type)
        if tag is not None:
            server_dict[server_type] = tag.text
    return server_dict


def copy_trivial(spec, instructions):
    '''Copies trivial tags which require no processing, such as build, title, and issues.'''
    for tag in ['build', 'title', 'issue']:
        for element in spec.findall(tag):
            instructions.append(element)


def addreplacement(instructions, server, filename, paths):
    if not paths or not filename:
        return
    server_tag = instructions.find(server)
    if server_tag is None:
        server_tag = ET.SubElement(instructions, server)
    if not server_tag.find('replacement//filename[text="{}"]'.format(filename)):
        repl_tag = ET.SubElement(server_tag, 'replacement')
        ET.SubElement(repl_tag, 'filename').text = filename
        for path in paths:
            ET.SubElement(repl_tag, 'path').text = path


def handle_file(filename, instructions, serverdict):
    '''Handles the research and insertion of the file into the instructions, as appropriate.
    Much special casing and business logic here.'''
    if re.search('\.js$', filename, re.IGNORECASE):
        instructions.append(ET.Element('javascript'))
    elif re.search('\.sql$', filename, re.IGNORECASE):
        database = ET.SubElement(instructions, 'database')
        if not any(filename.lower() == existing.text.lower() for existing in instructions.findall('.//script')):
            script = ET.SubElement(database, 'script')
            script.text = filename
        return
    elif re.search('\.xlsx$', filename, re.IGNORECASE):
        ET.SubElement(instructions, 'businessrules')
        return
    elif re.search('\.dll', filename, re.IGNORECASE):
        ET.SubElement(instructions, 'restartiis')
    for server, hostname in serverdict.items():
        paths = research.locationsfor(filename, hostname)
        addreplacement(instructions, server, filename, paths)
        SMF_paths = [path for path in paths if re.search(r'\\SMF\\', path, re.IGNORECASE)]
        if SMF_paths:
            addreplacement(instructions, 'admin', filename, SMF_paths)


def research_files(spec, instructions):
    serverdict = server_dictionary(spec)
    for file_tag in spec.findall('.//file'):
        filename = file_tag.text
        handle_file(filename, instructions, serverdict)


def instructions_from_spec(spec):
    instructions = ET.Element('instructions')
    copy_trivial(spec, instructions)
    research_files(spec, instructions)
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