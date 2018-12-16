#!/usr/bin/env python

import sys
import os
import re
from pathlib import Path
import subprocess
import json

_FFMPEG_EXECUTABLE = 'ffmpeg'
_FFPROBE_EXECUTABLE = 'ffprobe'
_DESIRED_AUDIO = ['ac3','dts','dca','aac','mp3','mp2']
_DESIRED_VIDEO = ['hevc','h265','h.265','x265','vc1','h264','h.264','x264','wmv3','mpeg4','mpeg2video','vp9']
_OUTPUT_FORMAT = 'mp4'
_DESIRED_LANGUAGE = ['eng']

def build_destination_path(infile, outdir):
    return Path(os.path.join(outdir, os.path.splitext(os.path.basename(infile))[0]+"."+_OUTPUT_FORMAT))

def do_conversion(infile, outfile, include_streams):
    cmd = _FFMPEG_EXECUTABLE + " -i \"" + str(infile.resolve()) + "\" -map " + " -map ".join(include_streams) + " -c copy \"" + str(outfile.resolve()) + "\""
    print("running: " + cmd)
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def convert(infile, outfile):
    result = subprocess.run(_FFPROBE_EXECUTABLE + " -v quiet -print_format json -show_streams " + str(infile.resolve()), shell=True, check=True, stdout=subprocess.PIPE)
    stream_data = json.loads(result.stdout)
    include_streams = []
    for stream in stream_data['streams']:
        if stream['codec_type'] == 'audio':
            if (stream['tags']['language'] in _DESIRED_LANGUAGE) and (stream['codec_name'] in _DESIRED_AUDIO):
                print('found audio! '  + str(stream['index']) + ' ' + stream['codec_name'] + ' ' + stream['tags']['language'])
                include_streams.append('0:' + str(stream['index']))
        elif stream['codec_type'] == 'video':
            if stream['codec_name'] in _DESIRED_VIDEO:
                print('found video! ' + str(stream['index']) + ' ' + stream['codec_name'])
                include_streams.append('0:' + str(stream['index']))
    return do_conversion(infile, outfile, include_streams)

def run():
    infile = ""
    outfile = ""
    if (len(sys.argv) < 3):
        print('usage: plexopt.py <infile> <outdir>')
        sys.exit()
    infile = Path(sys.argv[1])
    outdir = Path(sys.argv[2])
    if not infile.is_file():
        print('input file does not exist!')
        sys.exit()
    if not outdir.is_dir():
        print('output directory does not exist!')
        sys.exit()
    outfile = build_destination_path(infile, outdir)
    print(outfile)
    result = convert(infile, outfile)
    if result:
        print('conversion succeeded!')   
    else:
        print('conversion failed')
run()