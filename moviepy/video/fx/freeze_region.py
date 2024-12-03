from moviepy.decorators import apply_to_mask
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from .crop import crop

def freeze_region(clip, t=0, region=None, outside_region=None, mask=None):
    """ Freezes one region of the clip while the rest remains animated.
    
    You can choose one of three methods by providing either `region`,
    `outside_region`, or `mask`.

    Parameters
    -----------

    t
      Time at which to freeze the freezed region.

    region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be freezed. You can provide outside_region or mask instead.

    outside_region
      A tuple (x1, y1, x2, y2) defining the region of the screen (in pixels)
      which will be the only non-freezed region.

    mask
      If not None, will overlay a freezed version of the clip on the current clip,
      with the provided mask. In other words, the "visible" pixels in the mask
      indicate the freezed region in the final picture.

    """
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from .crop import crop

    frozen_clip = clip.to_ImageClip(t)
    
    if region is not None:
        x1, y1, x2, y2 = region
        frozen_region = frozen_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
        frozen_region = frozen_region.set_position((x1, y1))
        return CompositeVideoClip([clip, frozen_region])
    
    elif outside_region is not None:
        x1, y1, x2, y2 = outside_region
        frozen_clip = frozen_clip.crop(x1=0, y1=0, x2=clip.w, y2=y1).set_position((0, 0))
        frozen_clip = CompositeVideoClip([frozen_clip,
                                          frozen_clip.crop(x1=0, y1=y2, x2=clip.w, y2=clip.h).set_position((0, y2)),
                                          frozen_clip.crop(x1=0, y1=y1, x2=x1, y2=y2).set_position((0, y1)),
                                          frozen_clip.crop(x1=x2, y1=y1, x2=clip.w, y2=y2).set_position((x2, y1))])
        return CompositeVideoClip([clip, frozen_clip])
    
    elif mask is not None:
        return CompositeVideoClip([clip, frozen_clip.set_mask(mask)])
    
    else:
        raise ValueError("You must provide either region, outside_region, or mask")
