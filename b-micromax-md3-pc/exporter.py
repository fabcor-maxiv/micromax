#!/usr/bin/env python3
import sys
import math
import traceback
from time import time
from asyncio import StreamReader, StreamWriter
from atcpserv import AsyncTCPServer

PORT = 9001

STX = b"\02"
ETX = b"\03"
ARRAY_SEP = "\x1f"

READ = "READ "
LIST = "LIST"
EXEC = "EXEC "


def epoch_milisec() -> int:
    return int(time() * 1000)


def log(msg: str):
    print(msg)
    sys.stdout.flush()


def encode_val(val) -> str:
    def encode_list():
        str_lst = [encode_val(v) for v in val]
        return ARRAY_SEP + ARRAY_SEP.join(str_lst) + ARRAY_SEP

    def encode_float():
        if math.isinf(val):
            txt = "Infinity"
            if val < 0:
                txt = "-" + txt
            return txt

        return str(val)

    val_type = type(val)

    if val_type == str:
        return val

    if val_type == int:
        return str(val)

    if val_type == float:
        return encode_float()

    if val_type in (list, tuple):
        return encode_list()

    if val_type == bool:
        return "true" if val else "false"

    assert False, f"unsupported value type {val_type}"


class UnknownAttribue(Exception):
    pass


class UnknownCommand(Exception):
    pass


class MD3Up:
    def __init__(self):
        self._motors = {
            # name: (limits)
            "AlignmentX": (-5.6, 6.1),
            "AlignmentY": (-77.0, 2.0),
            "AlignmentZ": (-3.399, 6.1),
            "Omega": (-math.inf, math.inf),
            "CentringX": (-3.05, 3.05),
            "CentringY": (-3.05, 3.5),
        }

        self._attrs = {
            "AperturePosition": "BEAM",
            "ApertureDiameters": [5, 10, 15, 20, 50, 600],
            "AlignmentXPosition": 6.582e-06,
            "AlignmentXState": "Ready",
            "AlignmentYPosition": 9.362e-06,
            "AlignmentYState": "Ready",
            "AlignmentZPosition": 5.712e-05,
            "AlignmentZState": "Ready",
            "FrontLightIsOn": False,
            "BackLightIsOn": False,
            "FrontLightFactor": 0.9,
            "BackLightFactor": 1.6,
            "OmegaPosition": 359.999979169585,
            "OmegaState": "Ready",
            "CentringXPosition": 1.746e-06,
            "CentringXState": "Ready",
            "CentringYPosition": 1.174e-05,
            "CentringYState": "Ready",
            "CurrentApertureDiameterIndex": 2,
            "CoaxialCameraZoomValue": 1,
            "CoaxCamScaleX": 0.0018851562499999997,
            "CoaxCamScaleY": 0.0018851562499999997,
            "TransferMode": "SAMPLE_CHANGER",
            "HeadType": "SmartMagnet",
            "SampleIsLoaded": False,
            "CurrentPhase": "Transfer",
            "ScanStartAngle": 246.798,
            "ScanExposureTime": 0.663,
            "ScanRange": 6.0,
            "ScanNumberOfFrames": 1,
            "AlignmentTablePosition": "TRANSFER",
            "BeamstopPosition": "TRANSFER",
            "ScintillatorPosition": "UNKNOWN",
            "SampleHolderLength": 22.0,
            "CapillaryVerticalPosition": -93.49539792171772,
            "PlateLocation": "null",
            "CentringTableVerticalPosition": -1.174697170195887e-05,
            "FastShutterIsOpen": False,
            "CameraExposure": 40000.0,
            "LastTaskInfo": [
                "Hot Start",
                "0",
                "2023-08-04 10:41:57.125",
                "2023-08-04 10:41:57.325",
                "true",
                "null",
                "1",
            ],
            "State": "Ready",
        }

        self._commands = {
            # double[] getMotorLimits(String)
            "getMotorLimits": ("double[]", "String", self._do_get_motor_limits),
        }

    def _do_get_motor_limits(self, motor_name) -> tuple[float, float]:
        return self._motors[motor_name]

    def read_attribute(self, attribute_name: str):
        val = self._attrs.get(attribute_name)
        if val is None:
            raise UnknownAttribue()

        return val

    def list_commands(self):
        print(list(self._commands.items()))
        for name, (ret_type, args, _) in self._commands.items():
            yield name, ret_type, args

    def exec_command(self, command_name, command_args):
        cmd = self._commands.get(command_name)
        if cmd is None:
            raise UnknownCommand()

        _, _, cmd_method = cmd
        return cmd_method(*command_args)


class Exporter:
    def __init__(self):
        self._md3 = MD3Up()

    async def _write_reply(self, writer: StreamWriter, reply: str):
        msg = STX + reply.encode() + ETX
        writer.write(msg)
        await writer.drain()

        log(f"< {msg}")

    async def _read_message(self, reader: StreamReader) -> str:
        message = await reader.readuntil(ETX)

        log(f"> {message}")

        # assert that message starts with STX byte
        assert message[0] == STX[0]

        # chop off STX and ETX bytes
        return message[1:-1].decode()

    def _handle_read(self, attr_name: str) -> str:
        try:
            val = self._md3.read_attribute(attr_name)
            return f"RET:{encode_val(val)}"
        except UnknownAttribue:
            log(f"WARNING: read command for an unknown attribute '{attr_name}'")
            # this seems to be the error message MD3UP generates for unknown attributes
            return f"ERR:Undefined method: true.get{attr_name}"

    def _handle_exec(self, command: str) -> str:
        cmd_name, args = command.split(" ", 1)
        args = args.strip().split("\t")

        ret = self._md3.exec_command(cmd_name, args)

        return f"RET:{encode_val(ret)}"

    def _handle_list(self) -> str:
        def commands():
            for name, ret_type, args in self._md3.list_commands():
                yield f"{ret_type} {name}({args})"

        cmds = "\t".join(list(commands()))

        return f"RET:{cmds}"

    def _handle_message(self, msg: str):
        if msg.startswith(READ):
            return self._handle_read(msg[len(READ) :])

        if msg.startswith(EXEC):
            return self._handle_exec(msg[len(EXEC) :])

        if msg.startswith(LIST):
            return self._handle_list()

        assert False, f"unexpected message '{msg}'"

    async def new_connection(self, reader: StreamReader, writer: StreamWriter):
        log("MD3 new connection")

        try:
            while True:
                msg = await self._read_message(reader)
                reply = self._handle_message(msg)
                await self._write_reply(writer, reply)
        except Exception as ex:
            log(f"error: {str(ex)}")
            traceback.print_exception(ex)


exporter = Exporter()
tcp_srv = AsyncTCPServer(PORT, exporter.new_connection)
log("MD3 exporter emulator starting")
tcp_srv.start()
