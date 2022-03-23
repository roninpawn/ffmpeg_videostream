# FFmpeg VideoStream
***High speed video frame access in Python, using FFmpeg and FFshow***

This script requires:
- Karl Kroening's 'ffmpeg-python' library. (https://github.com/kkroening/ffmpeg-python)
- ffmpeg.exe + ffprobe.exe in the calling directory or accessible by PATH (https://www.ffmpeg.org/download.html)

## Basic Usage
```python
from ffmpeg_videostream import VideoStream

video = VideoStream("my_video.mp4")
video.open_stream()
while True:
    eof, frame = video.read()
    if eof: break
```

## Methods

**VideoStream** (_path, color, bytes_per_pixel_)

- path : The path to your video file as a string : `'/videos/my_video.mp4'`
- color : The pixel format you are requesting from FFmpeg : By default `'yuv420p'` _(recommended)_
- bytes_per_pixel : The number of bytes ***(not bits)*** that your pixel format uses to store a pixel
  : By default `1.5` (as per `'yuv420p'`)

**Note:** By setting `color` and `bytes_per_pixel` you can ingest video into any pixel format ffmpeg supports. However,
most source files and use cases will benefit by using the default configuration and converting the pixel data to
other formats as needed. (See 'Examples')

---

**.config** (_start_hms, end_hms, crop_rect, output_resolution_)
- start_hms : Read frames starting from this _time*_ in the video : _("seek" equivalent)_
- end_hms : Stop reading frames at this _time*_ in the video
  - _HMS times are composed as `[HH:]MM:SS[.m...]` or `S+[.m...][s|ms|us]`_
  - _(see https://ffmpeg.org/ffmpeg-utils.html#time-duration-syntax)_
- crop_rect : Accepts a list / tuple as `[x, y, width, height]` for cropping the video's input
- output_resolution :  Accepts a list / tuple as `[width, height]` declaring the final scaling of the video, forcing 
the output to match this resolution

**Note:** When crop_rect is set, it overrides the .shape() of the final output resolution. This is only important
to note if you were to request the crop in a separate call to .config(), AFTER requesting the output_resolution be 
changed in a previous call. For example...

```python
video.config(output_resolution=(1280, 720))
video.config(crop_rect=(0,0,720,480))
# Hey, just don't do it that way... huh?
```

---

**.open_stream** (_showinfo, loglevel, hide_banner, silence_even_test_)
- showinfo : When `True` invokes ffmpeg's '_showinfo_' filter providing details about each frame as it is read.
  - (see: https://ffmpeg.org/ffmpeg-filters.html#showinfo)
- loglevel : Sets ffmpeg's 'stderr' output to include/exclude certain data being printed to console.
  - (see: https://ffmpeg.org/ffmpeg.html#Generic-options )
- hide_banner : Shows/hides ffmpeg's startup banner.
  - Note: Various 'loglevel' settings implicitly silence this banner. When 'showinfo' is invoked no 'loglevel' 
output will be printed to console.
- silence_even_test : When `True` suppresses console warnings that an invalid resolution has been requested.

**Note:** Invoking 'showinfo' reduces the maximum speed raw frame data can ingest. In most rendering instances the speed
reduction is immeasurable due to other blocking processes. But for the raw acquisition of frames it can be significant.

---

**.read** ()

Returns an end-of-file boolean flag, followed by a single frame's worth of the raw bytestream from the video.
The bytestream data returned is in no way prepared, decoded, or shaped into an array structure. A simple example for 
converting YUV420p to BGR using numpy and OpenCV is provided:
```python
    eof, frame = video.read()
    arr = np.frombuffer(frame, np.uint8).reshape(video.shape[1] * 1.5, video.shape[0])
    bgr = cv2.cvtColor(arr, cv2.COLOR_YUV2BGR_I420)
```
**Note:** The VideoStream class can be initialized to request BGR output directly from ffmpeg, but it is slower to
acquire a 24-bit RGB / BGR encoded frame than to acquire the 12-bit YUV pixels and convert them.

---

**.shape** () : Returns the final output resolution of the video in a list : `[width, height]`

---

**.eof** () : Boolean indicating whether the end of the file has been reached

---

**.close** () : Closes the open stream



---

**.showinfo** (key)
- Called without a ``key``, returns the complete line of 'showinfo' data as a string
- Called with ``key``, searches 'showinfo' for a match and returns the value, or `None`
  - _(see: https://ffmpeg.org/ffmpeg-filters.html#showinfo )_

```python
current_frame_number = video.showinfo("n")
```
**Note:** All requests return `None` if `showinfo=True` was not set during `open_stream()`

---

**.inspect** (_attrib_)
- Returns a `dict()` containing all data found in the 'video' stream of ffprobe if no attrib declared.
- `.inspect("something")` returns the value of "something" from the `dict()` or `None` if not found.

# Examples

### Timing raw frame access speed
```python
from ffmpeg_videostream import VideoStream
from time import time

video = VideoStream("my_video.mp4")
video.open_stream()
frames = 0

print("\r\nReading VideoStream...")
timer = time()
while True:
    eof, frame = video.read()
    if eof: break
    frames += 1
timer = time() - timer

print(f"\r\nRead {frames} frames at {video.shape()} resolution from '{video.path}' in {round(timer, 3)} seconds.")
print(f"Effective read rate of {round(frames / timer)} frames per second.")
```

### Rendering output to PyGame
```python
from ffmpeg_videostream import VideoStream
import numpy as np
import cv2
import pygame

path = 'my_video.mp4'

video = VideoStream(path)
video.open_stream()

pygame.init()
screen = pygame.display.set_mode(video.shape())

while True:
    eof, frame = video.read()
    # Shape bytestream into YUV 4:2:0 numpy array, then use OpenCV to convert from YUV to RGB.
    arr = np.frombuffer(frame, np.uint8).reshape(video.shape()[1] * 3//2, video.shape()[0])
    img = cv2.cvtColor(arr, cv2.COLOR_YUV2RGB_I420)

    img = pygame.image.frombuffer(img, video.shape(), "RGB")
    screen.blit(img, (0, 0))    # Copy img onto the screen at coordinates: x=0, y=0
    pygame.display.update()
    pygame.event.pump()     # Makes pygame's window draggable / non-blocking.
    if eof:
        break
```