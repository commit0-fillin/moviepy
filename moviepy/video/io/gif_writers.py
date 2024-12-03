import os
import subprocess as sp
import numpy as np
import proglog
from moviepy.compat import DEVNULL
from moviepy.config import get_setting
from moviepy.decorators import requires_duration, use_clip_fps_by_default
from moviepy.tools import subprocess_call
try:
    import imageio
    IMAGEIO_FOUND = True
except ImportError:
    IMAGEIO_FOUND = False

@requires_duration
@use_clip_fps_by_default
def write_gif_with_tempfiles(clip, filename, fps=None, program='ImageMagick', opt='OptimizeTransparency', fuzz=1, verbose=True, loop=0, dispose=True, colors=None, logger='bar'):
    """ Write the VideoClip to a GIF file.


    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg. Does the same as write_gif (see this one for more
    docstring), but writes every frame to a file instead of passing
    them in the RAM. Useful on computers with little RAM.

    """
    import tempfile
    import shutil
    import os
    from ..VideoClip import ImageClip

    if logger == 'bar':
        logger = proglog.default_bar_logger('MoviePy - Building GIF with temp files')

    filename = os.path.abspath(filename)
    temp_dir = tempfile.mkdtemp()

    logger(message='Generating GIF frames')
    
    try:
        frame_iterator = clip.iter_frames(fps=fps, logger=logger)
        for i, frame in enumerate(frame_iterator):
            temp_file = os.path.join(temp_dir, f"frame{i:04d}.png")
            ImageClip(frame).save_frame(temp_file)

        logger(message='Assembling GIF')

        if program == 'ImageMagick':
            cmd = [get_setting('IMAGEMAGICK_BINARY'),
                   '-delay', str(1/fps*100),
                   '-loop', str(loop),
                   os.path.join(temp_dir, "frame*.png"),
                   '-coalesce',
                   '-layers', 'OptimizeTransparency',
                   '-fuzz', f'{fuzz}%',
                   filename]
        else:  # ffmpeg
            cmd = [get_setting('FFMPEG_BINARY'), '-y',
                   '-f', 'image2',
                   '-framerate', str(fps),
                   '-i', os.path.join(temp_dir, "frame%04d.png"),
                   '-loop', str(loop),
                   filename]

        subprocess_call(cmd, logger=logger)

    finally:
        logger(message='Cleaning up')
        shutil.rmtree(temp_dir)

    logger(message='GIF ready')

@requires_duration
@use_clip_fps_by_default
def write_gif(clip, filename, fps=None, program='ImageMagick', opt='OptimizeTransparency', fuzz=1, verbose=True, withmask=True, loop=0, dispose=True, colors=None, logger='bar'):
    """ Write the VideoClip to a GIF file, without temporary files.

    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg.


    Parameters
    -----------

    filename
      Name of the resulting gif file.

    fps
      Number of frames per second (see note below). If it
        isn't provided, then the function will look for the clip's
        ``fps`` attribute (VideoFileClip, for instance, have one).

    program
      Software to use for the conversion, either 'ImageMagick' or
      'ffmpeg'.

    opt
      (ImageMagick only) optimalization to apply, either
      'optimizeplus' or 'OptimizeTransparency'.

    fuzz
      (ImageMagick only) Compresses the GIF by considering that
      the colors that are less than fuzz% different are in fact
      the same.


    Notes
    -----

    The gif will be playing the clip in real time (you can
    only change the frame rate). If you want the gif to be played
    slower than the clip you will use ::

        >>> # slow down clip 50% and make it a gif
        >>> myClip.speedx(0.5).write_gif('myClip.gif')

    """
    import tempfile
    import subprocess as sp
    import os
    import numpy as np

    if logger == 'bar':
        logger = proglog.default_bar_logger('MoviePy - Building GIF')

    filename = os.path.abspath(filename)
    
    if program == 'ImageMagick':
        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            temp_name = temp_file.name
            logger(message='Generating GIF frames')
            frame_iterator = clip.iter_frames(fps=fps, logger=logger)
            for i, frame in enumerate(frame_iterator):
                im = Image.fromarray(frame)
                im.save(temp_name)
                if i == 0:
                    cmd = [get_setting('IMAGEMAGICK_BINARY'),
                           '-delay', str(1/fps*100),
                           '-loop', str(loop),
                           temp_name,
                           '-coalesce',
                           '-layers', opt,
                           '-fuzz', f'{fuzz}%']
                    if colors:
                        cmd += ['-colors', str(colors)]
                    cmd.append(filename)
                else:
                    cmd = [get_setting('IMAGEMAGICK_BINARY'),
                           filename,
                           temp_name,
                           '-delay', str(1/fps*100),
                           '-loop', str(loop),
                           '-layers', opt,
                           '-fuzz', f'{fuzz}%']
                    if colors:
                        cmd += ['-colors', str(colors)]
                    cmd.append(filename)
                
                subprocess_call(cmd, logger=logger)
    
    else:  # ffmpeg
        cmd = [get_setting('FFMPEG_BINARY'), '-y',
               '-f', 'rawvideo',
               '-vcodec', 'rawvideo',
               '-r', str(fps),
               '-s', f'{clip.w}x{clip.h}',
               '-pix_fmt', 'rgb24',
               '-i', '-',
               '-filter_complex', f'[0:v]split[x][z];[z]palettegen[y];[x][y]paletteuse',
               '-r', str(fps),
               '-f', 'gif',
               '-loop', str(loop),
               filename]
        
        proc = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)
        for frame in clip.iter_frames(fps=fps, logger=logger):
            proc.stdin.write(frame.tostring())
        proc.stdin.close()
        proc.stderr.close()
        if proc.wait():
            raise IOError(proc.stderr.read().decode('utf8'))

    logger(message='GIF ready')

def write_gif_with_image_io(clip, filename, fps=None, opt=0, loop=0, colors=None, verbose=True, logger='bar'):
    """
    Writes the gif with the Python library ImageIO (calls FreeImage).

    Parameters
    -----------
    opt
      Optimization level, between 0 and 5.
      0 means no optimization, 5 means maximum optimization.

    """
    if not IMAGEIO_FOUND:
        raise ImportError("Writing GIFs with imageio requires ImageIO installed")
    
    if logger == 'bar':
        logger = proglog.default_bar_logger('MoviePy - Building GIF with ImageIO')

    if fps is None:
        fps = clip.fps

    quantizer = 0 if colors is None else 2
    writer = imageio.get_writer(filename, mode='I', fps=fps, loop=loop, quantizer=quantizer)

    logger(message='Generating GIF frames')
    for frame in clip.iter_frames(fps=fps, logger=logger):
        writer.append_data(frame)

    writer.close()
    logger(message='GIF ready')
