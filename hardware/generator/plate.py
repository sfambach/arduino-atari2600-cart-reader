# Checks that no other footprint reaches into the base plate of the 3D-printed cartridge guide (61 x 17 mm around J1).
import sys
import pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
j1 = b.FindFootprintByReference('J1')
ang = round(j1.GetOrientationDegrees()) % 180
dx, dy = (30.5, 8.5) if ang == 0 else (8.5, 30.5)
pads = [p.GetPosition() for p in j1.Pads()]
cx = sum(p.x for p in pads) / len(pads); cy = sum(p.y for p in pads) / len(pads)
x0, x1 = pcbnew.ToMM(cx) - dx, pcbnew.ToMM(cx) + dx
y0, y1 = pcbnew.ToMM(cy) - dy, pcbnew.ToMM(cy) + dy
err = 0
for f in b.GetFootprints():
    if f.GetReference() in ('J1', 'A1'):
        continue
    bb = f.GetBoundingBox(False, False)
    fx0, fy0, fx1, fy1 = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())
    if fx0 < x1 and fx1 > x0 and fy0 < y1 and fy1 > y0:
        print('plate overlap', f.GetReference()); err += 1
print('plate %.2f..%.2f x %.2f..%.2f, overlaps %d' % (x0, x1, y0, y1, err))
sys.exit(1 if err else 0)
