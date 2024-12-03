from moviepy.decorators import apply_to_audio, apply_to_mask, requires_duration

@requires_duration
@apply_to_mask
@apply_to_audio
def loop(self, n=None, duration=None):
    """
    Returns a clip that plays the current clip in an infinite loop.
    Ideal for clips coming from gifs.
    
    Parameters
    ------------
    n
      Number of times the clip should be played. If `None` the
      the clip will loop indefinitely (i.e. with no set duration).

    duration
      Total duration of the clip. Can be specified instead of n.
    """
    if duration is not None:
        n = int(duration / self.duration)
    
    if n is None:
        return self.fl(lambda gf, t: gf(t % self.duration))
    else:
        return self.fl(lambda gf, t: gf(t % self.duration) if t < n * self.duration else gf(self.duration))
