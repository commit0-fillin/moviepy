from moviepy.decorators import apply_to_audio, apply_to_mask

@apply_to_mask
@apply_to_audio
def speedx(clip, factor=None, final_duration=None):
    """
    Returns a clip playing the current clip but at a speed multiplied
    by ``factor``. Instead of factor one can indicate the desired
    ``final_duration`` of the clip, and the factor will be automatically
    computed.
    The same effect is applied to the clip's audio and mask if any.
    """
    if final_duration:
        factor = clip.duration / final_duration

    if factor is None:
        raise ValueError("You must provide either 'factor' or 'final_duration'")

    new_clip = clip.copy()
    
    new_clip.duration = clip.duration / factor
    new_clip.end = new_clip.start + new_clip.duration
    
    def time_func(t):
        return factor * t

    new_clip.fl_time = lambda t: clip.fl_time(time_func(t))

    if clip.duration is not None:
        new_clip.duration = clip.duration / factor

    return new_clip
