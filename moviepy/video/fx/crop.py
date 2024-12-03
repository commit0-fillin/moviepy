def crop(clip, x1=None, y1=None, x2=None, y2=None, width=None, height=None, x_center=None, y_center=None):
    """
    Returns a new clip in which just a rectangular subregion of the
    original clip is conserved. x1,y1 indicates the top left corner and
    x2,y2 is the lower right corner of the croped region.
    All coordinates are in pixels. Float numbers are accepted.
    
    To crop an arbitrary rectangle:
    
    >>> crop(clip, x1=50, y1=60, x2=460, y2=275)
    
    Only remove the part above y=30:
    
    >>> crop(clip, y1=30)
    
    Crop a rectangle that starts 10 pixels left and is 200px wide
    
    >>> crop(clip, x1=10, width=200)
    
    Crop a rectangle centered in x,y=(300,400), width=50, height=150 :
    
    >>> crop(clip,  x_center=300 , y_center=400,
                        width=50, height=150)
    
    Any combination of the above should work, like for this rectangle
    centered in x=300, with explicit y-boundaries:
    
    >>> crop(x_center=300, width=400, y1=100, y2=600)
    
    """
    w, h = clip.w, clip.h

    # Calculate x1 and x2
    if x1 is None:
        if x_center is not None:
            if width is not None:
                x1 = x_center - width / 2
            elif x2 is not None:
                x1 = 2 * x_center - x2
            else:
                x1 = 0
        else:
            x1 = 0
    if x2 is None:
        if width is not None:
            x2 = x1 + width
        else:
            x2 = w

    # Calculate y1 and y2
    if y1 is None:
        if y_center is not None:
            if height is not None:
                y1 = y_center - height / 2
            elif y2 is not None:
                y1 = 2 * y_center - y2
            else:
                y1 = 0
        else:
            y1 = 0
    if y2 is None:
        if height is not None:
            y2 = y1 + height
        else:
            y2 = h

    # Ensure coordinates are within bounds
    x1 = max(0, min(x1, w))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h))
    y2 = max(0, min(y2, h))

    # Create the cropped clip
    return clip.fl_image(lambda img: img[int(y1):int(y2), int(x1):int(x2)])
