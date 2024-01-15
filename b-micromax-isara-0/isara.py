#!/usr/bin/env python3
from typing import Callable, Any
import asyncio
from sys import stderr
from argparse import ArgumentParser
from emu.isara import create_emulator
from overlord.emulator import EmulatedDevice, UnknownCommand
from overlord.server import listen


def parse_args():
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
        "--overlord-port",
        default=1111,
    )

    parser.add_argument(
        "--model",
        choices=["ISARA", "ISARA2"],
        default="ISARA2",
    )

    return parser.parse_args()


class _EmulatedIsara(EmulatedDevice):
    _VISIBLE_ATTRIBUTES = ["remote_mode", "door_closed", "power_on", "dewar_pucks"]

    def __init__(self, emulator):
        self.emu = emulator

    def get_attribute_names(self):
        return self._VISIBLE_ATTRIBUTES

    def get_attribute(self, name: str):
        return getattr(self.emu, name)

    def watch_attribute(self, attr_name: str, callback: Callable):
        self.emu.watch_attribute(attr_name, callback)

    def execute_command(self, command: str, args: list[Any]):
        match command:
            case "set_remote_mode":
                self.emu.set_remote_mode()
            case "set_manual_mode":
                self.emu.set_manual_mode()
            case "set_door_closed":
                self.emu.set_door_closed(args[0].lower() == "true")
            case _:
                raise UnknownCommand(command)


async def _run():
    args = parse_args()

    stderr.write(
        f"emulating {args.model} API\n"
        f" overlord port: {args.overlord_port}\n"
        f" operate port:  {args.operate_port}\n"
        f" monitor port:  {args.monitor_port}\n"
    )

    emulator = create_emulator(
        args.model, args.operate_port, args.monitor_port, enable_logging=True
    )

    await asyncio.gather(
        emulator.start(), listen(args.overlord_port, _EmulatedIsara(emulator))
    )


def main():
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        # just exit without any fuss
        pass


main()
