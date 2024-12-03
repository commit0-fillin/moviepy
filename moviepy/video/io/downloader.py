"""
Utilities to get a file from the internet
"""
import os
import requests
from moviepy.tools import subprocess_call

def download_webfile(url, filename, overwrite=False):
    """ Small utility to download the file at 'url' under name 'filename'.
    If url is a youtube video ID like z410eauCnH it will download the video
    using youtube-dl (install youtube-dl first !).
    If the filename already exists and overwrite=False, nothing will happen.
    """
    if os.path.exists(filename) and not overwrite:
        return

    if len(url) == 11:  # Assume it's a YouTube video ID
        subprocess_call(['youtube-dl', 
                         '-o', filename, 
                         'https://www.youtube.com/watch?v=' + url])
    else:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
