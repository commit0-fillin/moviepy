"""
Here is the current catalogue. These are meant
to be used with clip.fx. There are available as transfx.crossfadein etc.
if you load them with ``from moviepy.editor import *``
"""
from moviepy.decorators import add_mask_if_none, requires_duration
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from .CompositeVideoClip import CompositeVideoClip

@requires_duration
@add_mask_if_none
def crossfadein(clip, duration):
    """ Makes the clip appear progressively, over ``duration`` seconds.
    Only works when the clip is included in a CompositeVideoClip.
    """
    def make_frame(t):
        if t >= duration:
            return clip.get_frame(t)
        else:
            fading = clip.get_frame(t)
            mask = np.array([(t / duration)] * 3).reshape(1, 1, 3)
            return fading * mask

    new_clip = clip.set_make_frame(make_frame)
    new_clip.duration = clip.duration
    new_clip.end = clip.end

    if clip.mask is not None:
        new_clip.mask = clip.mask.fx(crossfadein, duration)

    return new_clip

@requires_duration
@add_mask_if_none
def crossfadeout(clip, duration):
    """ Makes the clip disappear progressively, over ``duration`` seconds.
    Only works when the clip is included in a CompositeVideoClip.
    """
    def make_frame(t):
        if t <= clip.duration - duration:
            return clip.get_frame(t)
        else:
            fading = clip.get_frame(t)
            mask = np.array([(clip.duration - t) / duration] * 3).reshape(1, 1, 3)
            return fading * mask

    new_clip = clip.set_make_frame(make_frame)
    new_clip.duration = clip.duration
    new_clip.end = clip.end

    if clip.mask is not None:
        new_clip.mask = clip.mask.fx(crossfadeout, duration)

    return new_clip


    clip
      A video clip.

    duration
      Time taken for the clip to be fully visible

    side
      Side of the screen where the clip comes from. One of
      'top' | 'bottom' | 'left' | 'right'

    Examples
    ===========

    clip
      A video clip.

    duration
      Time taken for the clip to be fully visible

    side
      Side of the screen where the clip comes from. One of
      'top' | 'bottom' | 'left' | 'right'

    Examples
    =========

    >>> from moviepy.editor import *
    >>> clips = [... make a list of clips]
    >>> slided_clips = [CompositeVideoClip([
                            clip.fx(transfx.slide_in, duration=1, side='left')])
                        for clip in clips]
    >>> final_clip = concatenate( slided_clips, padding=-1)

    """
    pass


    clip
      A video clip.

    duration
      Time taken for the clip to fully disappear.

    side
      Side of the screen where the clip goes. One of
      'top' | 'bottom' | 'left' | 'right'

    Examples
    ===========

    clip
      A video clip.

    duration
      Time taken for the clip to fully disappear.

    side
      Side of the screen where the clip goes. One of
      'top' | 'bottom' | 'left' | 'right'

    Examples
    =========

    >>> from moviepy.editor import *
    >>> clips = [... make a list of clips]
    >>> slided_clips = [CompositeVideoClip([
                            clip.fx(transfx.slide_out, duration=1, side='left')])
                        for clip in clips]
    >>> final_clip = concatenate( slided_clips, padding=-1)

    """
    pass

@requires_duration
def make_loopable(clip, cross_duration):
    """ Makes the clip fade in progressively at its own end, this way
    it can be looped indefinitely. ``cross`` is the duration in seconds
    of the fade-in.  """
    d = clip.duration
    def make_frame(t):
        if t < d - cross_duration:
            return clip.get_frame(t)
        else:
            fade_in_frame = clip.get_frame(t - d + cross_duration)
            fade_out_frame = clip.get_frame(t)
            blend_factor = (t - (d - cross_duration)) / cross_duration
            return fade_out_frame * (1 - blend_factor) + fade_in_frame * blend_factor

    return clip.set_make_frame(make_frame)
