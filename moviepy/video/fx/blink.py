import copy

def blink(clip, d_on, d_off):
    """
    Makes the clip blink. At each blink it will be displayed ``d_on``
    seconds and disappear ``d_off`` seconds. Will only work in
    composite clips.
    """
    new_clip = copy.copy(clip)
    
    def make_frame(t):
        cycle = d_on + d_off
        if t % cycle < d_on:
            return clip.get_frame(t)
        else:
            return None
    
    new_clip.make_frame = make_frame
    return new_clip
