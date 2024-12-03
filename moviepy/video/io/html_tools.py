"""
This module implements ipython_display
A function to embed images/videos/audio in the IPython Notebook
"""
import os
from base64 import b64encode
from moviepy.audio.AudioClip import AudioClip
from moviepy.tools import extensions_dict
from ..VideoClip import ImageClip, VideoClip
from .ffmpeg_reader import ffmpeg_parse_infos
try:
    from IPython.display import HTML
    ipython_available = True

    class HTML2(HTML):

        def __add__(self, other):
            return HTML2(self.data + other.data)
except ImportError:
    ipython_available = False
sorry = "Sorry, seems like your browser doesn't support HTML5 audio/video"
templates = {'audio': "<audio controls><source %(options)s  src='data:audio/%(ext)s;base64,%(data)s'>" + sorry + '</audio>', 'image': "<img %(options)s src='data:image/%(ext)s;base64,%(data)s'>", 'video': "<video %(options)ssrc='data:video/%(ext)s;base64,%(data)s' controls>" + sorry + '</video>'}


    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")

    """
    pass
    =========

    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")

    """
    pass


    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")
    """
    pass
    =========

    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")
    """
    pass
