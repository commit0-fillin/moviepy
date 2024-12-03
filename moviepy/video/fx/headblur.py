import numpy as np
try:
    import cv2
    headblur_possible = True
    if cv2.__version__ >= '3.0.0':
        cv2.CV_AA = cv2.LINE_AA
except:
    headblur_possible = False

def headblur(clip, fx, fy, r_zone, r_blur=None):
    """
    Returns a filter that will blurr a moving part (a head ?) of
    the frames. The position of the blur at time t is
    defined by (fx(t), fy(t)), the radius of the blurring
    by ``r_zone`` and the intensity of the blurring by ``r_blur``.
    Requires OpenCV for the circling and the blurring.
    Automatically deals with the case where part of the image goes
    offscreen.
    """
    if not headblur_possible:
        raise ImportError("OpenCV is not installed. Please install it to use the headblur effect.")

    if r_blur is None:
        r_blur = r_zone // 2

    def fl(gf, t):
        img = gf(t)
        h, w = img.shape[:2]
        x = int(fx(t))
        y = int(fy(t))

        # Create a mask for the blur area
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (x, y), r_zone, (255, 255, 255), -1, lineType=cv2.CV_AA)

        # Apply Gaussian blur to the image
        blurred = cv2.GaussianBlur(img, (2*r_blur+1, 2*r_blur+1), 0)

        # Blend the original image and the blurred image using the mask
        result = np.where(mask[:,:,np.newaxis] == 255, blurred, img)

        return result

    return clip.fl(fl)
if not headblur_possible:
    doc = headblur.__doc__
    headblur.__doc__ = doc
