#!/usr/bin/env python

from tango.server import Device, attribute, command


class BeamShutter(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._closed = False

    @attribute(name="StatusClosed", dtype=bool)
    def status_closed(self):
        return self._closed

    @command
    def Open(self):
        self._closed = False

    @command
    def Close(self):
        self._closed = True


if __name__ == "__main__":
    BeamShutter.run_server()
