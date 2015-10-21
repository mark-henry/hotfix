"""
Refreshes the files in current working directory from the build output folder path
given in hotfix spec file
"""
import os
import argparse
import shutil
import yaml
import subprocess


def find(buildfolder, filename):
    try:
        search = subprocess.check_output(['where', '/r', buildfolder, filename], shell=True)
        if not search:
            return None
        return search.splitlines()[0].decode('utf-8')
    except:
        return None


def files(spec):
    for issue in spec['issues']:
        for file in issue.get('files', []):
            yield file


def stage(spec_str, buildoutputfolder, refresh_only: bool):
    spec = yaml.safe_load(spec_str)

    build_tag = spec.get('build', None)
    if build_tag is None:
        print('Error: no <build> specified in spec!')
        return
    buildfolder = buildoutputfolder + '\\' + build_tag

    if refresh_only:
        files_to_stage = [f for f in os.listdir('.') if os.path.isfile(f)]
    else:
        files_to_stage = list(files(spec))
        if len(files_to_stage) == 0:
            print("No files in hotfix")
            return

    for filename in files_to_stage:
        src_path = find(buildfolder, filename)
        if not src_path:
            print('Could not find {} in build folder'.format(filename))
            continue
        shutil.copy2(src_path, '.')
        print('Copied file {} from {}'.format(filename, buildfolder))


def main():
    ap = argparse.ArgumentParser('Stages files from build output into current directory according to spec.')
    ap.add_argument('--buildsfolder', default='d:\\hotfixbuilds')
    ap.add_argument('--spec', default='.hotfix/spec.yaml', help='Looks in .hotfix by default')
    ap.add_argument('--refresh', dest='refresh', action='store_true',
                    help='Refresh only those files that are already staged in current dir.')
    ap.set_defaults(refresh=False)
    args = ap.parse_args()

    with open(args.spec) as specfile:
        stage(specfile.read(), args.buildsfolder, args.refresh)


if __name__ == '__main__':
    main()