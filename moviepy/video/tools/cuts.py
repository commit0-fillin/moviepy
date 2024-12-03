""" This module contains everything that can help automatize
the cuts in MoviePy """
from collections import defaultdict
import numpy as np
from moviepy.decorators import use_clip_fps_by_default

@use_clip_fps_by_default
def find_video_period(clip, fps=None, tmin=0.3):
    """ Finds the period of a video based on frames correlation """
    if fps is None:
        fps = clip.fps

    frame_duration = 1.0 / fps
    n_frames = int(clip.duration * fps)

    # Calculate correlation between frames
    correlations = []
    for i in range(1, n_frames):
        frame1 = clip.get_frame(i * frame_duration)
        frame2 = clip.get_frame((i + 1) * frame_duration)
        correlation = np.corrcoef(frame1.flatten(), frame2.flatten())[0, 1]
        correlations.append(correlation)

    # Find peaks in correlation
    peaks = [i for i in range(1, len(correlations) - 1) if correlations[i] > correlations[i-1] and correlations[i] > correlations[i+1]]

    # Calculate time differences between peaks
    time_diffs = [peak * frame_duration for peak in peaks]

    # Find the most common time difference above tmin
    time_diffs = [diff for diff in time_diffs if diff >= tmin]
    if not time_diffs:
        return None

    period = max(set(time_diffs), key=time_diffs.count)
    return period

class FramesMatch:
    """
    
    Parameters
    -----------

    t1
      Starting time

    t2
      End time

    d_min
      Lower bound on the distance between the first and last frames

    d_max
      Upper bound on the distance between the first and last frames

    """

    def __init__(self, t1, t2, d_min, d_max):
        self.t1 = t1
        self.t2 = t2
        self.d_min = d_min
        self.d_max = d_max
        self.time_span = t2 - t1

    def __str__(self):
        return '(%.04f, %.04f, %.04f, %.04f)' % (self.t1, self.t2, self.d_min, self.d_max)

    def __repr__(self):
        return '(%.04f, %.04f, %.04f, %.04f)' % (self.t1, self.t2, self.d_min, self.d_max)

    def __iter__(self):
        return iter((self.t1, self.t2, self.d_min, self.d_max))

class FramesMatches(list):

    def __init__(self, lst):
        list.__init__(self, sorted(lst, key=lambda e: e.d_max))

    def filter(self, cond):
        """
        Returns a FramesMatches object obtained by filtering out the FramesMatch
        which do not satistify the condition ``cond``. ``cond`` is a function
        (FrameMatch -> bool).

        Examples
        ---------
        >>> # Only keep the matches corresponding to (> 1 second) sequences.
        >>> new_matches = matches.filter( lambda match: match.time_span > 1)
        """
        filtered_matches = [match for match in self if cond(match)]
        return FramesMatches(filtered_matches)

    @staticmethod
    def load(filename):
        """ Loads a FramesMatches object from a file.
        >>> matching_frames = FramesMatches.load("somefile")
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        matches = []
        for line in lines:
            t1, t2, d_min, d_max = map(float, line.strip().split(','))
            matches.append(FramesMatch(t1, t2, d_min, d_max))
        
        return FramesMatches(matches)

    @staticmethod
    def from_clip(clip, dist_thr, max_d, fps=None):
        """ Finds all the frames tht look alike in a clip, for instance to make a
        looping gif.

        This teturns a  FramesMatches object of the all pairs of frames with
        (t2-t1 < max_d) and whose distance is under dist_thr.

        This is well optimized routine and quite fast.

        Examples
        ---------
        
        We find all matching frames in a given video and turn the best match with
        a duration of 1.5s or more into a GIF:

        >>> from moviepy.editor import VideoFileClip
        >>> from moviepy.video.tools.cuts import find_matching_frames
        >>> clip = VideoFileClip("foo.mp4").resize(width=200)
        >>> matches = find_matching_frames(clip, 10, 3) # will take time
        >>> best = matches.filter(lambda m: m.time_span > 1.5).best()
        >>> clip.subclip(best.t1, best.t2).write_gif("foo.gif")

        Parameters
        -----------

        clip
          A MoviePy video clip, possibly transformed/resized
        
        dist_thr
          Distance above which a match is rejected
        
        max_d
          Maximal duration (in seconds) between two matching frames
        
        fps
          Frames per second (default will be clip.fps)
        
        """
        if fps is None:
            fps = clip.fps

        duration = clip.duration
        n_frames = int(duration * fps)
        
        frames = [clip.get_frame(t) for t in np.arange(0, duration, 1/fps)]
        
        matches = []
        for i in range(n_frames):
            for j in range(i+1, n_frames):
                if (j-i)/fps > max_d:
                    break
                
                dist = np.mean(np.abs(frames[i] - frames[j]))
                if dist < dist_thr:
                    t1, t2 = i/fps, j/fps
                    matches.append(FramesMatch(t1, t2, dist, dist))
        
        return FramesMatches(matches)

    def select_scenes(self, match_thr, min_time_span, nomatch_thr=None, time_distance=0):
        """

        match_thr
          The smaller, the better-looping the gifs are.

        min_time_span
          Only GIFs with a duration longer than min_time_span (in seconds)
          will be extracted.

        nomatch_thr
          If None, then it is chosen equal to match_thr

        """
        if nomatch_thr is None:
            nomatch_thr = match_thr

        selected = []
        for match in self:
            if match.time_span < min_time_span:
                continue
            
            if match.d_min <= match_thr and match.d_max <= nomatch_thr:
                if not selected or (match.t1 - selected[-1].t2) >= time_distance:
                    selected.append(match)

        return FramesMatches(selected)

@use_clip_fps_by_default
def detect_scenes(clip=None, luminosities=None, thr=10, logger='bar', fps=None):
    """ Detects scenes of a clip based on luminosity changes.
    
    Note that for large clip this may take some time
    
    Returns
    --------
    cuts, luminosities
      cuts is a series of cuts [(0,t1), (t1,t2),...(...,tf)]
      luminosities are the luminosities computed for each
      frame of the clip.
    
    Parameters
    -----------
    
    clip
      A video clip. Can be None if a list of luminosities is
      provided instead. If provided, the luminosity of each
      frame of the clip will be computed. If the clip has no
      'fps' attribute, you must provide it.
    
    luminosities
      A list of luminosities, e.g. returned by detect_scenes
      in a previous run.
    
    thr
      Determines a threshold above which the 'luminosity jumps'
      will be considered as scene changes. A scene change is defined
      as a change between 2 consecutive frames that is larger than
      (avg * thr) where avg is the average of the absolute changes
      between consecutive frames.
      
    progress_bar
      We all love progress bars ! Here is one for you, in option.
      
    fps
      Must be provided if you provide no clip or a clip without
      fps attribute.
    

    """
    if luminosities is None:
        if clip is None:
            raise ValueError("You must provide either a clip or luminosities")
        if fps is None:
            fps = clip.fps
        
        def frame_luminosity(t):
            frame = clip.get_frame(t)
            return np.mean(frame)
        
        luminosities = [frame_luminosity(t) for t in np.arange(0, clip.duration, 1/fps)]
    
    luminosity_diffs = np.diff(luminosities)
    avg_diff = np.mean(np.abs(luminosity_diffs))
    threshold = thr * avg_diff
    
    scene_changes = np.where(np.abs(luminosity_diffs) > threshold)[0]
    scene_changes = np.insert(scene_changes, 0, -1)
    scene_changes = np.append(scene_changes, len(luminosities) - 1)
    
    cuts = [(scene_changes[i] / fps, scene_changes[i+1] / fps) for i in range(len(scene_changes) - 1)]
    
    return cuts, luminosities
