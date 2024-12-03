"""
This module implements all the functions to communicate with other Python
modules (PIL, matplotlib, mayavi, etc.)
"""
import numpy as np
import matplotlib.pyplot as plt

def PIL_to_npimage(im):
    """ Transforms a PIL/Pillow image into a numpy RGB(A) image.
        Actually all this do is returning numpy.array(im)."""
    return np.array(im)

def mplfig_to_npimage(fig):
    """ Converts a matplotlib figure to a RGB frame after updating the canvas"""
    fig.canvas.draw()  # Update the canvas
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    buf.shape = (h, w, 3)
    return buf
