#!/usr/bin/env python3
import json
import socket
from sys import stdin
from queue import Queue
from enum import Enum
from pprint import pprint
from threading import Thread

"""
Simple Overlord CLI client.

Allows to connect to an overlord device to watch attributes and
issue commands. Written to test the overlord network protocol.
"""

OVERLORD_PORT = 1111


class Sources(Enum):
    STDIN = 0
    SOCKET = 1


class StdinReader:
    def __init__(self, sink: Queue):
        self._sink = sink
        self._thread = Thread(target=self._run)
        self._thread.start()

    def _run(self):
        while True:
            line = stdin.readline()
            self._sink.put((Sources.STDIN, line))


class SocketReader:
    def __init__(self, sink: Queue, socket):
        self._buffer = b""
        self._sink = sink
        self._sock = socket
        self._thread = Thread(target=self._run)
        self._thread.start()

    def _read_line(self):
        while (endline := self._buffer.find(b"\n")) == -1:
            self._buffer += self._sock.recv(1024)

        line = self._buffer[:endline]
        self._buffer = self._buffer[endline + 1 :]

        return line.decode()

    def _run(self):
        while True:
            self._sink.put((Sources.SOCKET, self._read_line()))


def handle_overlord(msg: str):

    data = json.loads(msg)
    if (attrs := data.get("attributes")) is not None:
        pprint(attrs)
        return

    if (error := data.get("error")) is not None:
        print(f"error: {error}")
        return

    print(f"unexpected message from overlord: {msg}")


def handle_user(cmd: str, socket):
    def as_parts():
        for part in cmd.split():
            part = part.strip().lower()
            if part != "":
                yield part

    parts = list(as_parts())
    if len(parts) < 1:
        print("give me a command!")
        return

    command = parts[0]
    args = parts[1:]

    message = dict(command=command, args=args)
    text = f"{json.dumps(message)}\n"
    socket.sendall(text.encode())


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", OVERLORD_PORT))
    incoming = Queue()
    StdinReader(incoming)
    SocketReader(incoming, sock)

    while True:
        src, msg = incoming.get()
        match src:
            case Sources.STDIN:
                handle_user(msg, sock)
            case Sources.SOCKET:
                handle_overlord(msg)


main()
