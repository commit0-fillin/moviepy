import numpy as np

def blackwhite(clip, RGB=None, preserve_luminosity=True):
    """ Desaturates the picture, makes it black and white.
    Parameter RGB allows to set weights for the different color
    channels.
    If RBG is 'CRT_phosphor' a special set of values is used.
    preserve_luminosity maintains the sum of RGB to 1."""
    
    if RGB is None:
        RGB = [1, 1, 1]
    elif RGB == 'CRT_phosphor':
        RGB = [0.2989, 0.5870, 0.1140]
    
    if preserve_luminosity:
        RGB = np.array(RGB) / sum(RGB)
    
    def make_black_and_white(image):
        return np.dot(image[..., :3], RGB).astype('uint8')
    
    return clip.image_transform(make_black_and_white)
