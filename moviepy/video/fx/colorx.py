import numpy as np

def colorx(clip, factor):
    """ multiplies the clip's colors by the given factor, can be used
        to decrease or increase the clip's brightness (is that the
        reight word ?)
    """
    def modify_frame(get_frame, t):
        frame = get_frame(t)
        return np.clip(frame * factor, 0, 255).astype('uint8')
    
    return clip.fl(modify_frame)
