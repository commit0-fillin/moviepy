import os
import subprocess as sp
import proglog
from moviepy.compat import DEVNULL
from moviepy.config import get_setting
from moviepy.decorators import requires_duration

class FFMPEG_AudioWriter:
    """
    A class to write an AudioClip into an audio file.

    Parameters
    ------------

    filename
      Name of any video or audio file, like ``video.mp4`` or ``sound.wav`` etc.

    size
      Size (width,height) in pixels of the output video.

    fps_input
      Frames per second of the input audio (given by the AUdioClip being
      written down).

    codec
      Name of the ffmpeg codec to use for the output.

    bitrate:
      A string indicating the bitrate of the final video. Only
      relevant for codecs which accept a bitrate.

    """

    def __init__(self, filename, fps_input, nbytes=2, nchannels=2, codec='libfdk_aac', bitrate=None, input_video=None, logfile=None, ffmpeg_params=None):
        self.filename = filename
        self.codec = codec
        if logfile is None:
            logfile = sp.PIPE
        cmd = [get_setting('FFMPEG_BINARY'), '-y', '-loglevel', 'error' if logfile == sp.PIPE else 'info', '-f', 's%dle' % (8 * nbytes), '-acodec', 'pcm_s%dle' % (8 * nbytes), '-ar', '%d' % fps_input, '-ac', '%d' % nchannels, '-i', '-'] + (['-vn'] if input_video is None else ['-i', input_video, '-vcodec', 'copy']) + ['-acodec', codec] + ['-ar', '%d' % fps_input] + ['-strict', '-2'] + (['-ab', bitrate] if bitrate is not None else []) + (ffmpeg_params if ffmpeg_params else []) + [filename]
        popen_params = {'stdout': DEVNULL, 'stderr': logfile, 'stdin': sp.PIPE}
        if os.name == 'nt':
            popen_params['creationflags'] = 134217728
        self.proc = sp.Popen(cmd, **popen_params)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

@requires_duration
def ffmpeg_audiowrite(clip, filename, fps, nbytes, buffersize, codec='libvorbis', bitrate=None, write_logfile=False, verbose=True, ffmpeg_params=None, logger='bar'):
    """
    A function that wraps the FFMPEG_AudioWriter to write an AudioClip
    to a file.

    NOTE: verbose is deprecated.
    """
    if write_logfile:
        logfile = open(filename + ".log", 'w+')
    else:
        logfile = None
    
    logger = proglog.default_bar_logger(logger)
    
    with FFMPEG_AudioWriter(filename, fps, nbytes, clip.nchannels, codec=codec,
                            bitrate=bitrate, logfile=logfile,
                            ffmpeg_params=ffmpeg_params) as writer:
        for chunk in clip.iter_chunks(chunksize=buffersize,
                                      quantize=True,
                                      nbytes=nbytes,
                                      fps=fps,
                                      logger=logger):
            writer.write_frames(chunk)

    if write_logfile:
        logfile.close()
