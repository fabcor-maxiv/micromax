#!/usr/bin/env python

from tango.server import Device, attribute


class VacPlc01(Device):
    """
    emulate (small sumbset) of b312a/vac/plc-01 device
    """

    #
    # write only emulation of B312A_E06_DIA_DETC01_ENAC attribute
    #
    _attr0 = attribute(name="B312A_E06_DIA_DETC01_ENAC", dtype=bool)

    @_attr0.setter
    def _attr0_write(self, value):
        pass

    #
    # write only emulation of B312A_E06_DIA_DETC01_OPC attribute
    #
    _attr1 = attribute(name="B312A_E06_DIA_DETC01_OPC", dtype=bool)

    @_attr1.setter
    def _attr1_write(self, value):
        pass

    #
    # write only emulation of B312A_E06_DIA_DETC01_CLC attribute
    #
    _attr2 = attribute(name="B312A_E06_DIA_DETC01_CLC", dtype=bool)

    @_attr2.setter
    def _attr2_write(self, value):
        pass


if __name__ == "__main__":
    VacPlc01.run_server()
