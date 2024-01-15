from typing import Callable, Any


class UnknownCommand(Exception):
    def __init__(self, command: str):
        super().__init__(f"no such command: {command}")


class EmulatedDevice:
    def get_attribute_names(self) -> list[str]:
        raise NotImplementedError()

    def get_attribute(self, name: str) -> Any:
        raise NotImplementedError()

    def watch_attribute(self, attr_name: str, callback: Callable):
        raise NotImplementedError()

    def execute_command(self, command: str, args: list[Any]):
        raise NotImplementedError()
