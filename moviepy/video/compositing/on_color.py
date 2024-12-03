from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.VideoClip import ColorClip

def on_color(clip, size=None, color=(0, 0, 0), pos=None, col_opacity=None):
    """ 
    Returns a clip made of the current clip overlaid on a color
    clip of a possibly bigger size. Can serve to flatten transparent
    clips (ideal for previewing clips with masks).
    
    :param size: size of the final clip. By default it will be the
       size of the current clip.
    :param color: the background color of the final clip
    :param pos: the position of the clip in the final clip.
    :param col_opacity: opacity of the added color clip
    """
    if size is None:
        size = clip.size

    if pos is None:
        pos = 'center'

    color_clip = ColorClip(size, color)

    if col_opacity is not None:
        color_clip = color_clip.set_opacity(col_opacity)

    return CompositeVideoClip([color_clip, clip.set_position(pos)], size=size)
