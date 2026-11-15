"""Builds cartridge_guide.stl with manifold3d; same geometry as cartridge_guide.scad."""
import math, sys
import numpy as np
import manifold3d as m3d
import trimesh

slot_top, plate, gap = 27.0, 2.0, 2.0
top = slot_top + plate
cap_l, cap_w, off = 74.2, 15.2, 2.1
full_z, foot_x, band = 17.0, 25.5, 8.5
step_z = slot_top + plate - 18.5
cav_l, cav_w = 37.6, 10.1
slit_l, slit_w = 35.1, 2.5
nub_x0, nub_x1, nub_w, nub_depth = 28.3, 36.1, 2.7, 16.0
opn_x0, opn_x1, opn_t, opn_h = 21.4, 28.0, 1.9, 6.0
hole_x, screw_d, screw_depth = 22.75, 2.2, 10.0

def box(x0, y0, z0, x1, y1, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

prof = m3d.CrossSection([[(-foot_x, gap), (foot_x, gap), (cap_l / 2, full_z), (cap_l / 2, top), (-cap_l / 2, top), (-cap_l / 2, full_z)]])
body = m3d.Manifold.extrude(prof, cap_w).translate([0, 0, -cap_w / 2]).rotate([90, 0, 0])
for s in (-1, 1):
    x0, x1 = (opn_x0, opn_x1) if s > 0 else (-opn_x1, -opn_x0)
    body = body + box(x0, off - opn_t / 2, top - 0.01, x1, off + opn_t / 2, top + opn_h)
cut = box(-50, -cap_w / 2 - 1, -1, 50, off - band, step_z)
cut = cut + box(-cav_l / 2, off - cav_w / 2, -1, cav_l / 2, off - cav_w / 2 + cap_w, slot_top)
cut = cut + box(-slit_l / 2, off - slit_w / 2, slot_top - 1, slit_l / 2, off + slit_w / 2, top + 1)
for s in (-1, 1):
    x0, x1 = (nub_x0, nub_x1) if s > 0 else (-nub_x1, -nub_x0)
    cut = cut + box(x0, off - nub_w / 2, top - nub_depth, x1, off + nub_w / 2, top + 1)
    cut = cut + m3d.Manifold.cylinder(gap + screw_depth + 1, screw_d / 2, screw_d / 2, 32).translate([s * hole_x, off, -1])
part = body - cut
mesh = part.to_mesh()
tm = trimesh.Trimesh(np.array(mesh.vert_properties)[:, :3], np.array(mesh.tri_verts))
tm.apply_translation([0, 0, -gap])     # feet on z = 0 for printing
tm.export(sys.argv[1] if len(sys.argv) > 1 else 'cartridge_guide.stl')
print('watertight', tm.is_watertight, 'volume', round(tm.volume, 1), 'bounds', tm.bounds.round(2).tolist())
