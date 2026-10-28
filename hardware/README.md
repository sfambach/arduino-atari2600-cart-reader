# Boards

Through-hole (THT) boards that carry the 24-pin cartridge slot. Pinout matches `AtariCartReader/hal.h`. Version 1.2.

| Variant | Board | Size | Notes |
|---|---|---|---|
| [`uno/`](uno/) | Arduino Uno R3 shield | 68.6 × 53.3 mm | address bus via 2 × 74HC595 (SPI) |
| [`mega/`](mega/) | Arduino Mega 2560 shield | 101.6 × 53.3 mm | direct port wiring (PA, PC, PL) |
| [`nano/`](nano/) | carrier for a plugged-in Arduino Nano | 80 × 62 mm | same circuit and firmware as the Uno, 2 × M3 holes |
| [`uno-mcp23017/`](uno-mcp23017/) | Uno shield, alternative | 68.6 × 53.3 mm | address bus via MCP23017 (I²C), firmware with `#define ADDR_MCP23017` in `hal.h` |
| [`nano-mcp23017/`](nano-mcp23017/) | Nano carrier, alternative | 80 × 62 mm | address bus via MCP23017 (I²C), firmware with `#define ADDR_MCP23017` |

Each folder: KiCad 7 project, schematic PDF, Gerber + drill ZIP, render, DRC report (0 errors, 0 unconnected; remaining warnings are silkscreen near the board edge and, on the shields, the modified shield footprint).

Changes in 1.2: Uno and Nano address bus via two 74HC595 on SPI (MOSI D11, SCK D13, latch A2) instead of the MCP23017, which costs about 1.75 € (Reichelt); the MCP23017 boards stay as `-mcp23017` variants. Read button (SW2, A1 to GND) on all boards, reset button (SW1, on the Arduino RESET line) on the Uno and Mega shields (the Nano's own reset button stays reachable), 6 × 6 mm tactile switches; Uno: C1 moved right to make room.

Changes in 1.1: switched cartridge supply with polyfuse and orientation check, mounting holes for the slot flanges (M2.5) as fixing points for the 3D-printed guide, ICSP header removed from the shields (firmware goes over USB), Uno: the mounting hole next to the ICSP header removed, Mega: slot moved to the middle of the board. Silkscreen: each part shows reference and value ("R4 10k"), "fambach.net" in the front title.

## Switched cartridge supply

[`switch/schalter.png`](switch/schalter.png): the cartridge is only powered while the firmware reads it. A BC327 (PNP) switches pin 23, a 200 mA polyfuse limits a short, and A0 measures the switched rail.

- Before switching on, the firmware checks the orientation with the supply off: a weak pull-up on data line D2 back-feeds the cartridge's VCC through the ROM's protection diode only if the cartridge sits the right way round. A reversed cartridge (or none) leaves A0 low and the supply stays off.
- All address lines are held low during the check, so a reversed cartridge's A12 (on slot pin 7 = A1) keeps the ROM disabled.
- The ADC thresholds are not confirmed on hardware yet; the `S` command prints both readings for calibration.

| Signal | Uno / Nano | Mega |
|---|---|---|
| Switch (LOW = on) | D10 | D8 |
| Sense (via 10 kΩ) | A0 | A0 |

## Wiring

| Cartridge pin | Signal | Uno shield / Nano board | Mega shield |
|---|---|---|---|
| 8 … 1 | A0 … A7 | U1 QA … QH (74HC595) | D22 … D29 (PA0 … PA7) |
| 22, 21, 19, 20, 18 | A8, A9, A10, A11, A12 | U2 QA … QE (74HC595) | D37 … D33 (PC0 … PC4) |
| 9, 10, 11, 13 … 17 | D0 … D7 | D2 … D9 | D49 … D42 (PL0 … PL7) |
| 23 | +5 V (switched) | BC327 collector | BC327 collector |
| 12, 24 | GND | GND | GND |

Uno / Nano: U1 SER = MOSI (D11), U1 QH' → U2 SER, SRCLK = SCK (D13), RCLK = latch (A2), OE to GND, SRCLR to +5 V; U2 QF–QH unused. The firmware shifts A8–A12 first, then A0–A7.

MCP23017 variants: MCP23017 at I2C 0x20 (A0–A2 to GND, RESET to +5 V), SDA = A4, SCL = A5 with 4k7 pull-ups; GPA0–7 = A0–A7, GPB0–4 = A8–A12.

## Bill of materials

| Ref | Part | Uno | Mega | Nano |
|---|---|---|---|---|
| J1 | Atari 2600 cartridge slot, 2 × 12, 2.54 mm | 1 | 1 | 1 |
| U1, U2 | 74HC595 (DIP-16) + DIP-16 socket | 2 | – | 2 |
| R3 | 1 kΩ, axial | 1 | 1 | 1 |
| R4, R5 | 10 kΩ, axial | 2 | 2 | 2 |
| R6 | 100 kΩ, axial | 1 | 1 | 1 |
| Q1 | BC327 (PNP, TO-92) | 1 | 1 | 1 |
| F1 | Polyfuse 200 mA radial, 5.08 mm (MF-R020, RXEF020) | 1 | 1 | 1 |
| C1, C2, C4 | 100 nF ceramic, 5 mm pitch | 3 | 1 (C2) | 3 |
| C3 | 10 µF electrolytic, 5 mm, 2 mm pitch | 1 | 1 | 1 |
| SW1, SW2 | Tactile switch 6 × 6 mm THT (SW1 reset, SW2 read) | 2 | 2 | 1 (SW2) |
| – | Stacking headers (Uno: 6, 8, 8, 10; Mega shield set) or 2 × 15 female headers (Nano) | 1 set | 1 set | 2 |
| – | M2.5 screws for the slot flanges / guide | 2 | 2 | 2 |

MCP23017 variants instead of U1/U2 and C4: U1 MCP23017-E/SP (DIP-28) + DIP-28 socket, R1/R2 4.7 kΩ axial, C1 100 nF.

## Assumptions

- **Slot row spacing 5.5 mm** centre to centre, pitch 2.54 mm, flange holes 45.5 mm apart. Footprint: `lib/atari.pretty`.
- **Guide base plate 61 × 17 mm** around the slot (dashed on F.Fab): no other parts there; `generator/plate.py` checks this on every build. The guide itself is not designed yet.
- The pin 13–24 row is the cartridge's label side (silkscreen "Etikettseite").
- Not built or tested yet.

## Cartridge orientation

[`pinout/pinout.png`](pinout/pinout.png) shows the cartridge contacts seen from below with the label up: pins 13–24 (D3 … +5V, GND) are on the label side, pins 1–12 (A7 … GND) on the back. Pin k sits opposite pin 25 − k, so a cartridge inserted the wrong way round puts +5V on D2. Sources: [WiringVCS](https://github.com/drzaiusx11/WiringVCS) and [The Hardware Book](https://isa.umh.es/temas/micros/doc/hwb/co_CartridgeAtari2600.html); quick check: pin 23 has continuity to the ROM's VCC pin.

## Cartridge slot drawing

[`slot-drawing/slot-masse.png`](slot-drawing/slot-masse.png) is a 2D dimension sketch of the 24-pin cartridge slot (top, front, side and bottom views), measured by hand; `zeichnung.py` regenerates it. It is the basis for the planned 3D-printed cartridge guide. A slot from another source may differ, so check these values first:

- Pins 2×12, pitch 2.54 mm, rows 5.5 mm apart (centre to centre).
- Overall length 51.3 mm, width 9 mm, height 16.1 mm above the board (6 mm lower part + 10.1 mm upper part).
- Lower part below the flanges: 35 mm long, 6 mm high, 7.4 mm wide.
- Body between the flanges 36.8 mm. Mounting flanges 7.2 mm long, 7.1 mm wide (across the pin rows), 6.5 mm high, with a Ø2.8 mm hole centred 2.9 mm from the outer edge.
- Flange underside flush with the top of the lower part (6 mm above the board), flange top at 12.5 mm. That leaves 3.6 mm to the slot top (confirmed).
- Card slot opening: 33.3 mm long, 2.2 mm wide; the spring contacts close to about 1.4 mm (estimated), which suits a 1.6 mm cartridge PCB. Slot depth 9 mm.

The measured slot sat on round-pin socket strips for extra height. They are not needed and are left out; the guide sets the cartridge height instead.

## Rebuild

Needs KiCad 7 (pcbnew Python), `xvfb-run`, Java and [Freerouting 1.9.0](https://github.com/freerouting/freerouting) at `/opt/tools/freerouting.jar` (or `FREEROUTING=`).

```
sh generator/build.sh uno|mega|nano     # schematic, board, routing, DRC, guide-plate check
sh generator/outputs.sh uno|mega|nano   # Gerber ZIP, schematic PDF, render
```

`generator/boards.py` holds netlist and placement.

## Credits

Arduino shield symbols and footprints: [arduino-kicad-library](https://github.com/Alarm-Siren/arduino-kicad-library) by Alarm-Siren, CC BY-SA 4.0 (`lib/LICENSE-arduino-library.txt`).
