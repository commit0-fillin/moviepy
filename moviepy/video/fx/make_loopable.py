import moviepy.video.compositing.transitions as transfx
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

def make_loopable(clip, cross):
    """
    Makes the clip fade in progressively at its own end, this way
    it can be looped indefinitely. ``cross`` is the duration in seconds
    of the fade-in.
    """
    d = clip.duration
    
    def make_frame(t):
        if t < d - cross:
            return clip.get_frame(t)
        else:
            fade_in_frame = clip.get_frame(t - d + cross)
            fade_out_frame = clip.get_frame(t)
            blend_factor = (t - (d - cross)) / cross
            return fade_out_frame * (1 - blend_factor) + fade_in_frame * blend_factor
    
    return clip.set_make_frame(make_frame)
