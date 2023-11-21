from typing import Optional, Iterator
from dataclasses import dataclass
from sardana import State
from sardana.pool.controller import MotorController
from sardana.pool.controller import Type, Description


@dataclass
class _Motor:
    start_position: Optional[float] = None
    steps: Optional[Iterator[float]] = None
    position: Optional[float] = None


class FauxMotorController(MotorController):
    axis_attributes = {
        "StartPosition": {
            Type: float,
            Description: "moveable will start at this position, when Pool is initialized",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._motors = {}

    def getStartPosition(self, axis):
        # print(f"getStartPosition {axis=}")
        return self._motors[axis].start_position

    def setStartPosition(self, axis, value):
        # print(f"setStartPosition {axis=} {value=}")
        motor = self._motors[axis]

        motor.start_position = value

        if motor.position is None:
            motor.position = value

    def AddDevice(self, axis):
        # print(f"AddDevice {axis=}")
        self._motors[axis] = _Motor()

    def DeleteDevice(self, axis):
        # print(f"DeleteDevice {axis=}")
        del self._motor[axis]

    def StateOne(self, axis):
        # print(f"StateOne {axis=}")
        if self._motors[axis].steps:
            return State.Moving

        return State.On

    def _move_motor(self, motor: _Motor):
        if motor.steps is None:
            # no move steps, nothing to do here
            return

        try:
            motor.position = next(motor.steps)
        except StopIteration:
            motor.steps = None

    def ReadOne(self, axis):
        # print(f"ReadOne {axis=}")
        motor = self._motors[axis]
        self._move_motor(motor)

        return motor.position

    def StartOne(self, axis, position):
        # print(f"StartOne {axis=} {position=}")
        def steps(start, end, step_nums):
            step = (end - start) / step_nums
            for n in range(step_nums):
                yield start + step * n

            yield end

        motor = self._motors[axis]
        motor.steps = steps(motor.position, position, 10)
