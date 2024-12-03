import numpy as np

def fadein(clip, duration, initial_color=None):
    """
    Makes the clip progressively appear from some color (black by default),
    over ``duration`` seconds at the beginning of the clip. Can be used for
    masks too, where the initial color must be a number between 0 and 1.
    For cross-fading (progressive appearance or disappearance of a clip
    over another clip, see ``composition.crossfade``
    """
    if initial_color is None:
        initial_color = 0 if clip.ismask else [0, 0, 0]
    
    def fade(t):
        if t >= duration:
            return 1.0
        else:
            return 1.0 * t / duration
    
    def make_frame(t):
        fade_factor = fade(t)
        if clip.ismask:
            return np.interp(fade_factor, [0, 1], [initial_color, clip.get_frame(t)])
        else:
            return np.array(
                [i * fade_factor + (1 - fade_factor) * initial_color[j] 
                 for j, i in enumerate(clip.get_frame(t))]
            ).astype('uint8')
    
    return clip.fl(make_frame, apply_to=['mask', 'audio'])
