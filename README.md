# obs_mute
Show an image when muted. This is a simplified version of: https://github.com/dmadison/OBS-Mute-Indicator

![Screenshot](github/screenshot.png)

## Installation
Download [mute.py from the releases page](https://github.com/casey-c/obs_mute/releases) and save it somewhere. In OBS, go to Tools -> Scripts and hit the plus sign and then add the downloaded script. You can optionally download mute.png as well as a starter image.

Note: Seems like it only works with Python 3.6 on Windows. (3.8 didn't work). Make sure your python location is pointing to the right version.

## Usage
In the Tools -> Scripts menu, set the desired audio source and image source. When you mute the audio source, the chosen image source will be visible, and will hide once you unmute. You may need to hit the refresh button on the script after loading it the first time for it to update as it might be bugged (sorry!).
