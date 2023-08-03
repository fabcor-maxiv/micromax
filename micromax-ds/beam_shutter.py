#!/usr/bin/env python

from tango.server import Device, attribute


class BeamShutter(Device):
    @attribute(name="StatusClosed", dtype=bool)
    def status_closed(self):
        return False


if __name__ == "__main__":
    BeamShutter.run_server()
