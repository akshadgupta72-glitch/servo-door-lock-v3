# Arduino Configuration Code

[DoorLockConfig/DoorLockConfig.ino](DoorLockConfig/DoorLockConfig.ino) contains
the project author's supplied C++ sketch, preserved without behavior changes.
It is a prototype example, not production security firmware or a low-power
implementation. It is licensed under the repository's [MIT license](../LICENSES/MIT.txt).

## Setup

1. Install **Servo** and **IRremote** (the modern library providing
   `IRremote.hpp`) through Arduino IDE's Library Manager.
2. Open `DoorLockConfig/DoorLockConfig.ino`. Keep the enclosing folder named
   `DoorLockConfig` so Arduino recognizes the sketch.
3. For the original Uno R3 setup, select **Arduino Uno** and its serial port.
   A different board, including a 3.3V/8MHz Pro Mini, needs its own board and
   processor selection, appropriate programmer, and electrical compatibility
   checks; this sketch does not configure those automatically.
4. Test with the linkage disconnected before uploading to an assembled lock:
   startup immediately commands the rest position.
5. Open Serial Monitor at **9600 baud** to see startup and command messages.

| Connection / setting | Value |
| --- | --- |
| Servo signal | D9 |
| IR receiver output | D2 |
| Passive buzzer control | D13 |
| Rest / commanded unlocked angle | 0 degrees |
| Commanded locked angle | 70 degrees |
| Buzzer frequency / duration | 1000 Hz / 100 ms |

These are signal assignments, not a complete power schematic. Use a suitable
regulated servo supply and a common signal ground. Verify the receiver's
actual pinout and voltage, and use a buzzer driver if its current exceeds
the board's GPIO rating. Never apply the raw 7.4V battery to a 5V/3.3V rail
or the SG90 servo, and do not power the servo from a GPIO pin.

## Compile Check

Compiled for `arduino:avr:uno` with Arduino AVR Boards **1.8.8**, Servo
**1.3.0**, and IRremote **4.7.1**. The supplied sketch uses **10,156 bytes of
flash (31%)** and **592 bytes of RAM (28%)** with that toolchain.

```sh
arduino-cli compile --fqbn arduino:avr:uno --warnings all arduino/DoorLockConfig
```

Run the command from the repository root. No sketch was uploaded and no
physical lock or IR/buzzer behavior was tested as part of this compile check.

## Behavior and Known Limitations

- Every decoded message without `IRDATA_FLAGS_IS_REPEAT` toggles the commanded
  state. There is no remote address, protocol or command whitelist, nor
  authentication. Other remotes or unwanted decoded messages can operate it.
- Restarting or resetting always sets `isLocked` to false and commands
  `REST_ANGLE`. There is no position sensor: the boolean records the command,
  not proof that the physical lock moved or engaged.
- The source's 70-degree endpoint is intentionally unchanged. The CAD model
  uses 90 degrees for 35 mm of travel; at its ideal 70-degree pose it moves
  about 32.9 mm (3.29 cm). Calibrate to the actual mechanism without forcing
  it against an end stop.
- **Uno timer conflict:** with IRremote's default AVR timer configuration,
  `tone()` shares the receiving timer and can stop subsequent IR reception.
  `IrReceiver.resume()` does not restore that timer. The library documents
  stopping and restarting the IR timer around a completed beep; this supplied
  sketch has not been changed to implement that fix. See the
  [IRremote timer-conflict documentation](https://github.com/Arduino-IRremote/Arduino-IRremote#receiving-stops-after-analogwrite-or-tone-or-after-running-a-motor).
- The servo stays attached. There is no sleep mode, power switching, movement
  confirmation, jam detection, battery monitoring, or battery-runtime guarantee.

A successful compile is not a hardware test. Keep an independent manual
release and do not rely on this example to secure a door or provide emergency
egress.
