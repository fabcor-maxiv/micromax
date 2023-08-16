#!/usr/bin/env python3
import sys
import traceback
from asyncio import StreamReader, StreamWriter
from argparse import ArgumentParser
from atcpserv import AsyncTCPServer

ON = b"on"
OFF = b"off"
STATE = b"state"
DI = b"di"
DO = b"do"
POSITION = b"position"
MESSAGE = b"message"


def log(msg: str):
    print(msg)
    sys.stdout.flush()


async def _read_command(connection_name: str, reader: StreamReader) -> bytes:
    cmd = await reader.readuntil(b"\r")
    log(f"{connection_name}> {cmd}")

    # chop off trailing \r
    return cmd[:-1]


async def _write_reply(connection_name: str, writer: StreamWriter, reply: bytes):
    reply += b"\r"
    writer.write(reply)
    await writer.drain()

    log(f"{connection_name}< {reply}")


def _encode(val):
    t = type(val)
    if t == bool:
        return "1" if val else "0"


class _IsaraMixin:
    """
    contains code shared by ISARA and ISARA2 emulation
    """

    def __init__(self):
        self._power_on = False

    def _handle_state_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _handle_di_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _handle_do_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _handle_on_command(self):
        self._power_on = True
        return b"on"

    def _handle_off_command(self):
        self._power_on = False
        return b"off"

    def _handle_message_command(self):
        return b"System OK for operation"

    def _handle_operate_command(self, command: bytes):
        if command == ON:
            return self._handle_on_command()
        if command == OFF:
            return self._handle_off_command()

        assert False, f"unexpected command {command} on operate connection"

    def _handle_monitor_command(self, command: bytes) -> bytes:
        if command == STATE:
            return self._handle_state_command()
        if command == DI:
            return self._handle_di_command()
        if command == DO:
            return self._handle_do_command()
        if command == MESSAGE:
            return self._handle_message_command()

        assert False, f"unexpected command {command} on monitor connection"

    async def new_operate_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new operate connection")
        try:
            while True:
                cmd = await _read_command("operate", reader)
                reply = self._handle_operate_command(cmd)

                await _write_reply("operate", writer, reply)
        except:
            print(traceback.format_exc())

    async def new_monitor_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new monitor connection")
        try:
            while True:
                cmd = await _read_command("monitor", reader)
                reply = self._handle_monitor_command(cmd)

                await _write_reply("monitor", writer, reply)
        except:
            print(traceback.format_exc())


class Isara(_IsaraMixin):
    """
    emulates ISARA robot, the first model, aka the blue robot at BioMAX
    """

    def _handle_state_command(self) -> bytes:
        reply = f"state({_encode(self._power_on)},1,0,,,,,-1,-1,,,,0,0,,75.0,1.16,1.17,1.18,,,,)"
        return reply.encode()

    def _handle_di_command(self):
        reply = "di(" + "0" * 99 + ")"
        return reply.encode()

    def _handle_do_command(self):
        reply = "do(" + "0" * 99 + ")"
        return reply.encode()

    def _handle_position_command(self) -> bytes:
        return b"position(0.1,0.2,0.3,0.4,0.5,0.6)"

    def _handle_monitor_command(self, command: bytes) -> bytes:
        # handle ISARA1 specific monitor commands
        if command == POSITION:
            return self._handle_position_command()

        return super()._handle_monitor_command(command)


class Isara2(_IsaraMixin):
    """
    emulates ISARA2 robot, aka the yellow robot at MicroMAX
    """

    def _handle_state_command(self) -> bytes:
        reply = (
            f"state({_encode(self._power_on)},0,1,DoubleGripper,HOME,,1,1,-1,-1,-1,-1,-1,"
            "-1,-1,-1,,0,0,75.0,0,0,0.3865678,75.0,72.0,1,0,0,"
            "Robot is out of goniometer zone (translation),67108864,152.9,-390.8,"
            "-17.3,-180.0,0.0,89.1,-75.6,-18.8,93.6,0.0,105.3,-165.5,,1,,1,0,0,0,0,"
            "0,0,0,0,0,0,0,0,0,changetool|3|3|0|-2.441|0.068|392.37|0.0|0.0|-0.984)"
        )
        return reply.encode()

    def _handle_di_command(self) -> bytes:
        return (
            b"di(0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,"
            b"0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,"
            b"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0)"
        )

    def _handle_do_command(self) -> bytes:
        return (
            b"do(0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
            b",0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,1,1,0,0,0,0,0,0,0,0,"
            b"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)"
        )


def _listen(model: str, operate_port: int, monitor_port: int):
    def init_model():
        classes = {"ISARA": Isara, "ISARA2": Isara2}
        klass = classes[model]

        return klass()

    isara = init_model()
    op_srv = AsyncTCPServer(operate_port, isara.new_operate_connection)
    op_srv.start()

    mon_srv = AsyncTCPServer(monitor_port, isara.new_monitor_connection)
    mon_srv.start()

    log(f"emulating {model} at ports {operate_port} {monitor_port}")


def _parse_args():
    parser = ArgumentParser(description="Emulate ISARA Sample Changer API")

    parser.add_argument(
        "-o",
        "--operate-port",
        default=10000,
    )

    parser.add_argument(
        "-m",
        "--monitor-port",
        default=1000,
    )

    parser.add_argument(
        "--model",
        choices=["ISARA", "ISARA2"],
        default="ISARA2",
    )

    return parser.parse_args()


def _main():
    args = _parse_args()
    _listen(args.model, args.operate_port, args.monitor_port)


_main()
