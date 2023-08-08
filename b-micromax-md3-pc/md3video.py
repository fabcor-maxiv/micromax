#!/usr/bin/env python
from sys import stdout
import struct
import random
from tango.server import Device, attribute


IMAGE_MODE = 0  # monochrome, 8-bit per pixel
WIDTH = 1224
HEIGHT = 1024
HEADER_SIZE = 32
NUM_PIXELS = WIDTH * HEIGHT


def _build_image() -> bytearray:
    header = struct.pack(
        ">IHHqiiHHxxxx", 1447314767, 1, IMAGE_MODE, 0, WIDTH, HEIGHT, 0, HEADER_SIZE
    )

    # start with an all-black image
    pixels = b"\x00" * NUM_PIXELS
    return bytearray(header + pixels)


class MD3(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._image = _build_image()
        self._frame_number = 1

    def _update_image(self):
        # update frame number in the header
        self._image[8:16] = struct.pack(">q", self._frame_number)
        self._frame_number += 1

        # pick a random color and change some random pixels to that color
        new_color = random.randint(0, 255)
        for _ in range(16):
            pixel_idx = random.randint(0, NUM_PIXELS - 1)
            self._image[HEADER_SIZE + pixel_idx] = new_color

    @attribute(dtype="DevEncoded", format="%d")
    def video_last_image(self):
        print(f"MD3 OAV frame: {self._frame_number}")
        stdout.flush()

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
