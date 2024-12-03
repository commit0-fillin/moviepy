import threading
import time
import numpy as np
import pygame as pg
from moviepy.decorators import convert_masks_to_RGB, requires_duration
from moviepy.tools import cvsecs
pg.init()
pg.display.set_caption('MoviePy')

def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen """
    a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pg.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pg.display.flip()

@convert_masks_to_RGB
def show(clip, t=0, with_mask=True, interactive=False):
    """
    Splashes the frame of clip corresponding to time ``t``.
    
    Parameters
    ------------
    
    t
      Time in seconds of the frame to display.
    
    with_mask
      ``False`` if the clip has a mask but you want to see the clip
      without the mask.
    
    interactive
      ``True`` if you want to be able to interact with the displayed frame
      using Pygame events.
    """
    if isinstance(t, str):
        t = cvsecs(t)
    
    img = clip.get_frame(t)
    if with_mask and (clip.mask is not None):
        mask = 255 * clip.mask.get_frame(t)
        img = np.dstack([img, mask]).astype('uint8')
    
    imdisplay(img)
    
    if interactive:
        result = []
        while True:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = pg.mouse.get_pos()
                    rgb = img[y, x]
                    result.append({'position': (x, y), 'color': rgb})
                elif event.type == pg.QUIT:
                    print(result)
                    return result
    else:
        pg.event.wait()

@requires_duration
@convert_masks_to_RGB
def preview(clip, fps=15, audio=True, audio_fps=22050, audio_buffersize=3000, audio_nbytes=2, fullscreen=False):
    """ 
    Displays the clip in a window, at the given frames per second
    (of movie) rate. It will avoid that the clip be played faster
    than normal, but it cannot avoid the clip to be played slower
    than normal if the computations are complex. In this case, try
    reducing the ``fps``.
    
    Parameters
    ------------
    
    fps
      Number of frames per seconds in the displayed video.
        
    audio
      ``True`` (default) if you want the clip's audio be played during
      the preview.
        
    audio_fps
      The frames per second to use when generating the audio sound.
      
    fullscreen
      ``True`` if you want the preview to be displayed fullscreen.
      
    """
    if fullscreen:
        flags = pg.FULLSCREEN
    else:
        flags = 0

    # Initialize Pygame display
    pg.display.init()
    screen = pg.display.set_mode(clip.size, flags)

    audio_flag = audio and (clip.audio is not None)

    if audio_flag:
        # Initialize Pygame audio
        pg.mixer.quit()
        pg.mixer.init(audio_fps, -audio_nbytes*8, clip.audio.nchannels, audio_buffersize)
        soundarray = clip.audio.to_soundarray(fps=audio_fps, nbytes=audio_nbytes)
        sound = pg.sndarray.make_sound(soundarray)

    t0 = time.time()
    for t in np.arange(0, clip.duration, 1.0/fps):
        img = clip.get_frame(t)
        imdisplay(img, screen)
        
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                return
        
        if audio_flag:
            if t == 0:
                channel = sound.play()
            elif not channel.get_busy():
                channel = sound.play()

        time.sleep(max(0, t - (time.time() - t0)))

    pg.quit()
