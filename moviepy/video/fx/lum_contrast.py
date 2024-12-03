def lum_contrast(clip, lum=0, contrast=0, contrast_thr=127):
    """ luminosity-contrast correction of a clip """
    
    def modify_frame(get_frame, t):
        frame = get_frame(t)
        
        # Apply luminosity adjustment
        frame = frame.astype(float)
        frame += lum
        
        # Apply contrast adjustment
        if contrast != 0:
            factor = (259 * (contrast + 255)) / (255 * (259 - contrast))
            frame = factor * (frame - contrast_thr) + contrast_thr
        
        # Clip values to valid range [0, 255]
        return np.clip(frame, 0, 255).astype('uint8')
    
    return clip.fl(modify_frame)
