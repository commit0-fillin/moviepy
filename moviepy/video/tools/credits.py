"""
This module contains different functions to make end and opening
credits, even though it is difficult to fill everyone needs in this
matter.
"""
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.resize import resize
from moviepy.video.VideoClip import ImageClip, TextClip

def credits1(creditfile, width, stretch=30, color='white', stroke_color='black', stroke_width=2, font='Impact-Normal', fontsize=60, gap=0):
    """

    Parameters
    -----------
    
    creditfile
      A text file whose content must be as follows: ::
        
        # This is a comment
        # The next line says : leave 4 blank lines
        .blank 4
        
        ..Executive Story Editor
        MARCEL DURAND
        
        ..Associate Producers
        MARTIN MARCEL
        DIDIER MARTIN
        
        ..Music Supervisor
        JEAN DIDIER
    
    width
      Total width of the credits text in pixels
      
    gap
      Horizontal gap in pixels between the jobs and the names
    
    color
      Color of the text. See ``TextClip.list('color')``
      for a list of acceptable names.

    font
      Name of the font to use. See ``TextClip.list('font')`` for
      the list of fonts you can use on your computer.

    fontsize
      Size of font to use

    stroke_color
      Color of the stroke (=contour line) of the text. If ``None``,
      there will be no stroke.

    stroke_width
      Width of the stroke, in pixels. Can be a float, like 1.5.
    
        
    Returns
    ---------
    
    image
      An ImageClip instance that looks like this and can be scrolled
      to make some credits:

          Executive Story Editor    MARCEL DURAND
             Associate Producers    MARTIN MARCEL
                                    DIDIER MARTIN
                Music Supervisor    JEAN DIDIER
              
    """
    from moviepy.video.VideoClip import TextClip, CompositeVideoClip
    from moviepy.video.tools.drawing import color_gradient
    import numpy as np

    # Parse the credit file
    with open(creditfile, 'r') as f:
        lines = f.readlines()

    # Process the lines
    texts = []
    y = 0
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        elif line.startswith('.blank'):
            y += int(line.split()[1]) * fontsize
        elif line.startswith('..'):
            texts.append((line[2:], 'left', y))
            y += fontsize
        else:
            texts.append((line, 'right', y))
            y += fontsize

    # Create text clips
    clips = []
    for text, align, y in texts:
        clip = TextClip(text, fontsize=fontsize, font=font, color=color,
                        stroke_color=stroke_color, stroke_width=stroke_width)
        if align == 'left':
            clip = clip.set_position((0, y))
        else:
            clip = clip.set_position((width - clip.w, y))
        clips.append(clip)

    # Create the final composite
    final_height = y + fontsize  # Add extra space at the bottom
    credit_clip = CompositeVideoClip(clips, size=(width, final_height))

    # Add a gradient background
    gradient = color_gradient(credit_clip.size, p1=(0, 0), p2=(0, credit_clip.h), 
                              col1=(0,0,0), col2=(0.5, 0.5, 0.5))
    credit_clip = CompositeVideoClip([credit_clip.on_color(size=credit_clip.size, 
                                                           color=(0,0,0), pos=(0, 0)),
                                      credit_clip])

    return credit_clip.set_duration(credit_clip.h / stretch)
