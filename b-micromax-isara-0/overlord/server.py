from typing import Any
import json
import asyncio
import traceback
from json.decoder import JSONDecodeError
from asyncio import StreamReader, StreamWriter, Queue
from overlord.emulator import EmulatedDevice, UnknownCommand


class _Session:
    def __init__(
        self, device: EmulatedDevice, reader: StreamReader, writer: StreamWriter
    ):
        self.attr_updates = Queue()
        self.device = device
        self.reader = reader
        self._writer = writer

    async def send_message(self, message: dict):
        data = f"{json.dumps(message)}\n".encode()
        self._writer.write(data)
        await self._writer.drain()

    async def send_attributes(self, attributes: dict[str, Any]):
        await self.send_message(dict(attributes=attributes))

    async def send_error(self, error_message: str):
        await self.send_message(dict(error=error_message))


async def _push_attributes(attr_names: list[str], session: _Session):
    def all_attrs():
        for name in attr_names:
            yield name, session.device.get_attribute(name)

    attrs = {name: val for name, val in all_attrs()}
    await session.send_attributes(attrs)


def _watch_attributes(attr_names: list[str], session: _Session):
    async def push_new_val(name, val):
        await session.attr_updates.put((name, val))

    def attr_changed(name, val):
        asyncio.create_task(push_new_val(name, val))

    for name in attr_names:
        session.device.watch_attribute(name, lambda val, n=name: attr_changed(n, val))


class _InvalidMessage(Exception):
    pass


def _handle_command(line: bytes, session: _Session):
    message = json.loads(line)
    command = message.get("command")
    if command is None:
        raise _InvalidMessage("no 'command' key found")
    args = message.get("args")

    session.device.execute_command(command, args)


async def _read_connection(session: _Session):
    while (line := await session.reader.readline()) != b"":
        try:
            _handle_command(line, session)
        except (JSONDecodeError, _InvalidMessage) as ex:
            await session.send_error(f"error parsing command: {ex}")
        except UnknownCommand as ex:
            await session.send_error(f"{ex}")

    # socket was closed, we are done


async def _push_attribute_updates(session: _Session):
    while True:
        name, value = await session.attr_updates.get()
        await session.send_attributes({name: value})


async def _new_connection(
    device: EmulatedDevice, reader: StreamReader, writer: StreamWriter
):
    print("new overlord connection")
    session = _Session(device, reader, writer)

    _ = asyncio.create_task(_push_attribute_updates(session))

    try:
        attr_names = device.get_attribute_names()
        _watch_attributes(attr_names, session)
        await _push_attributes(attr_names, session)
        await _read_connection(session)
    except:  # noqa
        print(traceback.format_exc())

    print("closing overlord connection")
    writer.close()
    await writer.wait_closed()


async def listen(port: int, device: EmulatedDevice):
    srv = await asyncio.start_server(
        lambda r, w: _new_connection(device, r, w), host="0.0.0.0", port=port
    )

    await srv.serve_forever()
