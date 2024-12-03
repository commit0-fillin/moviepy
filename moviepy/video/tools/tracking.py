"""
This module contains different functions for tracking objects in videos,
manually or automatically. The tracking functions return results under
the form:  ``( txy, (fx,fy) )`` where txy is of the form [(ti, xi, yi)...]
and (fx(t),fy(t)) give the position of the track for all times t (if the
time t is out of the time bounds of the tracking time interval
fx and fy return the position of the object at the start or at the end
of the tracking time interval).
"""
import numpy as np
from moviepy.decorators import convert_to_seconds, use_clip_fps_by_default
from ..io.preview import imdisplay
from .interpolators import Trajectory
try:
    import cv2
    autotracking_possible = True
except:
    autotracking_possible = False

@convert_to_seconds(['t1', 't2'])
@use_clip_fps_by_default
def manual_tracking(clip, t1=None, t2=None, fps=None, nobjects=1, savefile=None):
    """
    Allows manual tracking of an object(s) in the video clip between
    times `t1` and `t2`. This displays the clip frame by frame
    and you must click on the object(s) in each frame. If ``t2=None``
    only the frame at ``t1`` is taken into account.
    
    Returns a list [(t1,x1,y1),(t2,x2,y2) etc... ] if there is one
    object per frame, else returns a list whose elements are of the 
    form (ti, [(xi1,yi1), (xi2,yi2), ...] )
    
    Parameters
    -------------

    t1,t2:
      times during which to track (defaults are start and
      end of the clip). t1 and t2 can be expressed in seconds
      like 15.35, in (min, sec), in (hour, min, sec), or as a
      string: '01:03:05.35'.
    fps:
      Number of frames per second to freeze on. If None, the clip's
      fps attribute is used instead.
    nobjects:
      Number of objects to click on each frame.
    savefile:
      If provided, the result is saved to a file, which makes
      it easier to edit and re-use later.

    Examples
    ---------
    
    >>> from moviepy.editor import VideoFileClip
    >>> from moviepy.video.tools.tracking import manual_tracking
    >>> clip = VideoFileClip("myvideo.mp4")
    >>> # manually indicate 3 trajectories, save them to a file
    >>> trajectories = manual_tracking(clip, t1=5, t2=7, fps=5,
                                       nobjects=3, savefile="track.txt")
    >>> # ...
    >>> # LATER, IN ANOTHER SCRIPT, RECOVER THESE TRAJECTORIES
    >>> from moviepy.video.tools.tracking import Trajectory
    >>> traj1, traj2, traj3 = Trajectory.load_list('track.txt')
    >>> # If ever you only have one object being tracked, recover it with
    >>> traj, =  Trajectory.load_list('track.txt')
    
    """
    import pygame as pg
    from moviepy.video.io.preview import show

    if t1 is None:
        t1 = 0
    if t2 is None:
        t2 = clip.duration
    
    times = np.arange(t1, t2, 1.0/fps) if fps else [t1]
    
    trajectories = []
    for t in times:
        frame = show(clip.set_duration(t2-t1), t-t1, interactive=True)
        clicks = []
        for i in range(nobjects):
            while True:
                event = pg.event.wait()
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    clicks.append((x, y))
                    break
        trajectories.append((t, clicks if nobjects > 1 else clicks[0]))
    
    pg.quit()
    
    if savefile:
        try:
            with open(savefile, 'w') as f:
                json.dump(trajectories, f)
        except Exception as e:
            print(f"Error saving to file: {e}")
    
    return trajectories

def findAround(pic, pat, xy=None, r=None):
    """
    find image pattern ``pat`` in ``pic[x +/- r, y +/- r]``.
    if xy is none, consider the whole picture.
    """
    import cv2
    import numpy as np

    if xy is None:
        result = cv2.matchTemplate(pic, pat, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        return max_loc

    x, y = xy
    h, w = pat.shape[:2]
    if r is None:
        r = max(h, w)

    roi = pic[max(0, y-r):min(pic.shape[0], y+r+h),
              max(0, x-r):min(pic.shape[1], x+r+w)]
    
    result = cv2.matchTemplate(roi, pat, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    
    return (max(0, x-r) + max_loc[0], max(0, y-r) + max_loc[1])

def autoTrack(clip, pattern, tt=None, fps=None, radius=20, xy0=None):
    """
    Tracks a given pattern (small image array) in a video clip.
    Returns [(x1,y1),(x2,y2)...] where xi,yi are
    the coordinates of the pattern in the clip on frame i.
    To select the frames you can either specify a list of times with ``tt``
    or select a frame rate with ``fps``.
    This algorithm assumes that the pattern's aspect does not vary much
    and that the distance between two occurences of the pattern in
    two consecutive frames is smaller than ``radius`` (if you set ``radius``
    to -1 the pattern will be searched in the whole screen at each frame).
    You can also provide the original position of the pattern with xy0.
    """
    if not autotracking_possible:
        raise ImportError("autoTrack requires OpenCV. Try installing it with 'pip install opencv-python'")

    if tt is None:
        if fps is None:
            fps = clip.fps
        tt = np.arange(0, clip.duration, 1.0/fps)

    if xy0 is None:
        xy0 = findAround(clip.get_frame(tt[0]), pattern)

    def find_pattern(t):
        frame = clip.get_frame(t)
        return findAround(frame, pattern, xy=xy0, r=radius)

    result = [find_pattern(t) for t in tt]
    
    return list(zip(tt, result))
