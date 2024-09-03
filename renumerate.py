#!/usr/bin/python

import sys
import os
import argparse
import glob
import re

version = "1.1.1"

def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False

def existing_file(string):
    if not os.path.isfile(string):
        raise argparse.ArgumentTypeError(repr(string) + " not found.")
    return string

def existing_directory(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError(repr(string) + " not found.")
    return string

def create_dir(string):
    if os.path.exists(string) and not os.path.isdir(string):
        raise argparse.ArgumentTypeError(repr(string) + " exist but is not a directory.")
    if not os.path.exists(string):
        os.makedirs(string)
    return string

def slugify(string):
    ilegals = [':', '"', '/', '\\', '|']
    ilegalsInv = ['<', '>', '?', '*']
    for i in ilegals:
        string = string.replace(i, '-')
    for i in ilegalsInv:
        string = string.replace(i, '')
    return string

parser = argparse.ArgumentParser(description='Splits albums files described with a cue sheet')

parser.add_argument('-d', '--directory', type=existing_directory, default='.', help='Directory to search for .cue files')
parser.add_argument('-s', '--start', type=int, default=1, help='Start from number')
parser.add_argument('-v', '--version', action='store_true', default=False, help='Print version and quit')
parser.add_argument('-V', '--verbose', action='store_true', default=False, help ='Make it more verbose')
args = parser.parse_args()

if args.version:
    print (version)
    sys.exit(0)

print(f"Working directory: {args.directory}")

def globFiles(extension: str, root: str):
    files = []
    files.extend(glob.glob(f"*.{extension}", root_dir=root))
    return files
files = []
patterns = ["flac", "ogg", "mp3", "wav"]
for pattern in patterns:
    files.extend(globFiles(pattern, args.directory))

files = [os.path.join(args.directory, file) for file in files]
files.sort()
# print(f"Found files:\n{'\n'.join(files)} ")

i = args.start
for index, file in enumerate(files):
    # origNum = re.search('^[0-9]+', file).group()
    basename = os.path.basename(file)
    newBasename = re.sub(r'^[0-9]+', f'{index + args.start:02d}', basename)
    print(f"{index}: {basename} -> {newBasename}")
    location = os.path.dirname(file)
    os.rename(file, os.path.join(location, newBasename))