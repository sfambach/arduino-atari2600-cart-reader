# Board tests

Run these before using a freshly built board with a cartridge. **Never insert a cartridge while a test runs.**

## Settings

All sketches (firmware and tests) share one `config.h`. Edit only the master copy `firmware/AtariCartReader/config.h` (select the board at the top: `BOARD_MEGA`, `BOARD_UNO`, `BOARD_UNO_MCP23017`, `BOARD_NANO`, `BOARD_NANO_MCP23017`), then run

```
python3 tools/sync_config.py
```

to copy it into every test sketch; `--check` only reports copies that differ. The Arduino IDE cannot include files from outside a sketch folder, hence the copies.

## bus_test

Address and data bus of all five boards. Upload, open the serial monitor (baud rate from `config.h`, line ending "Newline").

1. MCP23017 boards only: I2C scan (MCP23017 at `MCP_ADDR`) and register write / read back.
2. All lines high with pull-ups: a low line is shorted to GND.
3. Walking low: one line pulled low, all others must stay high. Reports the shorted pair with slot pin numbers.

On the 74HC595 boards the address outputs cannot be read back, so only the data lines are checked automatically; check A0-A12 with `w` and a multimeter.

The cartridge supply stays off the whole time. A short to +5 V is not detected; check slot pin 23 against the address and data pins with a multimeter.

Commands after the run:

| Command | Action |
|---|---|
| `t` | run the tests again |
| `w` | walking one: each address line HIGH in turn (`WALK_STEP_MS`), for measuring at the slot |
| `a1FFF` | put a fixed address (hex) on A0-A12 |
| `r` | release all lines |

## supply_test

Switched cartridge supply and orientation check (all five boards).

Without cartridge (runs at start, `t` repeats):

1. Supply off: A0 below `SENSE_OFF`.
2. Orientation check on an empty slot: all data lines high with pull-ups.
3. Supply on: A0 above the powered threshold (BC327 and fuse work).
4. Supply off again: the rail falls back, time is printed.

With a cartridge: `o` runs the orientation check as in the firmware (any data line low = reversed), `p` switches on only if the cartridge sits the right way round and checks the voltage under load, then switches off, `1` / `0` switch the supply on / off by hand (reading printed every second).

Both tests: syntax-checked for all five boards against stub headers; not built with the Arduino toolchain or run on hardware yet.
