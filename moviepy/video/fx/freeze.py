from moviepy.decorators import requires_duration
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip

@requires_duration
def freeze(clip, t=0, freeze_duration=None, total_duration=None, padding_end=0):
    """ Momentarily freeze the clip at time t.

    Set `t='end'` to freeze the clip at the end (actually it will freeze on the
    frame at time clip.duration - padding_end seconds).
    With ``duration``you can specify the duration of the freeze.
    With ``total_duration`` you can specify the total duration of
    the clip and the freeze (i.e. the duration of the freeze is
    automatically calculated). One of them must be provided.
    """
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    from moviepy.video.VideoClip import ImageClip

    if t == 'end':
        t = clip.duration - padding_end

    if freeze_duration is None and total_duration is None:
        raise ValueError("You must provide either freeze_duration or total_duration")

    if total_duration is not None:
        freeze_duration = total_duration - clip.duration

    frozen_frame = clip.to_ImageClip(t)
    freeze_clip = frozen_frame.set_duration(freeze_duration)

    if t < 0:
        raise ValueError("t must be non-negative")
    elif t > clip.duration:
        raise ValueError("t must be less than or equal to the clip's duration")
    elif t == 0:
        return concatenate_videoclips([freeze_clip, clip])
    elif t == clip.duration:
        return concatenate_videoclips([clip, freeze_clip])
    else:
        before = clip.subclip(0, t)
        after = clip.subclip(t)
        return concatenate_videoclips([before, freeze_clip, after])
