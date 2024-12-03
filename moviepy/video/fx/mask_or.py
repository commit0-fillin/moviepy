import numpy as np
from ..VideoClip import ImageClip

def mask_or(clip, other_clip):
    """ Returns the logical 'or' (max) between two masks.
        other_clip can be a mask clip or a picture (np.array).
        The result has the duration of 'clip' (if it has any)
    """
    if isinstance(other_clip, np.ndarray):
        other_clip = ImageClip(other_clip, ismask=True)
    
    def combine_masks(t):
        mask1 = clip.get_frame(t)
        mask2 = other_clip.get_frame(t) if hasattr(other_clip, 'get_frame') else other_clip.img
        return np.maximum(mask1, mask2)
    
    result = clip.fl_image(lambda frame: combine_masks(0))
    result.ismask = True
    
    if hasattr(clip, 'duration'):
        result = result.set_duration(clip.duration)
    
    return result
