# MicroMAX emulation

A series of docker images that emulate MicroMAX beamline.
The aim of the emulation is to be able to run MxCube, as it's deployed at MicroMAX, inside one of the containers.

## Building

To build all required images run:

    docker compose build

Note that you need to be on MAXIV white network, when building images.
The images are cloning code from MAXIV internal repositories.

## Running

Start emulation with:

    docker compose up

## Images

### `mysql`

Hosts the MicroMAX tango database.

### `tango-cs`

The 'tango host' of the MicroMAX tango devices.

### `micromax-ds`

Runs the emulated MicroMAX tango device servers.
Runs the Sardana Pool and MacroServers with emulated MicroMAX elements.

### `mysql-2`

Host 'csproxy' tango database.

### `g-v-csproxy-0`

The 'tango host' of the 'csproxy' tango devices.

### `csproxy-ds`

Runs emulated 'csproxy' devices.

### `mxcube`

Run the MxCube.

### `b-micromax-md3-pc`

Run MD3Up diffractometer exporter emulator.

### `dbg`

Can be used for debugging and troubleshooting.
