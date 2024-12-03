import numpy as np
from moviepy.decorators import audio_video_fx, requires_duration

@audio_video_fx
@requires_duration
def audio_fadeout(clip, duration):
    """ Return a sound clip where the sound fades out progressively
        over ``duration`` seconds at the end of the clip. """
    def faded_audio(get_frame, t):
        # Original audio at time t
        audio = get_frame(t)
        
        # Fade factor
        if t >= clip.duration - duration:
            factor = (clip.duration - t) / duration
        else:
            factor = 1.0
        
        # Apply fade
        return audio * factor

    return clip.fl(faded_audio, keep_duration=True)
