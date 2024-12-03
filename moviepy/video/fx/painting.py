painting_possible = True
try:
    from skimage.filter import sobel
except:
    try:
        from scipy.ndimage.filters import sobel
    except:
        painting_possible = False
import numpy as np

def to_painting(image, saturation=1.4, black=0.006):
    """ transforms any photo into some kind of painting """
    if not painting_possible:
        raise ImportError("Scikit-image or Scipy is required for the painting effect.")
    
    # Convert image to float and ensure it's in RGB
    img = np.array(image).astype(float) / 255
    if img.ndim == 2:
        img = np.dstack((img, img, img))
    
    # Increase saturation
    img = (img - 0.5) * saturation + 0.5
    img = np.clip(img, 0, 1)
    
    # Apply edge detection
    edges = sobel(img.mean(axis=2))
    
    # Create painting effect
    painting = img * (1 - black * (edges > 0.4))
    
    # Convert back to uint8
    return (np.clip(painting, 0, 1) * 255).astype('uint8')

def painting(clip, saturation=1.4, black=0.006):
    """
    Transforms any photo into some kind of painting. Saturation
    tells at which point the colors of the result should be
    flashy. ``black`` gives the anount of black lines wanted.
    Requires Scikit-image or Scipy installed.
    """
    return clip.fl_image(lambda img: to_painting(img, saturation, black))
if not painting_possible:
    doc = painting.__doc__
    painting.__doc__ = doc
