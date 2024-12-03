def invert_colors(clip):
    """ Returns the color-inversed clip.

    The values of all pixels are replaced with (255-v) or (1-v) for masks 
    Black becomes white, green becomes purple, etc.
    """
    return clip.image_transform(lambda frame: 255 - frame)
