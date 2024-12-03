import numpy as np
from moviepy.decorators import requires_duration

@requires_duration
def fadeout(clip, duration, final_color=None):
    """
    Makes the clip progressively fade to some color (black by default),
    over ``duration`` seconds at the end of the clip. Can be used for
    masks too, where the final color must be a number between 0 and 1.
    For cross-fading (progressive appearance or disappearance of a clip
    over another clip, see ``composition.crossfade``
    """
    if final_color is None:
        final_color = 0 if clip.ismask else (0, 0, 0)

    def make_frame(t):
        original = clip.get_frame(t)
        
        if t >= clip.duration - duration:
            factor = (t - (clip.duration - duration)) / duration
            return np.multiply(1.0 - factor, original) + np.multiply(factor, final_color)
        else:
            return original

    return clip.set_make_frame(make_frame)
