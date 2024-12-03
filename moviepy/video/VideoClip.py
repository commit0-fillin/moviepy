"""
This module implements VideoClip (base class for video clips) and its
main subclasses:
- Animated clips:     VideofileClip, ImageSequenceClip
- Static image clips: ImageClip, ColorClip, TextClip,
"""
import os
import subprocess as sp
import tempfile
import warnings
import numpy as np
import proglog
from imageio import imread, imsave
from ..Clip import Clip
from ..compat import DEVNULL, string_types
from ..config import get_setting
from ..decorators import add_mask_if_none, apply_to_mask, convert_masks_to_RGB, convert_to_seconds, outplace, requires_duration, use_clip_fps_by_default
from ..tools import deprecated_version_of, extensions_dict, find_extension, is_string, subprocess_call
from .io.ffmpeg_writer import ffmpeg_write_video
from .io.gif_writers import write_gif, write_gif_with_image_io, write_gif_with_tempfiles
from .tools.drawing import blit

class VideoClip(Clip):
    """Base class for video clips.

    See ``VideoFileClip``, ``ImageClip`` etc. for more user-friendly
    classes.


    Parameters
    -----------

    ismask
      `True` if the clip is going to be used as a mask.


    Attributes
    ----------

    size
      The size of the clip, (width,heigth), in pixels.

    w, h
      The width and height of the clip, in pixels.

    ismask
      Boolean set to `True` if the clip is a mask.

    make_frame
      A function ``t-> frame at time t`` where ``frame`` is a
      w*h*3 RGB array.

    mask (default None)
      VideoClip mask attached to this clip. If mask is ``None``,
                The video clip is fully opaque.

    audio (default None)
      An AudioClip instance containing the audio of the video clip.

    pos
      A function ``t->(x,y)`` where ``x,y`` is the position
      of the clip when it is composed with other clips.
      See ``VideoClip.set_pos`` for more details

    relative_pos
      See variable ``pos``.

    """

    def __init__(self, make_frame=None, ismask=False, duration=None, has_constant_size=True):
        Clip.__init__(self)
        self.mask = None
        self.audio = None
        self.pos = lambda t: (0, 0)
        self.relative_pos = False
        if make_frame:
            self.make_frame = make_frame
            self.size = self.get_frame(0).shape[:2][::-1]
        self.ismask = ismask
        self.has_constant_size = has_constant_size
        if duration is not None:
            self.duration = duration
            self.end = duration

    @convert_to_seconds(['t'])
    @convert_masks_to_RGB
    def save_frame(self, filename, t=0, withmask=True):
        """ Save a clip's frame to an image file.

        Saves the frame of clip corresponding to time ``t`` in
        'filename'. ``t`` can be expressed in seconds (15.35), in
        (min, sec), in (hour, min, sec), or as a string: '01:03:05.35'.

        If ``withmask`` is ``True`` the mask is saved in
        the alpha layer of the picture (only works with PNGs).

        """
        from moviepy.video.io.ffmpeg_writer import ffmpeg_write_image
        if withmask and self.mask is None:
            withmask = False
        
        frame = self.get_frame(t)
        if withmask:
            mask = 255 * self.mask.get_frame(t)
            frame = np.dstack([frame, mask]).astype('uint8')
        else:
            frame = frame.astype('uint8')
        
        ffmpeg_write_image(filename, frame)


        >>> from moviepy.editor import VideoFileClip
        >>> clip = VideoFileClip("myvideo.mp4").subclip(100,120)
        >>> clip.write_videofile("my_new_video.mp4")
        >>> clip.close()

        """
        pass
        ========

        >>> from moviepy.editor import VideoFileClip
        >>> clip = VideoFileClip("myvideo.mp4").subclip(100,120)
        >>> clip.write_videofile("my_new_video.mp4")
        >>> clip.close()

        """
        pass

    @requires_duration
    @use_clip_fps_by_default
    @convert_masks_to_RGB
    def write_images_sequence(self, nameformat, fps=None, verbose=True, withmask=True, logger='bar'):
        """ Writes the videoclip to a sequence of image files."""
        logger = proglog.default_bar_logger(logger)
        
        if fps is None:
            fps = self.fps

        if withmask and self.mask is None:
            withmask = False

        tt = np.arange(0, self.duration, 1.0/fps)
        
        filenames = []
        for i, t in logger.iter_bar(t=list(enumerate(tt))):
            name = nameformat % i
            filenames.append(name)
            self.save_frame(name, t, withmask=withmask)

        return filenames

    @requires_duration
    @convert_masks_to_RGB
    def write_gif(self, filename, fps=None, program='imageio', opt='nq', fuzz=1, verbose=True, loop=0, dispose=False, colors=None, tempfiles=False, logger='bar'):
        """ Write the VideoClip to a GIF file."""
        from moviepy.video.io.gif_writers import write_gif

        if fps is None:
            fps = self.fps

        write_gif(self, filename, fps=fps, program=program, opt=opt, fuzz=fuzz,
                  verbose=verbose, loop=loop, dispose=dispose, colors=colors,
                  tempfiles=tempfiles, logger=logger)

    def subfx(self, fx, ta=0, tb=None, **kwargs):
        """Apply a transformation to a part of the clip."""
        left = None
        center = None
        right = None

        if ta > 0:
            left = self.subclip(0, ta)
        if tb is None:
            center = self.subclip(ta).fx(fx, **kwargs)
        else:
            center = self.subclip(ta, tb).fx(fx, **kwargs)
            right = self.subclip(tb)

        clips = [c for c in [left, center, right] if c is not None]
        return concatenate_videoclips(clips)

    def fl_image(self, image_func, apply_to=None):
        """
        Modifies the images of a clip by replacing the frame
        `get_frame(t)` by another frame,  `image_func(get_frame(t))`
        """
        return self.fl(lambda gf, t: image_func(gf(t)), apply_to)

    def blit_on(self, picture, t):
        """
        Returns the result of the blit of the clip's frame at time `t`
        on the given `picture`, the position of the clip being given
        by the clip's ``pos`` attribute. Meant for compositing.
        """
        from moviepy.video.tools.drawing import blit
        
        frame = self.get_frame(t)
        if self.mask is None:
            mask = None
        else:
            mask = self.mask.get_frame(t)
        
        pos = self.pos(t) if callable(self.pos) else self.pos
        
        return blit(frame, picture, pos, mask=mask, ismask=self.ismask)

    def add_mask(self):
        """Add a mask VideoClip to the VideoClip.

        Returns a copy of the clip with a completely opaque mask
        (made of ones). This makes computations slower compared to
        having a None mask but can be useful in many cases. Choose

        Set ``constant_size`` to  `False` for clips with moving
        image size.
        """
        if self.has_constant_size:
            mask = ColorClip(self.size, 1.0, ismask=True)
            return self.set_mask(mask.set_duration(self.duration))
        else:
            mask = VideoClip(ismask=True).set_get_frame(
                lambda t: np.ones(self.get_frame(t).shape[:2], dtype=float))
            return self.set_mask(mask.set_duration(self.duration))

    def on_color(self, size=None, color=(0, 0, 0), pos=None, col_opacity=None):
        """Place the clip on a colored background."""
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

        if size is None:
            size = self.size
        if pos is None:
            pos = 'center'
        colorclip = ColorClip(size, color)

        if col_opacity is not None:
            colorclip = colorclip.set_opacity(col_opacity)

        if self.mask is None:
            return CompositeVideoClip([colorclip, self.set_position(pos)])
        else:
            return CompositeVideoClip([
                colorclip,
                self.set_position(pos),
                self.mask.set_position(pos)
            ])

    @outplace
    def set_make_frame(self, mf):
        """Change the clip's ``get_frame``."""
        self.make_frame = mf

    @outplace
    def set_audio(self, audioclip):
        """Attach an AudioClip to the VideoClip."""
        self.audio = audioclip

    @outplace
    def set_mask(self, mask):
        """Set the clip's mask."""
        assert isinstance(mask, VideoClip)
        self.mask = mask

    @add_mask_if_none
    @outplace
    def set_opacity(self, op):
        """Set the opacity/transparency level of the clip."""
        self.mask = self.mask.fl_image(lambda pic: op * pic)

    @apply_to_mask
    @outplace
    def set_position(self, pos, relative=False):
        """Set the clip's position in compositions."""
        self.relative_pos = relative
        if hasattr(pos, '__call__'):
            self.pos = pos
        else:
            self.pos = lambda t: pos

    @convert_to_seconds(['t'])
    def to_ImageClip(self, t=0, with_mask=True, duration=None):
        """Returns an ImageClip made out of the clip's frame at time ``t``."""
        new_clip = ImageClip(self.get_frame(t), ismask=self.ismask, duration=duration)
        if with_mask and self.mask is not None:
            new_clip.mask = self.mask.to_ImageClip(t)
        return new_clip

    def to_mask(self, canal=0):
        """Return a mask video clip made from the clip."""
        if self.ismask:
            return self
        else:
            newclip = self.fl_image(lambda pic: 1.0 * pic[:, :, canal] / 255)
            newclip.ismask = True
            return newclip

    def to_RGB(self):
        """Return a non-mask video clip made from the mask video clip."""
        if self.ismask:
            f = lambda pic: np.dstack(3 * [255 * pic]).astype('uint8')
            newclip = self.fl_image(f)
            newclip.ismask = False
            return newclip
        else:
            return self

    @outplace
    def without_audio(self):
        """Remove the clip's audio."""
        self.audio = None

    @outplace
    def afx(self, fun, *a, **k):
        """Transform the clip's audio."""
        self.audio = self.audio.fx(fun, *a, **k) if self.audio else None
