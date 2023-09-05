import json
import copy
import asyncio
from dataclasses import dataclass
from asyncio import StreamReader, StreamWriter, Queue, IncompleteReadError


async def _write_json(value, writer: StreamWriter):
    json_str = json.dumps(value) + "\n"
    writer.write(json_str.encode())
    await writer.drain()


@dataclass
class OverlordCommand:
    name: str
    args: list[str]


def _is_same_list(new_list, old_list):
    if len(new_list) != len(old_list):
        return False

    for new, old in zip(new_list, old_list):
        if not _is_same_value(new, old):
            return False

    return True


def _is_same_value(new_val, old_val):
    assert type(new_val) == type(old_val)

    if type(new_val) == list:
        return _is_same_list(new_val, old_val)

    return new_val == old_val


class Overlord:
    def __init__(self):
        self._attributes = {}
        self._updated_attrs_queues = []
        self._commands = Queue()

    def set_attr(self, name, value):
        if name in self._attributes and _is_same_value(value, self._attributes[name]):
            # same value as previous, ignore
            return

        self._attributes[name] = copy.copy(value)

        for queue in self._updated_attrs_queues:
            queue.put_nowait((name, value))

    async def get_command(self) -> OverlordCommand:
        return await self._commands.get()

    async def _push_attributes(self, writer: StreamWriter):
        # send current attribute values
        await _write_json(self._attributes, writer)

        #
        # 'listen' to update value, and push them to client
        #
        queue = Queue()
        self._updated_attrs_queues.append(queue)

        while True:
            name, value = await queue.get()
            await _write_json({name: value}, writer)

    async def _push_commands(self, reader: StreamReader):
        try:
            while True:
                cmd = await reader.readuntil(b"\n")
                cmd = cmd.decode().strip().split(" ")
                self._commands.put_nowait(OverlordCommand(cmd[0], cmd[1:]))
        except IncompleteReadError:
            # connection closed, this task is finished
            print("overlord socket closed")

    async def _new_connection(self, reader: StreamReader, writer: StreamWriter):
        asyncio.create_task(self._push_attributes(writer))
        asyncio.create_task(self._push_commands(reader))

    async def start(self, port: int):
        srv = await asyncio.start_server(
            self._new_connection, host="0.0.0.0", port=port
        )

        await srv.serve_forever()
