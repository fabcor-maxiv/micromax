#!/usr/bin/env python
from sys import stdout
import struct
import random
from pathlib import Path
from tango.server import Device, attribute
from simplejpeg import decode_jpeg

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


def _load_image() -> bytearray:
    jpg_file = Path(SAMPLE_JPEG)
    pixels = decode_jpeg(jpg_file.read_bytes())

    header = struct.pack(
        ">IHHqiiHHxxxx", 1447314767, 1, IMAGE_MODE, 0, WIDTH, HEIGHT, 0, HEADER_SIZE
    )

    return bytearray(header) + bytearray(pixels)


class MD3(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._image = _load_image()
        self._frame_number = 1

    def _update_image(self):
        # update frame number in the header
        self._image[8:16] = struct.pack(">q", self._frame_number)
        self._frame_number += 1

    @attribute(dtype="DevEncoded", format="%d")
    def video_last_image(self):
        self._update_image()

        return "VIDEO_IMAGE", self._image

    @attribute(dtype="DevULong")
    def image_width(self):
        return WIDTH

    @attribute(dtype="DevULong")
    def image_height(self):
        return HEIGHT


if __name__ == "__main__":
    MD3.run_server()
