# Cartridge guide (3D print)

A cap that sits on cartridge slot B (on pin headers, slot top 27 mm above the PCB)
and guides the cartridge onto the slot. Drawing and assumptions: [`../guide-drawing/`](../guide-drawing/).

| File | What |
|---|---|
| `cartridge_guide.scad` | OpenSCAD source (parameters at the top) |
| `cartridge_guide.py` | Same geometry built with `manifold3d`, writes the STL |
| `cartridge_guide.stl` | First test print |

- Sleeve, PCB slit (2.1 mm off centre), key holes and door openers are taken from
  `vcsslot.stl` by RabbitEngineering (Thingiverse 618065, CC BY-NC).
- Print upright, feet on the bed, no supports (slopes 38° from vertical). The top over the
  slot is a 37.6 mm bridge on side B.
- Fixed with two M2.5 screws from below through the PCB. The feet stay 2 mm above the PCB,
  so the screws pull the cap down onto the slot.
- The STL was generated with `python3 cartridge_guide.py`; the `.scad` file has not been
  rendered in OpenSCAD yet.
