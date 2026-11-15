// Cartridge guide (cap) for slot B on pin headers, draft 5 (see drawing/).
// NOTE: the rounded slope corners and chamfered opener tips of cartridge_guide.py (2026-11-15) are not ported here yet; the STL is built from cartridge_guide.py.
// Sleeve, slit, key holes and door openers taken from vcsslot.stl
// (RabbitEngineering, Thingiverse 618065, CC BY-NC).
// x = along the slot, y = across (side A negative, side B positive), z = up from the PCB.
// Print upright, feet on the bed.

slot_top   = 27.0;    // slot B top above the PCB (measured)
plate      = 2.0;     // closed top, rests on the slot
gap        = 2.0;     // gap under the feet; the screws pull the cap onto the slot
top        = slot_top + plate;
cap_l      = 74.2;    // sleeve length (vcsslot)
cap_w      = 15.2;    // sleeve width (vcsslot)
off        = 2.1;     // slit centre towards side B (vcsslot 2.06)
full_z     = 17.0;    // full length above this height
foot_x     = 30.0;    // half length of the foot (61 mm wide: slopes 25° from vertical)
band       = 8.5;     // below step_z max. 8.5 from slot centre (free area 61 x 17)
step_z     = slot_top + plate - 18.5;   // cartridge shell bottom
cav_l      = 37.0 + 0.6;
cav_w      = 9.5 + 0.6;
slit_l     = 35.1;
slit_w     = 2.5;
nub_x0     = 28.3;  nub_x1 = 36.1;  nub_w = 2.7;  nub_depth = 12;   // closed at the bottom
opn_x0     = 21.4;  opn_x1 = 28.0;  opn_t = 1.9;  opn_h = 6.0;
hole_x     = 22.75; screw_d = 2.2;  screw_depth = 10;

module body() {
    rotate([90, 0, 0]) translate([0, 0, -cap_w / 2])
        linear_extrude(cap_w)
            polygon([[-foot_x, gap], [-cap_l / 2, full_z], [-cap_l / 2, top],
                     [cap_l / 2, top], [cap_l / 2, full_z], [foot_x, gap]]);
}

difference() {
    union() {
        body();
        for (s = [-1, 1])
            translate([s > 0 ? opn_x0 : -opn_x1, off - opn_t / 2, top - 0.01])
                cube([opn_x1 - opn_x0, opn_t, opn_h + 0.01]);
    }
    // slot cavity, open towards side B
    translate([-cav_l / 2, off - cav_w / 2, -1]) cube([cav_l, cap_w, slot_top + 1]);
    // slit for the cartridge PCB
    translate([-slit_l / 2, off - slit_w / 2, slot_top - 1]) cube([slit_l, slit_w, plate + 2]);
    for (s = [-1, 1]) {
        // key holes for the cartridge nubs
        translate([s > 0 ? nub_x0 : -nub_x1, off - nub_w / 2, top - nub_depth]) cube([nub_x1 - nub_x0, nub_w, nub_depth + 1]);
        // M2.5 screw holes from below
        translate([s * hole_x, off, -1]) cylinder(d = screw_d, h = gap + screw_depth + 1, $fn = 32);
    }
}
