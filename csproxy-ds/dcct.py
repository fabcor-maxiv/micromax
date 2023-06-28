#!/usr/bin/env python3
import time
from PyTango import ConnectionFailed
from tango import Database, DbDevInfo
from tango.server import Device, attribute


TANGO_CONNECT_RETRY_TIME = 2.1
DEVICE_NAME = "r3-319s2/dia/dcct-01"


def _connect_to_db():
    db = None
    while db is None:
        try:
            db = Database()
        except ConnectionFailed:
            print(
                f"failed to connect to tango host, retrying in {TANGO_CONNECT_RETRY_TIME} seconds"
            )
            time.sleep(TANGO_CONNECT_RETRY_TIME)

    return db


def register_device():
    db = _connect_to_db()

    db_info = DbDevInfo()
    db_info._class = "Dcct"
    db_info.server = "Dcct/0"
    db_info.name = DEVICE_NAME

    db.add_device(db_info)


class Dcct(Device):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @attribute(name="Current", dtype=float)
    def current(self):
        return 8.293e-06

    @attribute(name="Lifetime", dtype=float)
    def lifetime(self):
        return -539.76


if __name__ == "__main__":
    register_device()
    Dcct.run_server()
