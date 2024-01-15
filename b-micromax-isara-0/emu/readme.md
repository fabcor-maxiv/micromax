# ISARA emulator

Emulates network traffic of an ISARA sample changer robot.
Supports emulating ISARA2 systems and older ISARA system to a limited degree.
The emulator is used by the unit tests.

## Emulator API

To start the emulator create an emulator object with `emu.isara.create_emulator()`.
This function allows you to specify if ISARA or ISARA2 model should be emulated.
Call `start()` method on the emulator objects.
The `start()` method returns an async coroutine, that you need to run in the  asyncio loop.

### Emulator Object Methods

The emulator object returned by `create_emulator()` function provides methods to manipulate it's state.
These methods provide a way to simulate external action affecting the robot.
For example method `set_remote_mode()` allows to programmatically emulate turning the PLC key to _manul mode_ position.
Below are description of all available methods.

#### set_remote_mode()

Set robot's PLC to _remote mode_.
Simulates turning the PLC control key to _remote mode_ position.

#### set_manual_mode()

Set robot's PLC to _manual mode_.
Simulates turning the PLC control key to _manual mode_ position.

#### set_door_closed(is_closed: bool)

Sets robot's PLC hutch doors closed state.
When `is_closed` is `True`, simulates the states when the hutch is searched.
On `False`, simulates that the hutch is not searched.

### Watchable Emulator Attributes

The emulator objects have a number of attributes that reflect the state of the robot.
Use `watch_attribute()` method on the emulator object to register attribute change callbacks.
`watch_attribute()` takes two parameters, attribute name and a callable.
When the attribute value changes, the callable will be invoked with the attribute's new value.
Following attributes can be watched:

| name        | type       | purpose                     |
|-------------|------------|-----------------------------|
| remote_mode | bool       | is remote enabled?          |
| door_closed | bool       | is hutch door closed?       |
| power_on    | bool       | is robot power on?          |
| dewar_pucks | list(bool) | pucks detected in the dewar |
