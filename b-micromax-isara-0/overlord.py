import sys
import json
import asyncio
from asyncio import StreamReader, StreamWriter, Queue


async def _write_json(value, writer: StreamWriter):
    json_str = json.dumps(value) + "\n"
    writer.write(json_str.encode())
    await writer.drain()


class Overlord:
    def __init__(self):
        self._attributes = {}
        self._updated_attrs_queues = []
        self._commands = Queue()

    def set_attr(self, name, value):
        if name in self._attributes and self._attributes[name] == value:
            # same value as previous, ignore
            return

        self._attributes[name] = value
        for queue in self._updated_attrs_queues:
            queue.put_nowait((name, value))

    async def get_command(self) -> str:
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
        while True:
            cmd = await reader.readuntil(b"\n")
            cmd = cmd.decode().strip().lower()
            self._commands.put_nowait(cmd)

    async def _new_connection(self, reader: StreamReader, writer: StreamWriter):
        asyncio.create_task(self._push_attributes(writer))
        asyncio.create_task(self._push_commands(reader))

    async def start(self, port: int):
        srv = await asyncio.start_server(
            self._new_connection, host="0.0.0.0", port=port
        )

        await srv.serve_forever()
