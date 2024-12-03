def f_accel_decel(t, old_d, new_d, abruptness=1, soonness=1.0):
    """
    abruptness
      negative abruptness (>-1): speed up down up
      zero abruptness : no effect
      positive abruptness: speed down up down
      
    soonness
      for positive abruptness, determines how soon the
      speedup occurs (0<soonness < inf)
    """
    if abruptness == 0:
        return t * new_d / old_d
    
    t = t / old_d  # Normalize t to [0, 1]
    if abruptness > 0:
        z = (1 - t) * soonness
        return new_d * (t + abruptness * (t**2 - t) * np.exp(-z)) / (1 + abruptness * (t - 1) * np.exp(-z))
    else:
        abruptness = max(abruptness, -1)  # Ensure abruptness > -1
        return new_d * (t + abruptness * t * (1 - t)) / (1 + abruptness * (t - 1))

def accel_decel(clip, new_duration=None, abruptness=1.0, soonness=1.0):
    """

    new_duration
      If None, will be that of the current clip.

    abruptness
      negative abruptness (>-1): speed up down up
      zero abruptness : no effect
      positive abruptness: speed down up down
      
    soonness
      for positive abruptness, determines how soon the
      speedup occurs (0<soonness < inf)
    """
    if new_duration is None:
        new_duration = clip.duration
    
    old_duration = clip.duration
    
    def time_transform(t):
        return f_accel_decel(t, old_duration, new_duration, abruptness, soonness)
    
    return clip.fl_time(time_transform, apply_to=['mask', 'audio'])
