import numpy as np

def mask_color(clip, color=None, thr=0, s=1):
    """ Returns a new clip with a mask for transparency where the original
    clip is of the given color.

    You can also have a "progressive" mask by specifying a non-nul distance
    threshold thr. In this case, if the distance between a pixel and the given
    color is d, the transparency will be 

    d**s / (thr**s + d**s)

    which is 1 when d>>thr and 0 for d<<thr, the stiffness of the effect being
    parametrized by s
    """
    if color is None:
        raise ValueError("Color must be specified")

    def make_mask(get_frame, t):
        frame = get_frame(t)
        if frame.ndim == 2:
            # Grayscale image
            distances = np.abs(frame - color[0])
        else:
            # RGB image
            distances = np.sqrt(np.sum((frame - color) ** 2, axis=2))

        if thr == 0:
            mask = distances > 0
        else:
            mask = distances ** s / (thr ** s + distances ** s)

        return mask.astype('float32')

    mask = clip.fl(make_mask)
    return mask.set_ismask(True)
