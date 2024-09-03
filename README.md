# cuedeflorate
Python script to split albums stored in singles files with corresponding cueFile.

## Dependencies
To use albumSplitter.py, you need deflacue and ffmpeg-python:

    pip3 install deflacue ffmpeg-python

You'll also need ffmpeg:

    apt-get install ffmpeg

And flac:

    apt-get install flac

## Quickstart
To use cuedeflorate.py, simply call it following this example:

    python cuedeflorate.py -d <workingDir> -r

The script will automatically read the info stored in the .cue file, split the album with one file for each song, apply tags (only 'artist', 'title', 'tracknumber' are applied).

Here is the full help message with parameters description:
```
Splits albums files described with a cue sheet

options:
  -h, --help            show this help message and exit
  -r, --recurse         Search recursively
  -d DIRECTORY, --directory DIRECTORY
                        Directory to search for .cue files
  --delete              Delete processed files (.cue and audio track)
  -v, --version         Print version and quit
  -V, --verbose         Make it more verbose
```
# Donate
This project is given for free ! If you want me to get some draft beers on you, help yourself and donate some coins, contact me using this email: kizzyol76@gmail.com

