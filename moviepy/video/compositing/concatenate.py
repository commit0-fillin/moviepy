import numpy as np
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.tools import deprecated_version_of
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.on_color import on_color
from moviepy.video.VideoClip import ColorClip, VideoClip
try:
    reduce
except NameError:
    from functools import reduce

def concatenate_videoclips(clips, method='chain', transition=None, bg_color=None, ismask=False, padding=0):
    """ Concatenates several video clips

    Returns a video clip made by clip by concatenating several video clips.
    (Concatenated means that they will be played one after another).

    There are two methods:

    - method="chain": will produce a clip that simply outputs
      the frames of the succesive clips, without any correction if they are
      not of the same size of anything. If none of the clips have masks the
      resulting clip has no mask, else the mask is a concatenation of masks
      (using completely opaque for clips that don't have masks, obviously).
      If you have clips of different size and you want to write directly the
      result of the concatenation to a file, use the method "compose" instead.

    - method="compose", if the clips do not have the same
      resolution, the final resolution will be such that no clip has
       to be resized.
       As a consequence the final clip has the height of the highest
       clip and the width of the widest clip of the list. All the
       clips with smaller dimensions will appear centered. The border
       will be transparent if mask=True, else it will be of the
       color specified by ``bg_color``.

    The clip with the highest FPS will be the FPS of the result clip.

    Parameters
    -----------
    clips
      A list of video clips which must all have their ``duration``
      attributes set.
    method
      "chain" or "compose": see above.
    transition
      A clip that will be played between each two clips of the list.

    bg_color
      Only for method='compose'. Color of the background.
      Set to None for a transparent clip

    padding
      Only for method='compose'. Duration during two consecutive clips.
      Note that for negative padding, a clip will partly play at the same
      time as the clip it follows (negative padding is cool for clips who fade
      in on one another). A non-null padding automatically sets the method to
      `compose`.

    """
    if padding != 0:
        method = 'compose'
    
    if method == 'chain':
        return _concatenate_chain(clips, transition, ismask)
    elif method == 'compose':
        return _concatenate_compose(clips, transition, bg_color, ismask, padding)
    else:
        raise ValueError("Method must be 'chain' or 'compose'")

def _concatenate_chain(clips, transition, ismask):
    """Helper function for concatenate_videoclips using chain method"""
    if transition is not None:
        clips = [clip.crossfadein(transition.duration) if i != 0 else clip 
                 for i, clip in enumerate(clips)]
        clips = reduce(lambda x, y: x + [transition, y], clips)
    
    durations = [c.duration for c in clips]
    tt = np.cumsum([0] + durations)  # start times, and end time
    
    def make_frame(t):
        i = max([i for i, e in enumerate(tt) if e <= t])
        return clips[i].get_frame(t - tt[i])
    
    result = VideoClip(make_frame, duration=tt[-1])
    
    if any(clip.mask for clip in clips):
        masks = [c.mask if (c.mask is not None) else ColorClip(c.size, 1.0, ismask=True)
                 for c in clips]
        result.mask = concatenate_videoclips(masks, method="chain", ismask=True)
    
    result.fps = max([clip.fps for clip in clips if hasattr(clip, 'fps') and clip.fps is not None])
    return result

def _concatenate_compose(clips, transition, bg_color, ismask, padding):
    """Helper function for concatenate_videoclips using compose method"""
    w = max(clip.w for clip in clips)
    h = max(clip.h for clip in clips)
    
    tt = np.cumsum([0] + [clip.duration for clip in clips])
    
    # Handle padding
    if padding < 0:
        tt = tt[:-1] + [t + padding for t in tt[1:]]
    elif padding > 0:
        tt = [t + padding * i for i, t in enumerate(tt)]
    
    def make_frame(t):
        i = max([i for i, e in enumerate(tt) if e <= t])
        clip = clips[i]
        t1 = t - tt[i]
        frame = clip.get_frame(t1)
        if clip.w != w or clip.h != h:
            frame = np.pad(frame, ((0, h - clip.h), (0, w - clip.w), (0, 0)), 
                           mode='constant', constant_values=bg_color or 0)
        return frame
    
    result = VideoClip(make_frame, duration=tt[-1])
    
    if ismask:
        result = result.to_mask()
    
    if transition is not None:
        result = CompositeVideoClip([result] + [
            transition.set_start(t).set_position((0, 0))
            for t in tt[1:-1]
        ])
    
    result.fps = max([clip.fps for clip in clips if hasattr(clip, 'fps') and clip.fps is not None])
    return result
concatenate = deprecated_version_of(concatenate_videoclips, oldname='concatenate')
