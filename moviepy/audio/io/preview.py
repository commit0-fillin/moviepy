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
    pg.mixer.init(fps, -8 * nbytes, clip.nchannels, buffersize)
    
    soundarray = clip.to_soundarray(buffersize=buffersize, nbytes=nbytes, quantize=True)
    sound = pg.sndarray.make_sound(soundarray.reshape((-1, 2*nbytes))[:, 0].astype(np.int16))
    
    if (audioFlag is not None) and (videoFlag is not None):
        audioFlag.set()
        videoFlag.wait()
    
    channel = sound.play()
    
    t0 = time.time()
    while channel.get_busy():
        t1 = time.time()
        time.sleep(max(0, (t0 + clip.duration) - t1))
    
    sound.stop()
    pg.mixer.quit()
