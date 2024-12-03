import numpy as np

def supersample(clip, d, nframes):
    """ Replaces each frame at time t by the mean of `nframes` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur."""
    def make_frame(t):
        tt = np.linspace(t-d, t+d, nframes)
        return np.mean([clip.get_frame(t) for t in tt], axis=0)
    
    return clip.fl(make_frame)
