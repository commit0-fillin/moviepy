def scroll(clip, h=None, w=None, x_speed=0, y_speed=0, x_start=0, y_start=0, apply_to='mask'):
    """ Scrolls horizontally or vertically a clip, e.g. to make end
        credits """
    def scroll_func(get_frame, t):
        x = x_start + x_speed * t
        y = y_start + y_speed * t
        
        frame = get_frame(t)
        
        if h is None and w is None:
            return frame
        
        h_f = h or clip.h
        w_f = w or clip.w
        
        x = int(x % w_f) if w_f else 0
        y = int(y % h_f) if h_f else 0
        
        if w_f:
            frame = np.hstack([frame[:, x:], frame[:, :x]])
        if h_f:
            frame = np.vstack([frame[y:], frame[:y]])
        
        return frame[:h_f, :w_f] if h_f and w_f else frame

    return clip.fl(scroll_func, apply_to=apply_to)
