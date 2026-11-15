# Cartridge guide (3D print)

A cap that sits on cartridge slot B (on pin headers, slot top 27 mm above the PCB)
and guides the cartridge onto the slot. Drawing and assumptions: [`drawing/`](drawing/).

| File | What |
|---|---|
| `cartridge_guide.scad` | OpenSCAD source (parameters at the top) |
| `cartridge_guide.py` | Same geometry built with `manifold3d`, writes the STL |
| `cartridge_guide.stl` | First test print (tapered ends, 2 mm gap under the feet) |
| `cartridge_guide_gerade.stl` | Variant 2 (`--straight`): ends straight down to the PCB, no step, no gap |

- Sleeve, PCB slit (2.1 mm off centre), key holes and door openers are taken from
  `vcsslot.stl` by RabbitEngineering (Thingiverse 618065, CC BY-NC).
- Print upright, feet on the bed, no supports (slopes 38° from vertical). The top over the
  slot is a 37.6 mm bridge on side B.
- Fixed with two M2.5 screws from below through the PCB. The feet stay 2 mm above the PCB,
  so the screws pull the cap down onto the slot.
- The STL was generated with `python3 cartridge_guide.py`; the `.scad` file has not been
  rendered in OpenSCAD yet.
- Variant 2 covers the full 74.2 × 15.2 mm on the PCB. Only 61 × 17 mm around the slot was checked to be free of parts.

## Mounting direction

Checked by Stefan on the test print (2026-11-15): side A (closed) sits over pins 13–24, the cartridge label side. Side B (open) sits over pins 1–12.

## Changes after the first test print (2026-11-15)

- Slope-to-side corner on both ends rounded (r = 6 mm), so the overhang fades out instead of ending in a sharp edge; feet and top stay square.
- Opener tips chamfered by 0.5 mm.
- The openers are small (6.6 × 1.9 mm): set a minimum layer time of 15 s in the slicer so they can cool (10 s was not enough on the first print, Stefan 2026-11-15).
- `cartridge_guide.scad` does not have these changes yet; the STL comes from `cartridge_guide.py`.
