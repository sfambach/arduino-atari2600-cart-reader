# Shields

Two through-hole (THT) shields that carry the 24-pin cartridge slot. Pinout matches `AtariCartReader/hal.h`.

| Variant | Board | Size | Parts |
|---|---|---|---|
| [`uno/`](uno/) | Arduino Uno R3 | 68.6 × 53.3 mm | slot, MCP23017 (socket), 2 × 4k7, 2 × 100n, 10µ |
| [`mega/`](mega/) | Arduino Mega 2560 | 101.6 × 53.3 mm | slot, 100n, 10µ |

Each folder: KiCad 7 project, schematic PDF, Gerber + drill ZIP, render, DRC report (0 errors, 0 unconnected; only silkscreen-at-edge warnings from the shield outline).

## Wiring

| Cartridge pin | Signal | Uno shield | Mega shield |
|---|---|---|---|
| 8 … 1 | A0 … A7 | MCP23017 GPA0 … GPA7 | D22 … D29 (PA0 … PA7) |
| 22, 21, 19, 20, 18 | A8, A9, A10, A11, A12 | MCP23017 GPB0 … GPB4 | D37 … D33 (PC0 … PC4) |
| 9, 10, 11, 13 … 17 | D0 … D7 | D2 … D9 | D49 … D42 (PL0 … PL7) |
| 23 | +5 V | 5V | 5V |
| 12, 24 | GND | GND | GND |

Uno: MCP23017 at I2C 0x20 (A0–A2 to GND, RESET to +5 V), SDA = A4, SCL = A5 with 4k7 pull-ups.

## Bill of materials

| Ref | Part | Uno | Mega |
|---|---|---|---|
| J1 | Atari 2600 cartridge slot, 2 × 12, 2.54 mm | 1 | 1 |
| U1 | MCP23017-E/SP (DIP-28) + DIP-28 socket | 1 | – |
| R1, R2 | 4.7 kΩ, axial | 2 | – |
| C1, C2 | 100 nF ceramic, 5 mm pitch | 2 | 1 |
| C3 | 10 µF electrolytic, 5 mm, 2 mm pitch | 1 | 1 |
| – | Stacking headers for Uno (6, 8, 8, 10) or Mega shield set | 1 set | 1 set |

## Assumptions

- **Slot row spacing 5.5 mm** centre to centre (measured: 6 mm across the outer pin edges, pins 0.5 mm), pitch 2.54 mm. Footprint: `lib/atari.pretty`.
- Cartridge body sits over the slot: keep-out ±11 mm across the slot for parts taller than the slot.
- Not built or tested yet.

## Cartridge slot drawing

[`slot-drawing/slot-masse.png`](slot-drawing/slot-masse.png) is a 2D dimension sketch of the 24-pin cartridge slot (top, front, side and bottom views), measured by hand; `zeichnung.py` regenerates it. It is the basis for the planned 3D-printed cartridge guide. A slot from another source may differ, so check these values first:

- Pins 2×12, pitch 2.54 mm, rows 5.5 mm apart (centre to centre).
- Overall length 51.3 mm, width 9 mm, height 16.1 mm above the board (6 mm lower part + 10.1 mm upper part).
- Lower part below the flanges: 35 mm long, 6 mm high (width assumed 9 mm).
- Body between the flanges 36.8 mm. Mounting flanges 7.2 mm long, 7.1 mm wide (across the pin rows), 6.5 mm high, with a Ø2.8 mm hole centred 2.9 mm from the outer edge.
- Flange underside flush with the top of the lower part (6 mm above the board), flange top at 12.5 mm. That leaves 3.6 mm to the slot top; measured were 3.1–3.4 mm, so one value is about 0.3 mm off (open).
- Card slot opening: not yet measured.

The measured slot sat on round-pin socket strips for extra height. They are not needed and are left out; the guide sets the cartridge height instead.

## Rebuild

Needs KiCad 7 (pcbnew Python), `xvfb-run`, Java and [Freerouting 1.9.0](https://github.com/freerouting/freerouting) at `/opt/tools/freerouting.jar` (or `FREEROUTING=`).

```
sh generator/build.sh uno
sh generator/build.sh mega
```

`generator/boards.py` holds netlist and placement; the scripts build schematic, board, route and DRC.

## Credits

Arduino shield symbols and footprints: [arduino-kicad-library](https://github.com/Alarm-Siren/arduino-kicad-library) by Alarm-Siren, CC BY-SA 4.0 (`lib/LICENSE-arduino-library.txt`).
