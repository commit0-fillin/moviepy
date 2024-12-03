import numpy as np

def find_audio_period(aclip, t_min=0.1, t_max=2, t_res=0.01):
    """ Finds the period, in seconds of an audioclip.
    
    The beat is then given by bpm = 60/T

    t_min and _tmax are bounds for the returned value, t_res
    is the numerical precision
    """
    # Get the audio data as a numpy array
    audio_array = aclip.to_soundarray()
    
    # If stereo, convert to mono by averaging channels
    if audio_array.ndim > 1:
        audio_array = np.mean(audio_array, axis=1)
    
    # Calculate the autocorrelation of the audio signal
    correlation = np.correlate(audio_array, audio_array, mode='full')
    correlation = correlation[len(correlation)//2:]
    
    # Get the sample rate of the audio clip
    sample_rate = aclip.fps
    
    # Convert time bounds to sample indices
    min_lag = int(t_min * sample_rate)
    max_lag = int(t_max * sample_rate)
    
    # Find peaks in the autocorrelation
    peaks = []
    for i in range(min_lag, max_lag):
        if correlation[i] > correlation[i-1] and correlation[i] > correlation[i+1]:
            peaks.append((i, correlation[i]))
    
    # If no peaks found, return None
    if not peaks:
        return None
    
    # Sort peaks by correlation value (descending)
    peaks.sort(key=lambda x: x[1], reverse=True)
    
    # Return the period corresponding to the highest peak
    period = peaks[0][0] / sample_rate
    
    # Round the period to the specified resolution
    period = round(period / t_res) * t_res
    
    return period
