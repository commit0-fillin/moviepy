"""
This module implements all the functions to read a video or a picture
using ffmpeg. It is quite ugly, as there are many pitfalls to avoid
"""
from __future__ import division
import logging
import os
import re
import subprocess as sp
import warnings
import numpy as np
from moviepy.compat import DEVNULL, PY3
from moviepy.config import get_setting
from moviepy.tools import cvsecs
logging.captureWarnings(True)

class FFMPEG_VideoReader:

    def __init__(self, filename, print_infos=False, bufsize=None, pix_fmt='rgb24', check_duration=True, target_resolution=None, resize_algo='bicubic', fps_source='tbr'):
        self.filename = filename
        self.proc = None
        infos = ffmpeg_parse_infos(filename, print_infos, check_duration, fps_source)
        self.fps = infos['video_fps']
        self.size = infos['video_size']
        self.rotation = infos['video_rotation']
        if target_resolution:
            target_resolution = (target_resolution[1], target_resolution[0])
            if None in target_resolution:
                ratio = 1
                for idx, target in enumerate(target_resolution):
                    if target:
                        ratio = target / self.size[idx]
                self.size = (int(self.size[0] * ratio), int(self.size[1] * ratio))
            else:
                self.size = target_resolution
        self.resize_algo = resize_algo
        self.duration = infos['video_duration']
        self.ffmpeg_duration = infos['duration']
        self.nframes = infos['video_nframes']
        self.infos = infos
        self.pix_fmt = pix_fmt
        self.depth = 4 if pix_fmt == 'rgba' else 3
        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100
        self.bufsize = bufsize
        self.initialize()
        self.pos = 1
        self.lastread = self.read_frame()

    def initialize(self, starttime=0):
        """Opens the file, creates the pipe. """
        self.close()  # if any

        if starttime != 0:
            offset = min(1, starttime)
            i_arg = ['-ss', "%.06f" % (starttime - offset),
                     '-i', self.filename,
                     '-ss', "%.06f" % offset]
        else:
            i_arg = ['-i', self.filename]

        cmd = ([get_setting("FFMPEG_BINARY")] + i_arg +
               ['-loglevel', 'error',
                '-f', 'image2pipe',
                '-pix_fmt', self.pix_fmt,
                '-vcodec', 'rawvideo', '-'])

        if self.size != self.infos['video_size']:
            cmd += ['-s', '%dx%d' % (self.size[0], self.size[1]),
                    '-sws_flags', self.resize_algo]

        self.proc = sp.Popen(cmd, bufsize=self.bufsize,
                             stdout=sp.PIPE,
                             stderr=sp.PIPE)

        self.pos = int(self.fps * starttime)

    def skip_frames(self, n=1):
        """Reads and throws away n frames """
        w, h = self.size
        for i in range(n):
            self.proc.stdout.read(self.depth * w * h)
            self.pos += 1

    def get_frame(self, t):
        """ Read a file video frame at time t.

        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fetching arbitrary frames
        whenever possible, by moving between adjacent frames.
        """
        # Get frame number from time
        pos = int(self.fps * t)
        
        if pos == self.pos:
            return self.lastread
        else:
            if (pos < self.pos) or (pos > self.pos + 100):
                self.initialize(t)
                self.pos = pos
            else:
                self.skip_frames(pos - self.pos - 1)
            
            result = self.read_frame()
            self.pos = pos
            return result

    def __del__(self):
        self.close()

def ffmpeg_read_image(filename, with_mask=True):
    """ Read an image file (PNG, BMP, JPEG...).

    Wraps FFMPEG_Videoreader to read just one image.
    Returns an ImageClip.

    This function is not meant to be used directly in MoviePy,
    use ImageClip instead to make clips out of image files.

    Parameters
    -----------

    filename
      Name of the image file. Can be of any format supported by ffmpeg.

    with_mask
      If the image has a transparency layer, ``with_mask=true`` will save
      this layer as the mask of the returned ImageClip

    """
    if with_mask:
        pix_fmt = 'rgba'
    else:
        pix_fmt = 'rgb24'
    
    reader = FFMPEG_VideoReader(filename, pix_fmt=pix_fmt, check_duration=False)
    im = reader.lastread
    reader.close()

    return im

def ffmpeg_parse_infos(filename, print_infos=False, check_duration=True, fps_source='tbr'):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_nframes",
    "video_duration", "audio_found", "audio_fps"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """
    # Open the file in a pipe, read output
    cmd = [get_setting("FFMPEG_BINARY"), "-i", filename]
    if not check_duration:
        cmd += ["-t", "00:00:00.1"]
    cmd += ["-f", "null", "-"]

    popen_params = {"bufsize": 10**5,
                    "stdout": sp.PIPE,
                    "stderr": sp.PIPE,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)
    (output, error) = proc.communicate()
    infos = error.decode('utf8')

    if print_infos:
        # print the whole info text returned by FFMPEG
        print(infos)

    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError(("MoviePy error: the file %s could not be found!\n"
                       "Please check that you entered the correct "
                       "path.") % filename)

    result = dict()
    result['video_found'] = False
    result['audio_found'] = False
    result['duration'] = None
    result['video_duration'] = None
    result['audio_duration'] = None

    # parse the output
    for line in lines:
        try:
            line = line.strip()
            if line.startswith('Duration:'):
                match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
                result['duration'] = cvsecs(match)
            elif line.startswith('Stream') and 'Video:' in line:
                result['video_found'] = True
                match = re.findall(" [0-9]*.* fps", line)
                fps = float(match[0].split(' ')[1])
                result['video_fps'] = fps
            elif line.startswith('Stream') and 'Audio:' in line:
                result['audio_found'] = True
        except:
            pass

    # compute video duration and number of frames
    if result['video_found']:
        result['video_nframes'] = int(result['duration'] * result['video_fps']) + 1
        result['video_duration'] = result['duration']
    if result['audio_found']:
        result['audio_duration'] = result['duration']

    # We could have also recomputed the duration from the number
    # of frames, as follows:
    # >>> result['duration'] = result['video_nframes'] / result['video_fps']

    return result
