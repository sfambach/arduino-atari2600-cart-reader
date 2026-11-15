# Wish list for the next board revision

Collected from Stefan on 2026-11-15. Not implemented yet; applies to all Atari cart reader boards.

- [ ] RGB LED (addressable or not) as indicator for reverse polarity and for processing/status.
- [ ] Push button at the board edge, left or right where there are no pins; also a variant with a right-angle button.
- [ ] Mounting holes for M3.
- [ ] Decoupling capacitor close to each IC (two ICs, two capacitors); place them vertically to the left/right of the IC, not horizontally.
- [ ] Fuse at the board edge.
- [ ] Move slot B further down (towards the board edge): with the cartridge guide fitted, the space between push button and module is only just enough (Stefan, 2026-11-15).
- [ ] Option for MCP23018 instead of MCP23017 (Stefan, 2026-11-15): same I2C registers, but open-drain outputs (need pull-ups on A0-A12, e.g. 2 x 10 kOhm SIP resistor networks, or the internal GPPU pull-ups if slow edges are acceptable), different DIP-28 pinout and an analog ADDR pin (to GND = 0x20). Needs its own footprint or a second footprint variant; firmware: enable GPPU, otherwise unchanged. Verify against the MCP23018 datasheet before layout.
- [ ] MCP23017 as SMD (SOIC-28, or SSOP-28) instead of DIP-28: considerably cheaper (Stefan, 2026-11-15). Same pinout as the DIP version; keep the decoupling capacitor close to it. Same for the MCP23018 option.
