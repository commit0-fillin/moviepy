""" Misc. bindings to ffmpeg and ImageMagick."""
import os
from moviepy.config import get_setting
from moviepy.tools import subprocess_call, cvsecs
import os
import subprocess as sp
import sys
from moviepy.config import get_setting
from moviepy.tools import subprocess_call

def ffmpeg_movie_from_frames(filename, folder, fps, digits=6, bitrate='v'):
    """
    Writes a movie out of the frames (picture files) in a folder.
    Almost deprecated.
    """
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call
    
    s = "%" + "%02d" % digits + "d"
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-f", "image2",
           "-r", "%d" % fps,
           "-i", os.path.join(folder, s) + ".png",
           "-b", "%dk" % bitrate if isinstance(bitrate, int) else bitrate,
           "-r", "%d" % fps,
           filename]
    
    subprocess_call(cmd)

def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """ Makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call, cvsecs
    
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*cvsecs(t)) for t in [t1, t2]]
        targetname = "%sSUB%d_%d.%s" % (name, T1, T2, ext)
    
    cmd = [get_setting("FFMPEG_BINARY"), "-y",
           "-i", filename,
           "-ss", "%0.2f" % t1,
           "-t", "%0.2f" % (t2-t1),
           "-vcodec", "copy", "-acodec", "copy", targetname]
    
    subprocess_call(cmd)

def ffmpeg_merge_video_audio(video, audio, output, vcodec='copy', acodec='copy', ffmpeg_output=False, logger='bar'):
    """ merges video file ``video`` and audio file ``audio`` into one
        movie file ``output``. """
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call
    
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", audio, "-i", video,
           "-vcodec", vcodec, "-acodec", acodec, output]
    
    subprocess_call(cmd, logger=logger)

def ffmpeg_extract_audio(inputfile, output, bitrate=3000, fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call
    
    ext = os.path.splitext(output)[1][1:]
    cmd = [get_setting("FFMPEG_BINARY"), "-y", "-i", inputfile, "-ab", "%dk" % bitrate,
           "-ar", "%d" % fps, "-vn", output]
    
    subprocess_call(cmd)

def ffmpeg_resize(video, output, size):
    """ resizes ``video`` to new size ``size`` and write the result
        in file ``output``. """
    from moviepy.config import get_setting
    from moviepy.tools import subprocess_call
    
    cmd = [get_setting("FFMPEG_BINARY"), "-i", video, "-vf", "scale=%d:%d" % (size[0], size[1]),
           "-c:a", "copy", output]
    
    subprocess_call(cmd)
