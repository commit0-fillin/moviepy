import numpy as np
from moviepy.decorators import apply_to_mask
from moviepy.video.VideoClip import ImageClip

@apply_to_mask
def margin(clip, mar=None, left=0, right=0, top=0, bottom=0, color=(0, 0, 0), opacity=1.0):
    """
    Draws an external margin all around the frame.
    
    :param mar: if not ``None``, then the new clip has a margin of
        size ``mar`` in pixels on the left, right, top, and bottom.
        
    :param left, right, top, bottom: width of the margin in pixel
        in these directions.
        
    :param color: color of the margin.
    
    :param opacity: opacity of the margin.
    
    """
    if mar is not None:
        left = right = top = bottom = mar
    
    def make_bg(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        new_w = w + left + right
        new_h = h + top + bottom
        shape = (new_h, new_w) if frame.ndim == 2 else (new_h, new_w, frame.shape[2])
        bg = np.zeros(shape, dtype=frame.dtype)
        if isinstance(color, (int, float)):
            bg.fill(color)
        else:
            bg[:, :] = color
        bg[top:top+h, left:left+w] = frame
        return bg
    
    new_clip = clip.fl(make_bg)
    
    if opacity != 1:
        new_clip = new_clip.set_opacity(opacity)
    
    return new_clip
