#!/usr/bin/python

from deflacue import deflacue

import sys
import os
import argparse
import glob
import datetime as dt
import ffmpeg
import chardet
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

parser.add_argument('-r', '--recurse', action='store_true', default=False, help='Search recursively')
parser.add_argument('-d', '--directory', type=existing_directory, default='.', help='Directory to search for .cue files')
parser.add_argument('--delete', action='store_true', default=False, help='Delete processed files (.cue and audio track)')
parser.add_argument('-v', '--version', action='store_true', default=False, help='Print version and quit')
parser.add_argument('-V', '--verbose', action='store_true', default=False, help ='Make it more verbose')
args = parser.parse_args()

if args.version:
    print (version)
    sys.exit(0)



print(f"Working directory: {args.directory}")
print(f"Recurse: {args.recurse}")
cues = glob.glob('*.cue', root_dir=args.directory)
cues.extend( x for x in glob.glob('**/*.cue', root_dir=args.directory, recursive=args.recurse) if x not in cues)
cues = [os.path.join(args.directory, cue) for cue in cues]
cues.sort()
print(f"Found files: {'\n'.join(cues)} ")

def parse_cue_timedelta(input: str):
    components = input.split(':')
    components.reverse()
    components.extend([0]*(3-len(components)))
    return dt.timedelta(minutes=int(components[2]), seconds=int(components[1]), milliseconds=int(components[0]))


for cue in cues:
    print(f"Processing album: {cue}")
    cueEncoding = None
    with open(cue, 'rb') as rawdata:
        cueEncoding = chardet.detect(rawdata.read())['encoding']
    cueBaseDir = os.path.dirname(cue)
    tracklist = deflacue.CueParser.from_file(cue, encoding = cueEncoding).run()
    for index, track in enumerate(tracklist.tracks):
        track.startSeconds = parse_cue_timedelta(track.data['INDEX 01'])
        track.endSeconds = parse_cue_timedelta(tracklist.tracks[index+1].data['INDEX 01']) if index+1 < len(tracklist.tracks) else None

    audiofiles = [os.path.join(cueBaseDir, str(f.path)) for f in tracklist.files]

    for index, track in enumerate(tracklist.tracks):
        trackFilename = re.sub(r'[^\w\-_\. ]', '_', f"{index:02d} - {track.title}")[:100] + ".flac"
        trackFilePath = os.path.join(cueBaseDir, trackFilename)
        print(f"Processing track: {trackFilename}, from {track.startSeconds} to {track.endSeconds}")
        outputKWArgs = {
            'ss': track.startSeconds,
            'vn': None,
            'c:a': 'flac',
            'metadata:g:0': f"TITLE={index:02d} - {track.title}",
            'metadata:g:1': f"ARTIST={track.data["PERFORMER"]}",
            'metadata:g:2': f"TRACKNUMBER={index+1:02d}",
            'q:a': 0,
        }
        if track.endSeconds:
            outputKWArgs['to'] = track.endSeconds

        inputFilePath = os.path.join(cueBaseDir, str(track.file.path))
        if not os.path.isfile(inputFilePath):
            print("No source file to cut from, skipping...")
            continue

        program = ffmpeg.input(inputFilePath).output(trackFilePath, **outputKWArgs).overwrite_output()
        print(' '.join(program.compile()))
        program.run()
    if args.delete:
        os.remove(cue)
        for f in audiofiles:
            if os.path.isfile(f):
                os.remove(f)



sys.exit(0)
