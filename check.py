"""
Verifies the deployable files staged conform to the hofix spec. 
"""
import argparse
import os
from xml.etree import ElementTree as ET


__author__ = 'mhenry'


def get_expected_files(spec):
    files = spec.findall('.//file')
    if files is not None:
        return [file.text.lower() for file in files]
    else:
        return []


def get_staged_files():
    return [f.lower() for f in os.listdir('.') if os.path.isfile(f)]


def check(spec_filename):
    spec = ET.parse(spec_filename).getroot()
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
    ap.add_argument('--spec', default='./.hotfix/spec.xml')
    args = ap.parse_args()
    
    check(args.spec)
    

if __name__ == '__main__':
    main()