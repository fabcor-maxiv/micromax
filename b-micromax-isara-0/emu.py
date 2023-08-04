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


class Isara:
    def __init__(self):
        self._power_on = False

    def _handle_on_command(self):
        self._power_on = True
        return b"on"

    def _handle_off_command(self):
        self._power_on = False
        return b"off"

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

    async def _handle_operate_connection(
        self, reader: StreamReader, writer: StreamWriter
    ):
        while True:
            cmd = await _read_command("operate", reader)

            if cmd == ON:
                reply = self._handle_on_command()
            elif cmd == OFF:
                reply = self._handle_off_command()
            else:
                assert False, f"unexpected command {cmd} on operate connection"

            await _write_reply("operate", writer, reply)

    async def new_operate_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new operate connection")
        try:
            await self._handle_operate_connection(reader, writer)
        except:
            print(traceback.format_exc())

    async def _handle_monitor_connection(
        self, reader: StreamReader, writer: StreamWriter
    ):
        while True:
            cmd = await _read_command("monitor", reader)

            if cmd == STATE:
                reply = self._handle_state_command()
            elif cmd == DI:
                reply = self._handle_di_command()
            elif cmd == DO:
                reply = self._handle_do_command()
            else:
                assert False, f"unexpected command {cmd} on monitor connection"

            await _write_reply("monitor", writer, reply)

    async def new_monitor_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new monitor connection")
        try:
            await self._handle_monitor_connection(reader, writer)
        except:
            print(traceback.format_exc())


def _listen(operate_port: int, monitor_port: int):
    isara = Isara()
    op_srv = AsyncTCPServer(operate_port, isara.new_operate_connection)
    op_srv.start()

    mon_srv = AsyncTCPServer(monitor_port, isara.new_monitor_connection)
    mon_srv.start()

    log(f"emulating ISARA at ports {operate_port} {monitor_port}")


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

    return parser.parse_args()


def _main():
    args = _parse_args()
    _listen(args.operate_port, args.monitor_port)


_main()
