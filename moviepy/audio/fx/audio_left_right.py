import numpy as np

def audio_left_right(audioclip, left=1, right=1, merge=False):
    """
    For a stereo audioclip, this function enables to change the volume
    of the left and right channel separately (with the factors `left`
    and `right`)
    Makes a stereo audio clip in which the volume of left and right
    is controllable

    Parameters:
    -----------
    audioclip : AudioClip
        The input audio clip (must be stereo)
    left : float, optional
        The volume factor for the left channel (default is 1)
    right : float, optional
        The volume factor for the right channel (default is 1)
    merge : bool, optional
        If True, merge the channels into a mono track (default is False)

    Returns:
    --------
    AudioClip
        A new AudioClip with adjusted left and right channels
    """
    def adjust_channels(get_frame, t):
        frame = get_frame(t)
        if frame.ndim == 1:
            raise ValueError("Input audio clip must be stereo (2 channels)")
        
        adjusted = np.array([frame[:, 0] * left, frame[:, 1] * right]).T
        
        if merge:
            return np.mean(adjusted, axis=1)
        return adjusted

    return audioclip.fl(adjust_channels)
