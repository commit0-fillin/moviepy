from moviepy.decorators import apply_to_mask

@apply_to_mask
def even_size(clip):
    """ 
    Crops the clip to make dimensions even.
    """
    w, h = clip.w, clip.h
    new_w = w if w % 2 == 0 else w - 1
    new_h = h if h % 2 == 0 else h - 1
    
    if new_w == w and new_h == h:
        return clip
    
    return clip.crop(x_center=w/2, y_center=h/2, width=new_w, height=new_h)
