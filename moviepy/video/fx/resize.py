resize_possible = True
try:
    import cv2
    import numpy as np
    resizer.origin = 'cv2'
except ImportError:
    try:
        from PIL import Image
        import numpy as np
        resizer.origin = 'PIL'
    except ImportError:
        try:
            from scipy.misc import imresize
            resizer = lambda pic, newsize: imresize(pic, map(int, newsize[::-1]))
            resizer.origin = 'Scipy'
        except ImportError:
            resize_possible = False
from moviepy.decorators import apply_to_mask

def resize(clip, newsize=None, height=None, width=None, apply_to_mask=True):
    """ 
    Returns a video clip that is a resized version of the clip.
    
    Parameters
    ------------
    
    newsize:
      Can be either 
        - ``(width,height)`` in pixels or a float representing
        - A scaling factor, like 0.5
        - A function of time returning one of these.
            
    width:
      width of the new clip in pixel. The height is then computed so
      that the width/height ratio is conserved. 
            
    height:
      height of the new clip in pixel. The width is then computed so
      that the width/height ratio is conserved.
    
    Examples
    ----------
             
    >>> myClip.resize( (460,720) ) # New resolution: (460,720)
    >>> myClip.resize(0.6) # width and heigth multiplied by 0.6
    >>> myClip.resize(width=800) # height computed automatically.
    >>> myClip.resize(lambda t : 1+0.02*t) # slow swelling of the clip
    
    """
    if not resize_possible:
        raise ImportError("Neither OpenCV nor PIL nor Scipy are installed. Resizing is not possible.")

    w, h = clip.size

    if newsize is not None:
        if callable(newsize):
            def new_func(get_frame, t):
                new_size = newsize(t)
                if isinstance(new_size, (int, float)):
                    ratio = new_size
                    new_w, new_h = int(w * ratio), int(h * ratio)
                else:
                    new_w, new_h = new_size
                frame = get_frame(t)
                return resizer(frame, (new_w, new_h))

            new_clip = clip.fl(new_func)
            if apply_to_mask and clip.mask is not None:
                new_clip.mask = resize(clip.mask, newsize, apply_to_mask=False)
            return new_clip

        elif isinstance(newsize, (int, float)):
            ratio = newsize
            newsize = (int(w * ratio), int(h * ratio))
        else:
            newsize = tuple(map(int, newsize))
    elif height is not None:
        ratio = height / h
        newsize = (int(w * ratio), height)
    elif width is not None:
        ratio = width / w
        newsize = (width, int(h * ratio))
    else:
        raise ValueError("Either newsize, width, or height must be specified")

    def resize_frame(frame):
        return resizer(frame, newsize)

    new_clip = clip.fl_image(resize_frame)

    if apply_to_mask and clip.mask is not None:
        new_clip.mask = resize(clip.mask, newsize=newsize, apply_to_mask=False)

    return new_clip
if not resize_possible:
    doc = resize.__doc__
    resize.__doc__ = doc
