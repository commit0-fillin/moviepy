import time
import numpy as np
import pygame as pg
from moviepy.decorators import requires_duration
pg.init()
pg.display.set_caption('MoviePy')

@requires_duration
def preview(clip, fps=22050, buffersize=4000, nbytes=2, audioFlag=None, videoFlag=None):
    """
    Plays the sound clip with pygame.
    
    Parameters
    -----------
    
    fps
       Frame rate of the sound. 44100 gives top quality, but may cause
       problems if your computer is not fast enough and your clip is
       complicated. If the sound jumps during the preview, lower it
       (11025 is still fine, 5000 is tolerable).
        
    buffersize
      The sound is not generated all at once, but rather made by bunches
      of frames (chunks). ``buffersize`` is the size of such a chunk.
      Try varying it if you meet audio problems (but you shouldn't
      have to).
    
    nbytes:
      Number of bytes to encode the sound: 1 for 8bit sound, 2 for
      16bit, 4 for 32bit sound. 2 bytes is fine.
    
    audioFlag, videoFlag:
      Instances of class threading events that are used to synchronize
      video and audio during ``VideoClip.preview()``.
    
    """
    pg.mixer.quit()
    pg.mixer.init(fps, -8 * nbytes, clip.nchannels, 1024)
    totalsize = int(fps * clip.duration)
    pospos = np.array(list(range(0, totalsize, buffersize)) + [totalsize])
    
    sound = pg.sndarray.make_sound(
        (clip.to_soundarray(buffersize=buffersize, nbytes=nbytes, quantize=True)
         .reshape((-1, 2*nbytes))[:, 0])
        .astype(np.int16)
    )
    
    channel = sound.play()
    if (audioFlag is not None) and (videoFlag is not None):
        audioFlag.set()
        videoFlag.wait()
    
    t0 = time.time()
    for i in range(1, len(pospos)):
        t1 = time.time()
        while t1 - t0 < pospos[i] / fps:
            time.sleep(0.001)
            t1 = time.time()
    
    sound.stop()
    pg.mixer.quit()
