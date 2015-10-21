"""
Verifies the deployable files staged conform to the hofix spec. 
"""
import argparse
import os
import yaml


__author__ = 'mhenry'


def get_expected_files(spec):
    files = []
    for issue in spec.get('issues', []):
        files.extend([f.lower() for f in issue.get('files', [])])
    return files


def get_staged_files():
    return [f.lower() for f in os.listdir('.') if os.path.isfile(f)]


def check(spec_str):
    spec = yaml.safe_load(spec_str)
    spec_files = get_expected_files(spec)
    staged_files = get_staged_files()
    for expected in spec_files:
        if expected not in staged_files:
            print("Missing from staging: " + expected)
    for staged in staged_files:
        if staged not in spec_files:
            print("Unexpected file: " + staged)


def main():
    ap = argparse.ArgumentParser(description='Verifies that the files for this hotfix conform to spec.')
    ap.add_argument('--spec', default='.hotfix/spec.yaml')
    args = ap.parse_args()

    with open(args.spec) as specfile:
        check(specfile.read())
    

if __name__ == '__main__':
    main()