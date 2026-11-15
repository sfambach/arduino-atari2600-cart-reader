# Board tests

Run these before using a freshly built board with a cartridge. **Never insert a cartridge while a test runs.**

## mcp23017_test

For the Uno / Nano MCP23017 boards. Open `mcp23017_test/mcp23017_test.ino` in the Arduino IDE (settings in `config.h`), upload, open the serial monitor (baud rate from `config.h`, default 115200, line ending "Newline").

1. I2C scan: the MCP23017 must answer at 0x20.
2. Register write / read back over I2C.
3. All address lines (MCP23017) and data lines (D2-D9) high with pull-ups: a low line is shorted to GND.
4. Walking low: one line pulled low, all others must stay high. Reports the shorted pair with slot pin numbers.

The cartridge supply (D10) stays off the whole time. A short to +5 V is not detected; check slot pin 23 against the address and data pins with a multimeter.

Commands after the run:

| Command | Action |
|---|---|
| `t` | run the tests again |
| `w` | walking one: each address line HIGH for 2 s, for measuring at the slot |
| `a1FFF` | put a fixed address (hex) on A0-A12 |
| `r` | release all lines |

## supply_test

Second test: switched cartridge supply and orientation check (all boards). Settings in `supply_test/config.h`; enable your board at the top (`BOARD_MEGA`, `BOARD_UNO`, `BOARD_UNO_MCP23017`, `BOARD_NANO`, `BOARD_NANO_MCP23017`).

Without cartridge (runs at start, `t` repeats):

1. Supply off: A0 below the orientation threshold.
2. Orientation check on an empty slot: stays low, so the firmware would not switch on.
3. Supply on: A0 above the powered threshold (BC327 and fuse work).
4. Supply off again: the rail falls back, time is printed.

With a cartridge: `o` prints the orientation reading (right way round or not), `p` switches on only if the orientation is right and checks the voltage under load, then switches off.

Both sketches: not compiled or run on hardware yet.
