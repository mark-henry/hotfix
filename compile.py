import re
import argparse
import sys
import yaml
from research import Research


research = Research()


def serverdict(spec) -> dict:
    """Returns dict of servertype => hostname, like app => 10.1.0.181"""
    server_dict = {}
    for server_type in ['app', 'web', 'offline']:
        if server_type in spec:
            server_dict[server_type] = spec[server_type]
    return server_dict


def copy_trivial(spec, instructions):
    """Copies trivial tags which require no processing, such as build, title, and issues."""
    for tag in ['build', 'title', 'issues']:
        if tag in spec:
            instructions[tag] = spec[tag]


def addreplacement(instructions, server, filename, paths):
    if not paths or not filename:
        return
    replacements = instructions.setdefault(server, {}).setdefault('replacements', [])
    replacements.append({
        'filename': filename,
        'paths': sorted(paths)
    })


def removeredundant_caseinsensitive(filenames) -> list:
    """For strings that have case-insentitive duplicates in the given list, filters all but the last occurrence."""
    lowered = [f.lower() for f in filenames]
    result = []
    for index, filename in enumerate(filenames):
        if filename.lower() not in lowered[index + 1:]:
            result.append(filename)
    return result


def research_files(filenames, servers, instructions):
    """
    Handles the research and insertion of the files into the instructions, as appropriate.
    Much special casing and business logic here.
    """
    filenames = removeredundant_caseinsensitive(filenames)

    if any(re.search('\.js$', f, re.IGNORECASE) for f in filenames):
        instructions['javascript'] = True

    if any(re.search('\.xlsx$', f, re.IGNORECASE) for f in filenames):
        instructions['businessrules'] = True


    sql_files = [f for f in filenames if re.search('\.sql$', f, re.IGNORECASE)]
    if sql_files:
        instructions.setdefault('database', {})['scripts'] = sorted(sql_files)

    for server, hostname in servers.items():
        for filename in filenames:
            paths = research.locationsfor(filename, hostname)
            addreplacement(instructions, server, filename, paths)
            smf_paths = [path for path in paths if re.search(r'\\SMF\\', path, re.IGNORECASE)]
            addreplacement(instructions, 'admin', filename, smf_paths)
            if any(re.search('\.dll$', p, re.IGNORECASE) for p in paths):
                instructions.setdefault(server, {})['restartiis'] = True


def handle_special(spec, instructions):
    for servertype in ['app', 'web', 'offline']:
        special = servertype + 'special'
        if special in spec:
            instructions.setdefault(servertype, {})['special'] = spec[special]


def validate(spec):
    def warn(msg):
        print("Warning: {}!".format(msg), file=sys.stderr)
        
    for servertype in ['app', 'web', 'offline']:
        if servertype not in spec:
            warn("no {} server specified".format(servertype))
    if 'build' not in spec:
        warn('no build number specified')
    if 'title' not in spec:
        warn('no title specified')
    if 'issues' not in spec:
        warn('no issues in hotfix')
    for issue in spec.get('issues', []):
        if 'number' not in issue:
            warn('no number specified for issue')
        issue_num = issue.get('number', '<no number>')
        if 'files' not in issue:
            warn('no files specified for issue {}'.format(issue_num))
        if 'summary' not in issue:
            warn('no summary specified for issue {}'.format(issue_num))


def allfiles(spec):
    files = []
    for issue in spec.get('issues', []):
        if 'files' in issue:
            files.extend(issue['files'])
    return files


def instructions_from_spec(spec):
    instructions = {}
    validate(spec)
    copy_trivial(spec, instructions)
    research_files(allfiles(spec), serverdict(spec), instructions)
    handle_special(spec, instructions)
    return instructions


def main():
    arg_parser = argparse.ArgumentParser(description='Creates hotfix template values from given specifications.')
    arg_parser.add_argument('specfile', help='hotfix specification file')
    args = arg_parser.parse_args()

    with open(args.specfile) as yamlfile:
        specification = yaml.safe_load(yamlfile.read())
        instructions = instructions_from_spec(specification)
        print(yaml.dump(instructions))


if __name__ == "__main__":
    main()
