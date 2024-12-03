"""
all decorators used in moviepy go there
"""
import decorator
from moviepy.tools import cvsecs

@decorator.decorator
def outplace(f, clip, *a, **k):
    """ Applies f(clip.copy(), *a, **k) and returns clip.copy()"""
    new_clip = clip.copy()
    f(new_clip, *a, **k)
    return new_clip

@decorator.decorator
def convert_masks_to_RGB(f, clip, *a, **k):
    """ If the clip is a mask, convert it to RGB before running the function """
    if clip.ismask:
        clip = clip.rgb_color()
    return f(clip, *a, **k)

@decorator.decorator
def apply_to_mask(f, clip, *a, **k):
    """ This decorator will apply the same function f to the mask of
        the clip created with f """
    new_clip = f(clip, *a, **k)
    if clip.mask is not None:
        new_clip.mask = f(clip.mask, *a, **k)
    return new_clip

@decorator.decorator
def apply_to_audio(f, clip, *a, **k):
    """ This decorator will apply the function f to the audio of
        the clip created with f """
    new_clip = f(clip, *a, **k)
    if hasattr(clip, 'audio') and clip.audio is not None:
        new_clip.audio = f(clip.audio, *a, **k)
    return new_clip

@decorator.decorator
def requires_duration(f, clip, *a, **k):
    """ Raise an error if the clip has no duration."""
    if clip.duration is None:
        raise ValueError("Clip has no duration")
    return f(clip, *a, **k)

@decorator.decorator
def audio_video_fx(f, clip, *a, **k):
    """ Use an audio function on a video/audio clip
    
    This decorator tells that the function f (audioclip -> audioclip)
    can be also used on a video clip, at which case it returns a
    videoclip with unmodified video and modified audio.
    """
    if hasattr(clip, 'audio'):
        new_clip = clip.copy()
        if clip.audio is not None:
            new_clip.audio = f(clip.audio, *a, **k)
        return new_clip
    else:
        return f(clip, *a, **k)

def preprocess_args(fun, varnames):
    """ Applies fun to variables in varnames before launching the function """
    @decorator.decorator
    def wrapper(f, *args, **kwargs):
        names = f.__code__.co_varnames
        new_kwargs = {k: fun(v) if k in varnames else v for (k, v) in kwargs.items()}
        new_args = [fun(arg) if names[i] in varnames else arg for i, arg in enumerate(args)]
        return f(*new_args, **new_kwargs)
    return wrapper

def convert_to_seconds(varnames):
    """Converts the specified variables to seconds"""
    return preprocess_args(cvsecs, varnames)

@decorator.decorator
def add_mask_if_none(f, clip, *a, **k):
    """ Add a mask to the clip if there is none. """
    if clip.mask is None:
        clip = clip.add_mask()
    return f(clip, *a, **k)

@decorator.decorator
def use_clip_fps_by_default(f, clip, *a, **k):
    """ Will use clip.fps if no fps=... is provided in **k """
    if 'fps' not in k and hasattr(clip, 'fps') and clip.fps is not None:
        k['fps'] = clip.fps
    return f(clip, *a, **k)
