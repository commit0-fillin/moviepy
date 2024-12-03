"""
This module deals with making images (np arrays). It provides drawing
methods that are difficult to do with the existing Python libraries.
"""
import numpy as np

def blit(im1, im2, pos=None, mask=None, ismask=False):
    """ Blit an image over another.
    
    Blits ``im1`` on ``im2`` as position ``pos=(x,y)``, using the
    ``mask`` if provided. If ``im1`` and ``im2`` are mask pictures
    (2D float arrays) then ``ismask`` must be ``True``.
    """
    if pos is None:
        pos = (0, 0)
    
    h1, w1 = im1.shape[:2]
    h2, w2 = im2.shape[:2]
    x, y = pos

    # Ensure the position is within the bounds of im2
    x = max(0, min(x, w2 - 1))
    y = max(0, min(y, h2 - 1))

    # Calculate the overlapping region
    h = min(h1, h2 - y)
    w = min(w1, w2 - x)

    if ismask:
        im2[y:y+h, x:x+w] = im1[:h, :w] if mask is None else mask[:h, :w] * im1[:h, :w]
    else:
        if mask is None:
            im2[y:y+h, x:x+w] = im1[:h, :w]
        else:
            mask = np.dstack((mask, mask, mask)) if im1.ndim == 3 else mask
            im2[y:y+h, x:x+w] = (1 - mask[:h, :w]) * im2[y:y+h, x:x+w] + mask[:h, :w] * im1[:h, :w]

    return im2

def color_gradient(size, p1, p2=None, vector=None, r=None, col1=0, col2=1.0, shape='linear', offset=0):
    """Draw a linear, bilinear, or radial gradient.
    
    The result is a picture of size ``size``, whose color varies
    gradually from color `col1` in position ``p1`` to color ``col2``
    in position ``p2``.
    
    If it is a RGB picture the result must be transformed into
    a 'uint8' array to be displayed normally:
     
     
    Parameters
    ------------      
    
    size
        Size (width, height) in pixels of the final picture/array.
    
    p1, p2
        Coordinates (x,y) in pixels of the limit point for ``col1``
        and ``col2``. The color 'before' ``p1`` is ``col1`` and it
        gradually changes in the direction of ``p2`` until it is ``col2``
        when it reaches ``p2``.
    
    vector
        A vector [x,y] in pixels that can be provided instead of ``p2``.
        ``p2`` is then defined as (p1 + vector).
    
    col1, col2
        Either floats between 0 and 1 (for gradients used in masks)
        or [R,G,B] arrays (for colored gradients).
                         
    shape
        'linear', 'bilinear', or 'circular'.
        In a linear gradient the color varies in one direction,
        from point ``p1`` to point ``p2``.
        In a bilinear gradient it also varies symetrically form ``p1``
        in the other direction.
        In a circular gradient it goes from ``col1`` to ``col2`` in all
        directions.
    
    offset
        Real number between 0 and 1 indicating the fraction of the vector
        at which the gradient actually starts. For instance if ``offset``
        is 0.9 in a gradient going from p1 to p2, then the gradient will
        only occur near p2 (before that everything is of color ``col1``)
        If the offset is 0.9 in a radial gradient, the gradient will
        occur in the region located between 90% and 100% of the radius,
        this creates a blurry disc of radius d(p1,p2).  
    
    Returns
    --------
    
    image
        An Numpy array of dimensions (W,H,ncolors) of type float
        representing the image of the gradient.
        
    
    Examples
    ---------
    
    >>> grad = color_gradient(blabla).astype('uint8')
    
    """
    w, h = size
    
    if vector is not None:
        p2 = (p1[0] + vector[0], p1[1] + vector[1])
    
    if shape == 'linear':
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        if p2 is None:
            p2 = (w-1, h-1)
        
        vector = (p2[0] - p1[0], p2[1] - p1[1])
        norm = np.sqrt(vector[0]**2 + vector[1]**2)
        
        t = ((X - p1[0])*vector[0] + (Y - p1[1])*vector[1]) / (norm**2)
        t = np.clip((t - offset) / (1 - offset), 0, 1)
        
    elif shape == 'bilinear':
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        tx = np.abs(X - p1[0]) / w
        ty = np.abs(Y - p1[1]) / h
        t = np.maximum(tx, ty)
        t = np.clip((t - offset) / (1 - offset), 0, 1)
        
    elif shape == 'circular':
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        if r is None:
            r = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        t = np.sqrt((X - p1[0])**2 + (Y - p1[1])**2) / r
        t = np.clip((t - offset) / (1 - offset), 0, 1)
    
    else:
        raise ValueError("shape must be 'linear', 'bilinear', or 'circular'")

    if isinstance(col1, (int, float)) and isinstance(col2, (int, float)):
        return col1 * (1-t) + col2 * t
    else:
        col1 = np.array(col1)
        col2 = np.array(col2)
        return np.dstack([col1[i] * (1-t) + col2[i] * t for i in range(len(col1))])

def color_split(size, x=None, y=None, p1=None, p2=None, vector=None, col1=0, col2=1.0, grad_width=0):
    """Make an image splitted in 2 colored regions.
    
    Returns an array of size ``size`` divided in two regions called 1 and
    2 in wht follows, and which will have colors col& and col2
    respectively.
    
    Parameters
    -----------
    
    x: (int)
        If provided, the image is splitted horizontally in x, the left
        region being region 1.
            
    y: (int)
        If provided, the image is splitted vertically in y, the top region
        being region 1.
    
    p1,p2:
        Positions (x1,y1),(x2,y2) in pixels, where the numbers can be
        floats. Region 1 is defined as the whole region on the left when
        going from ``p1`` to ``p2``.
    
    p1, vector:
        ``p1`` is (x1,y1) and vector (v1,v2), where the numbers can be
        floats. Region 1 is then the region on the left when starting
        in position ``p1`` and going in the direction given by ``vector``.
         
    gradient_width
        If not zero, the split is not sharp, but gradual over a region of
        width ``gradient_width`` (in pixels). This is preferable in many
        situations (for instance for antialiasing). 
     
    
    Examples
    ---------
    
    >>> size = [200,200]
    >>> # an image with all pixels with x<50 =0, the others =1
    >>> color_split(size, x=50, col1=0, col2=1)
    >>> # an image with all pixels with y<50 red, the others green
    >>> color_split(size, x=50, col1=[255,0,0], col2=[0,255,0])
    >>> # An image splitted along an arbitrary line (see below) 
    >>> color_split(size, p1=[20,50], p2=[25,70] col1=0, col2=1)
            
    """
    w, h = size
    shape = (h, w) if isinstance(col1, (int, float)) else (h, w, len(col1))
    img = np.zeros(shape)
    
    if x is not None:
        if grad_width == 0:
            img[:, :x] = col1
            img[:, x:] = col2
        else:
            img[:, :x-grad_width//2] = col1
            img[:, x+grad_width//2:] = col2
            if grad_width > 0:
                grad = np.linspace(0, 1, grad_width)
                for i in range(grad_width):
                    img[:, x-grad_width//2+i] = col1 * (1-grad[i]) + col2 * grad[i]
    
    elif y is not None:
        if grad_width == 0:
            img[:y, :] = col1
            img[y:, :] = col2
        else:
            img[:y-grad_width//2, :] = col1
            img[y+grad_width//2:, :] = col2
            if grad_width > 0:
                grad = np.linspace(0, 1, grad_width)
                for i in range(grad_width):
                    img[y-grad_width//2+i, :] = col1 * (1-grad[i]) + col2 * grad[i]
    
    elif p1 and (p2 or vector):
        if vector:
            p2 = (p1[0] + vector[0], p1[1] + vector[1])
        
        normal = np.array([-(p2[1] - p1[1]), p2[0] - p1[0]])
        normal = normal / np.linalg.norm(normal)
        
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        pos = np.dstack([X, Y])
        dist = np.dot(pos - p1, normal)
        
        if grad_width == 0:
            img[dist <= 0] = col1
            img[dist > 0] = col2
        else:
            img[dist <= -grad_width/2] = col1
            img[dist > grad_width/2] = col2
            mask = (dist > -grad_width/2) & (dist <= grad_width/2)
            grad = (dist[mask] + grad_width/2) / grad_width
            if isinstance(col1, (int, float)):
                img[mask] = col1 * (1-grad) + col2 * grad
            else:
                for i in range(len(col1)):
                    img[mask, i] = col1[i] * (1-grad) + col2[i] * grad
    
    else:
        raise ValueError("You must provide either x, y, or p1 and (p2 or vector)")
    
    return img

def circle(screensize, center, radius, col1=1.0, col2=0, blur=1):
    """ Draw an image with a circle.
    
    Draws a circle of color ``col1``, on a background of color ``col2``,
    on a screen of size ``screensize`` at the position ``center=(x,y)``,
    with a radius ``radius`` but slightly blurred on the border by ``blur``
    pixels
    """
    w, h = screensize
    shape = (h, w) if isinstance(col1, (int, float)) else (h, w, len(col1))
    img = np.full(shape, col2)
    
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    
    if blur == 0:
        mask = dist_from_center <= radius
        img[mask] = col1
    else:
        inner_circle = dist_from_center <= (radius - blur)
        img[inner_circle] = col1
        
        blur_zone = (dist_from_center > (radius - blur)) & (dist_from_center < (radius + blur))
        blur_factor = (radius + blur - dist_from_center[blur_zone]) / (2 * blur)
        
        if isinstance(col1, (int, float)):
            img[blur_zone] = col1 * blur_factor + col2 * (1 - blur_factor)
        else:
            for i in range(len(col1)):
                img[blur_zone, i] = col1[i] * blur_factor + col2[i] * (1 - blur_factor)
    
    return img
