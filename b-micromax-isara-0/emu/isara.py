#!/usr/bin/env python3
from typing import Optional
import traceback
import asyncio
from sys import stderr
from enum import Enum
from asyncio import StreamReader, StreamWriter, Event, IncompleteReadError
from .watchable_attrs import WatchableAttrsMixin

PUCKS_NUM = 29

DI = "di"
DO = "do"
ON = "on"
OFF = "off"
PUT = "put"
TRAJ = "traj"
ABORT = "abort"
STATE = "state"
RESET = "reset"
MESSAGE = "message"
OPENLID = "openlid"
SPEEDUP = "speedup"
CLOSELID = "closelid"
POSITION = "position"
SPEEDDOWN = "speeddown"
CLEARMEMORY = "clearmemory"

_logging_enabled = False


def log(msg: str):
    if _logging_enabled:
        stderr.write(f"{msg}\n")


async def _read_command(connection_name: str, reader: StreamReader) -> str:
    cmd = await reader.readuntil(b"\r")
    log(f"{connection_name}> {cmd!r}")

    # chop off trailing \r and make a string
    return cmd[:-1].decode()


async def _write_reply(connection_name: str, writer: StreamWriter, reply: str):
    data = (reply + "\r").encode()
    writer.write(data)
    await writer.drain()

    log(f"{connection_name}< {data!r}")


def _encode_list(lst):
    encoded = [_encode(v) for v in lst]
    return ",".join(encoded)


def _encode(val):
    t = type(val)

    if t == bool:
        return "1" if val else "0"

    if t == list:
        return _encode_list(val)


def _get_command_args(command_name: str, command: str) -> list:
    args_str = command[len(command_name) + 1 : -1]
    return args_str.split(",")


class _Positions(Enum):
    HOME = "HOME"
    SOAK = "SOAK"


class _Speed:
    # TODO: check with the real robot for supported speed ratios
    RATIOS = ["0.01", "1.0", "10.0", "50.0", "75.0", "100.0"]

    def __init__(self):
        self._current_ration_idx = self._max_idx()

    def _max_idx(self):
        return len(self.RATIOS) - 1

    @property
    def ratio(self) -> str:
        return self.RATIOS[self._current_ration_idx]

    @property
    def decimal_ratio(self) -> float:
        """
        current speed ratio as decimal percentage number,
        that is a value between 0.0 and 1.0
        """
        return float(self.ratio) / 100.0

    def increase(self):
        if self._current_ration_idx == self._max_idx():
            # already at highest possible ratio
            return

        self._current_ration_idx += 1

    def decrease(self):
        if self._current_ration_idx == 0:
            # already at lowest possible speed ratio
            return

        self._current_ration_idx -= 1


class _RobotArm:
    def __init__(self):
        self._position = _Positions.HOME
        self.speed = _Speed()

    def move_to(self, new_position: _Positions):
        assert self._position is not None
        asyncio.create_task(self._run_trajectory(new_position))

    async def _run_trajectory(self, new_position: _Positions):
        # start moving to new position
        log(f"moving to {new_position.value}")
        self._position = None

        # emulate that it take some time to reach destination position,
        # scale travel time according to current speed ratio
        travel_time = 0.5 / self.speed.decimal_ratio
        await asyncio.sleep(travel_time)

        # we have arrived at our new position
        self._position = new_position
        log(f"reached {new_position.value}")

    def is_moving(self) -> bool:
        return self._position is None

    def get_position(self) -> _Positions:
        return self._position

    def get_position_name(self) -> str:
        if self._position is None:
            return "UNDEFINED"

        return self._position.value

    def change_speed(self, increase_speed: bool):
        if increase_speed:
            self.speed.increase()
        else:
            self.speed.decrease()


class _DewarLid:
    OPEN_POS = 10
    CLOSED_POS = 0

    def __init__(self):
        self._position = self.OPEN_POS
        self._target_position = None
        self._target_position_set = Event()

    def start(self):
        asyncio.create_task(self._run())

    def is_moving(self) -> bool:
        return self._target_position is not None

    async def _run(self):
        async def move_lid():
            while self._position != self._target_position:
                step = 1 if self._position < self._target_position else -1
                self._position += step
                await asyncio.sleep(0.6)

            self._target_position = None
            self._target_position_set.clear()

        while True:
            await self._target_position_set.wait()
            await move_lid()

    def open(self):
        self._target_position = self.OPEN_POS
        self._target_position_set.set()

    def close(self):
        self._target_position = self.CLOSED_POS
        self._target_position_set.set()


class _IsaraMixin(WatchableAttrsMixin):
    """
    contains code shared by ISARA and ISARA2 emulation
    """

    def __init__(self, operate_port: int, monitor_port: int):
        super().__init__()

        # TCP ports to use
        self._operate_port = operate_port
        self._monitor_port = monitor_port

        self._message = "System OK for operation"
        #
        # emulates the robot PLC modes, i.e. the key switch modes
        #
        # we only emulate:
        #   'remote mode' (remote_mode = True)
        #   'manual mode' (remote_mode = False)
        #
        self.remote_mode = True
        self.door_closed = True
        self.power_on = True

        # puck present in the dewar
        self.dewar_pucks = [False] * PUCKS_NUM
        # start with a couple of pucks present, for convenience
        self.dewar_pucks[0] = True
        self.dewar_pucks[PUCKS_NUM - 1] = True

        self._robot_arm = _RobotArm()
        self._dewar_lid = _DewarLid()

    #
    # public API for changing the state of the ISARA
    #

    def set_remote_mode(self):
        self.remote_mode = True

    def set_manual_mode(self):
        self.remote_mode = False

    def set_door_closed(self, is_closed: bool):
        self.door_closed = is_closed

    #
    # ISARA and ISARA2 common emulation code
    #

    def _handle_state_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _handle_di_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _handle_do_command(self):
        # needs model specific implementation
        raise NotImplementedError()

    def _check_plc(self) -> Optional[str]:
        if not self.remote_mode:
            return "Remote mode requested"

        if not self.door_closed:
            return "Doors must be closed"

        return None

    def _handle_on_command(self) -> str:
        plc_err = self._check_plc()
        if plc_err is not None:
            return plc_err

        self.power_on = True
        return "on"

    def _handle_off_command(self) -> str:
        plc_err = self._check_plc()
        if plc_err is not None:
            return plc_err

        self.power_on = False
        return "off"

    def _handle_message_command(self) -> str:
        return "System OK for operation"

    def _handle_speed_command(self, command: str):
        plc_err = self._check_plc()
        if plc_err is not None:
            return plc_err

        self._robot_arm.change_speed(command == SPEEDUP)

        return command

    def _handle_operate_command(self, command: str) -> str:
        if command == ON:
            return self._handle_on_command()
        if command == OFF:
            return self._handle_off_command()
        if command == ABORT:
            return "abort"
        if command in [SPEEDUP, SPEEDDOWN]:
            return self._handle_speed_command(command)

        assert False, f"unexpected command {command} on operate connection"

    def _handle_monitor_command(self, command: str) -> str:
        if command == STATE:
            return self._handle_state_command()
        if command == DI:
            return self._handle_di_command()
        if command == DO:
            return self._handle_do_command()
        if command == MESSAGE:
            return self._handle_message_command()

        assert False, f"unexpected command {command} on monitor connection"

    async def _new_operate_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new operate connection")
        try:
            while True:
                cmd = await _read_command("operate", reader)
                reply = self._handle_operate_command(cmd)

                await _write_reply("operate", writer, reply)
        except IncompleteReadError:
            # connection closed, we are done here
            return
        except:  # noqa
            print(traceback.format_exc())

    async def _new_monitor_connection(self, reader: StreamReader, writer: StreamWriter):
        log("new monitor connection")
        try:
            while True:
                cmd = await _read_command("monitor", reader)
                reply = self._handle_monitor_command(cmd)

                await _write_reply("monitor", writer, reply)
        except IncompleteReadError:
            # connection closed, we are done here
            return
        except:  # noqa
            # unexpected exception
            print(traceback.format_exc())

    async def start(self):
        self._dewar_lid.start()

        op_srv = await asyncio.start_server(
            self._new_operate_connection, host="0.0.0.0", port=self._operate_port
        )

        mon_srv = await asyncio.start_server(
            self._new_monitor_connection, host="0.0.0.0", port=self._monitor_port
        )

        await asyncio.gather(
            op_srv.serve_forever(),
            mon_srv.serve_forever(),
        )


class Isara(_IsaraMixin):
    """
    emulates ISARA robot, the first model, aka the blue robot at BioMAX
    """

    def _handle_state_command(self) -> str:
        power_on = _encode(self.power_on)
        remote_mode = _encode(self.remote_mode)
        speed_ratio = self._robot_arm.speed.ratio

        return f"state({power_on},{remote_mode},0,,,,,-1,-1,,,,0,0,,{speed_ratio},1.16,1.17,1.18,,,,)"

    def _handle_di_command(self) -> str:
        return "di(" + "0" * 99 + ")"

    def _handle_do_command(self) -> str:
        return "do(" + "0" * 99 + ")"

    def _handle_position_command(self) -> str:
        return "position(0.1,0.2,0.3,0.4,0.5,0.6)"

    def _handle_monitor_command(self, command: str) -> str:
        # handle ISARA1 specific monitor commands
        if command == POSITION:
            return self._handle_position_command()

        return super()._handle_monitor_command(command)


class Isara2(_IsaraMixin):
    """
    emulates ISARA2 robot, aka the yellow robot at MicroMAX
    """

    def _handle_state_command(self) -> str:
        power_on = _encode(self.power_on)
        remote_mode = _encode(self.remote_mode)
        position = self._robot_arm.get_position_name()
        path_running = _encode(self._robot_arm.is_moving())
        speed_ratio = self._robot_arm.speed.ratio

        return (
            f"state({power_on},{remote_mode},1,DoubleGripper,{position},,1,1,-1,-1,-1,-1,-1,"
            f"-1,-1,-1,,{path_running},0,{speed_ratio},0,0,0.3865678,75.0,72.0,1,0,0,"
            f"{self._message},67108864,152.9,-390.8,"
            "-17.3,-180.0,0.0,89.1,-75.6,-18.8,93.6,0.0,105.3,-165.5,,1,,1,0,0,0,0,"
            "0,0,0,0,0,0,0,0,0,changetool|3|3|0|-2.441|0.068|392.37|0.0|0.0|-0.984)"
        )

    def _handle_di_command(self) -> str:
        return (
            "di(0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,"
            "0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,"
            "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0)"
        )

    def _handle_do_command(self) -> str:
        puck_presence = _encode(self.dewar_pucks)

        return (
            "do("
            "0,0,1,0,0,1,0,1,0,0,"  # 00 - 09
            "1,0,0,0,0,0,0,0,0,0,"  # 10 - 19
            "0,0,0,1,0,0,0,0,0,0,"  # 20 - 29
            "0,0,0,0,0,0,0,0,0,0,"  # 30 - 39
            "0,0,0,1,0,0,0,0,0,0,"  # 40 - 49
            f"1,0,0,0,0,0,{puck_presence},0,0,0,0,0,"  # 50 - 89
            "0,0,0,0,0,0,0,0,0,0,"  # 90 - 99
            "0,0,0,0,0,0,0,0,0,0,"  # 100 - 110
            "0,0)"
        )

    def _handle_put_traj(self) -> str:
        if self._robot_arm.get_position() != _Positions.SOAK:
            return "Rejected - Trajectory must start at position: SOAK"

        return "put"

    def _handle_traj_command(self, name, *_) -> str:
        if not self.power_on:
            return "Robot power disabled"

        if self._robot_arm.is_moving():
            return "Path already running"

        if self._dewar_lid.is_moving():
            return "Disabled when lid is moving"

        if name == "soak":
            self._robot_arm.move_to(_Positions.SOAK)
            return "soak"

        if name == "home":
            self._robot_arm.move_to(_Positions.HOME)
            return "home"

        if name == "back":
            return "back"

        if name == "put":
            return self._handle_put_traj()

        raise NotImplementedError(f"running trajectory '{name}'")

    def _handle_openlid_command(self) -> str:
        self._dewar_lid.open()
        return "openlid"

    def _handle_closelid_command(self) -> str:
        self._dewar_lid.close()
        return "closelid"

    def _handle_clearmemory_command(self) -> str:
        if self._robot_arm.is_moving():
            return "Disabled when path is running"

        return "clearmemory"

    def _handle_reset_command(self) -> str:
        return "reset"

    def _handle_operate_command(self, command: str) -> str:
        #
        # handle ISARA2 specific operate commands
        #

        if command.startswith(TRAJ):
            args = _get_command_args(TRAJ, command)
            return self._handle_traj_command(*args)

        if command == OPENLID:
            return self._handle_openlid_command()

        if command == CLOSELID:
            return self._handle_closelid_command()

        if command == CLEARMEMORY:
            return self._handle_clearmemory_command()

        if command == RESET:
            return self._handle_reset_command()

        # handle generic operate commands
        return super()._handle_operate_command(command)


def create_emulator(
    model: str, operate_port: int, monitor_port: int, enable_logging=False
):
    global _logging_enabled
    _logging_enabled = enable_logging

    classes = {"ISARA": Isara, "ISARA2": Isara2}
    klass = classes[model]

    return klass(operate_port, monitor_port)
