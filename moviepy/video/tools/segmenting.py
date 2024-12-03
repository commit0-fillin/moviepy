import numpy as np
import scipy.ndimage as ndi
from moviepy.video.VideoClip import ImageClip
import cv2
import matplotlib.pyplot as plt

def findObjects(clip, rem_thr=500, preview=False):
    """ 
    Returns a list of ImageClips representing each a separate object on
    the screen.
        
    rem_thr : all objects found with size < rem_Thr will be
         considered false positives and will be removed
    
    """
    # Get the first frame of the clip
    frame = clip.get_frame(0)
    
    # Convert the frame to grayscale
    gray = np.mean(frame, axis=2).astype(np.uint8)
    
    # Threshold the image to create a binary mask
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
    
    # Filter out small objects
    mask = stats[:, 4] >= rem_thr
    stats = stats[mask]
    centroids = centroids[mask]
    
    # Create ImageClips for each object
    object_clips = []
    for i in range(1, len(stats)):  # Skip the background (label 0)
        x, y, w, h, area = stats[i]
        object_frame = frame[y:y+h, x:x+w]
        object_clip = ImageClip(object_frame)
        object_clips.append(object_clip)
    
    if preview:
        # Draw bounding boxes on the original frame for preview
        preview_frame = frame.copy()
        for stat in stats[1:]:  # Skip the background (label 0)
            x, y, w, h, _ = stat
            cv2.rectangle(preview_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Display the preview
        plt.imshow(preview_frame)
        plt.title("Objects Found")
        plt.axis('off')
        plt.show()
    
    return object_clips
