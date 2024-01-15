from typing import Callable


class MultiKeyDict:
    def __init__(self):
        self._vals = {}

    def add(self, key, val):
        if key not in self._vals:
            self._vals[key] = [val]
        else:
            self._vals[key].append(val)

    def get(self, key):
        return self._vals.get(key, [])


class WatchableAttrsMixin:
    def __init__(self):
        self.__watched_attrs = MultiKeyDict()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        for callback in self.__watched_attrs.get(name):
            callback(value)

    def watch_attribute(self, attr_name: str, callback: Callable):
        self.__watched_attrs.add(attr_name, callback)
