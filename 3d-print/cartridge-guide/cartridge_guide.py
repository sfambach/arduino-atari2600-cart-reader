"""Builds cartridge_guide.stl with manifold3d; same geometry as cartridge_guide.scad."""
import math, sys
import numpy as np
import manifold3d as m3d
import trimesh

STRAIGHT = '--straight' in sys.argv   # variant 2 (Stefan 15.11.2026): ends straight down to the PCB, no step, no gap
args = [a for a in sys.argv[1:] if not a.startswith('--')]
slot_top, plate = 27.0, 2.0
gap = 0.0 if STRAIGHT else 2.0
top = slot_top + plate
cap_l, cap_w, off = 74.2, 15.2, 2.1
full_z, foot_x, band = (gap, cap_l / 2, 99.0) if STRAIGHT else (17.0, 30.0, 8.5)
step_z = slot_top + plate - 18.5
cav_l, cav_w = 37.6, 10.1
slit_l, slit_w = 35.1, 2.5
nub_x0, nub_x1, nub_w, nub_depth = 28.3, 36.1, 2.7, 12.0   # closed at the bottom (Stefan 15.11.2026)
opn_x0, opn_x1, opn_t, opn_h = 21.4, 28.0, 1.9, 6.0
hole_x, screw_d, screw_depth = 22.75, 2.2, 10.0

def box(x0, y0, z0, x1, y1, z1):
    return m3d.Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

edge_r = 0.0 if STRAIGHT else 6.0     # rounded slope-to-side corner (no new overhang), feet and top stay square (Stefan 15.11.2026)

def rounded(points, radius, keep):
    """Replaces each corner not in keep by an arc of the given radius (fillet)."""
    out, n = [], len(points)
    for i, p in enumerate(points):
        if i in keep or radius <= 0:
            out.append(p); continue
        a, b = np.array(points[i - 1]), np.array(points[(i + 1) % n])
        p = np.array(p)
        u, v = (a - p) / np.linalg.norm(a - p), (b - p) / np.linalg.norm(b - p)
        half = math.acos(np.clip(np.dot(u, v), -1, 1)) / 2
        d = radius / math.tan(half)
        t0, t1 = p + u * d, p + v * d
        c = p + (u + v) / np.linalg.norm(u + v) * radius / math.sin(half)
        a0, a1 = math.atan2(*(t0 - c)[::-1]), math.atan2(*(t1 - c)[::-1])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for k in range(13):
            ang = a0 + da * k / 12
            out.append((c[0] + radius * math.cos(ang), c[1] + radius * math.sin(ang)))
    return out

corners = [(-foot_x, gap), (foot_x, gap), (cap_l / 2, full_z), (cap_l / 2, top), (-cap_l / 2, top), (-cap_l / 2, full_z)]
prof = m3d.CrossSection([rounded(corners, edge_r, keep={0, 1, 3, 4})])
body = m3d.Manifold.extrude(prof, cap_w).translate([0, 0, -cap_w / 2]).rotate([90, 0, 0])
for s in (-1, 1):
    x0, x1 = (opn_x0, opn_x1) if s > 0 else (-opn_x1, -opn_x0)
    # openers: 0.5 mm chamfer on the tip so the thin tops print cleaner and slide into the cartridge
    tip = box(x0 + 0.5, off - opn_t / 2 + 0.5, top + opn_h - 0.01, x1 - 0.5, off + opn_t / 2 - 0.5, top + opn_h)
    stem = box(x0, off - opn_t / 2, top - 0.01, x1, off + opn_t / 2, top + opn_h - 0.5)
    body = body + m3d.Manifold.batch_hull([stem, tip])
cut = m3d.Manifold()   # no step on side A (Stefan 15.11.2026)
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
tm.export(args[0] if args else 'cartridge_guide.stl')
print('watertight', tm.is_watertight, 'volume', round(tm.volume, 1), 'bounds', tm.bounds.round(2).tolist())
