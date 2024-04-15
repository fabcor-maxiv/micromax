#!/usr/bin/env python
from tango import AttrWriteType
from tango.server import Device, attribute

ATTRIBUTES = [
    # Eiger detector cover tags
    "B312A_E06_DIA_DETC01_ENAC",
    "B312A_E06_DIA_DETC01_OPC",
    "B312A_E06_DIA_DETC01_CLC",
    # Jungfrau detector cover tags
    "B312A_E06_DIA_DETC02_ENAC",
    "B312A_E06_DIA_DETC02_OPC",
    "B312A_E06_DIA_DETC02_CLC",
]


class VacPlc01(Device):
    """
    emulate (small subset) of b312a/vac/plc-01 device
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_attrs()

    def _init_attrs(self):
        for attr_name in ATTRIBUTES:
            attr = attribute(
                name=attr_name, dtype=bool, access=AttrWriteType.READ_WRITE
            )
            self.add_attribute(attr, lambda _, __: False, lambda _, __: None)


if __name__ == "__main__":
    VacPlc01.run_server()
