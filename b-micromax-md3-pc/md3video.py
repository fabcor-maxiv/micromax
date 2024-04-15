#!/usr/bin/env python
import time
import numpy
import struct
from pathlib import Path
from random import random
from tango.server import Device, attribute
from simplejpeg import decode_jpeg

CORNER_SIZE = 8

# monochrome, 8-bit per pixel
IMAGE_MODE_L = 0
# rgb, 24-bit per pixel
IMAGE_MODE_RGB = 6


SAMPLE_JPEG = "sample.jpeg"
IMAGE_MODE = IMAGE_MODE_RGB
WIDTH = 1224
HEIGHT = 1024
HEADER_SIZE = 32
NUM_PIXELS = WIDTH * HEIGHT


def _paint_corner(orig, color):
    pixels = numpy.copy(orig)
    for i in range(CORNER_SIZE):
        pixels[i][0:CORNER_SIZE] = color

    return bytearray(pixels)


def _make_image(header, pixels, corner_color):
    return header + _paint_corner(pixels, corner_color)


def _load_images():
    sample_pixels = decode_jpeg(Path(SAMPLE_JPEG).read_bytes())

    header = bytearray(
        struct.pack(
            ">IHHqiiHHxxxx", 1447314767, 1, IMAGE_MODE, 0, WIDTH, HEIGHT, 0, HEADER_SIZE
        )
    )

    yield header + bytearray(sample_pixels)
    yield _make_image(header, sample_pixels, [0, 0, 0])
    yield _make_image(header, sample_pixels, [255, 0, 0])
    yield _make_image(header, sample_pixels, [0, 255, 0])
    yield _make_image(header, sample_pixels, [0, 0, 255])


class MD3(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._images = list(_load_images())
        self._frame_number = 0

    def _get_image(self):
        self._frame_number += 1
        image = self._images[self._frame_number % len(self._images)]
        # update frame number in the header
        image[8:16] = struct.pack(">q", self._frame_number)

        return image

    @attribute(dtype="DevEncoded", format="%d")
    def video_last_image(self):
        return "VIDEO_IMAGE", self._get_image()

    @attribute(dtype="DevULong")
    def image_width(self):
        return WIDTH

    @attribute(dtype="DevULong")
    def image_height(self):
        return HEIGHT


if __name__ == "__main__":
    MD3.run_server()
