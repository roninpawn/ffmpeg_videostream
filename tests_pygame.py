from ffmpeg_videostream import VideoStream
from time import time
import numpy as np
import cv2
import pygame


def test(stream, callback=None):
    frames = 0
    video.open_stream()

    timer = time()
    while True:
        eof, frame = stream.read()
        if eof: break
        if callback is not None:
            callback(frame)
        frames += 1

    timer = time() - timer
    stream.close()

    print(f"Processed {frames} frames at {stream.shape()} resolution from '{stream.path}' in {round(timer, 3)} "
          f"seconds. \r\nEffective rate of {round(frames / timer, 1)} frames per second.")


def to_color(frame):
        arr = np.frombuffer(frame, np.uint8).reshape(video.shape()[1] * 3 // 2, video.shape()[0])
        img = cv2.cvtColor(arr, cv_color)
        return img


def to_color_pygame(frame):
    img = to_color(frame)
    to_pygame(img)


def to_pygame(img):
    pygame.event.pump()
    img = pygame.image.frombuffer(img, window_size, pygame_color)
    screen.blit(img, (0, 0))
    pygame.display.update()


def to_scale_pygame(frame):
    pygame.event.pump()
    img = pygame.image.frombuffer(to_color(frame), window_size, pygame_color)
    img = pygame.transform.scale(img, scale_size)
    screen.blit(img, (0, 0))
    pygame.display.update()


# Provide path to a test video. (<2 minute duration recommended)
path = "test_video.mp4"

print("\r\n--- TEST #1: FFmpeg > RGB24 > RAW (no draw)")
video = VideoStream(path, "rgb24", 3)   # FFmpeg converts source and outputs RGB 24-bit frames
test(video)                             # RGB frames are read and discarded.

print("\r\n--- TEST #2: FFmpeg > YUV420p > RAW (no draw)")
video = VideoStream(path)               # FFmpeg outputs YUV 12-bit frames
test(video)                             # YUV frames are read and discarded

print("\r\n--- TEST #3: FFmpeg > YUV420p > OpenCV:RGB (no draw) ")
cv_color = cv2.COLOR_YUV2RGB_I420
test(video, to_color)                   # YUV frames are converted by OpenCV to RGB

print("\r\n--- TEST #4: FFmpeg > YUV420p > OpenCV:BGR (no draw) ")
cv_color = cv2.COLOR_YUV2BGR_I420
test(video, to_color)                   # YUV frames are converted by OpenCV to BGR

print("\r\nBegin Pygame DRAW Tests", end='')
print("\r\n--- TEST #5: FFmpeg > RGB24 > PyGame")
pygame_color = "RGB"
pygame.init()                           # Initialize PyGame
window_size = video.shape()
screen = pygame.display.set_mode(window_size)
video = VideoStream(path, "rgb24", 3)   # FFmpeg converts source and outputs RGB 24-bit frames
test(video, to_pygame)                  # Pygame renders as RGB

print("\r\n--- TEST #6: FFmpeg > YUV420p > OpenCV:RGB > PyGame")
video = VideoStream(path)               # FFmpeg outputs YUV 12-bit frames
cv_color = cv2.COLOR_YUV2RGB_I420       # OpenCV converts YUV frames to RGB
test(video, to_color_pygame)            # Pygame renders as RGB

print("\r\n--- TEST #7: FFmpeg > YUV420p > OpenCV:BGR > PyGame")
cv_color = cv2.COLOR_YUV2BGR_I420       # OpenCV converts YUV frames to BGR
pygame_color = "BGR"
test(video, to_color_pygame)            # Pygame renders as BGR

print("\r\n--- TEST #8: PyGame scales frame in BGR")
scale_size = [int(x * .66) for x in window_size]
test(video, to_scale_pygame)            # Pygame scales and renders image in BGR.

print("\r\n--- TEST #9: PyGame scales frame in RGB")
pygame_color = "RGB"
cv_color = cv2.COLOR_YUV2RGB_I420       # OpenCV converts YUV frames to RGB
test(video, to_scale_pygame)            # Pygame scales and renders image in RGB.
