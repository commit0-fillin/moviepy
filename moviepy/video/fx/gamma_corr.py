import numpy as np

def gamma_corr(clip, gamma):
    """ Gamma-correction of a video clip 
    
    :param clip: A VideoClip object
    :param gamma: Float, the gamma correction factor
    :return: A new VideoClip with gamma correction applied
    """
    def apply_gamma(get_frame, t):
        frame = get_frame(t)
        return np.power(frame / 255.0, gamma) * 255.0

    return clip.fl(apply_gamma)
