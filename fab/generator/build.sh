#!/bin/sh
# Erzeugt Schaltplan, Platine (Freerouting) und DRC fuer eine Variante: ./build.sh uno|mega
set -e
export KICAD7_FOOTPRINT_DIR=${KICAD7_FOOTPRINT_DIR:-/usr/share/kicad/footprints}
export KICAD7_SYMBOL_DIR=${KICAD7_SYMBOL_DIR:-/usr/share/kicad/symbols}
cd "$(dirname "$0")"
B=$1
H=$(cd .. && pwd)/$B
T=${TMPDIR:-/tmp}/taxcart-$B
mkdir -p $H $T
N=atari2600-cart-reader-$B
cat > $H/fp-lib-table <<'T'
(fp_lib_table
  (version 7)
  (lib (name "atari")(type "KiCad")(uri "${KIPRJMOD}/../lib/atari.pretty")(options "")(descr "Atari 2600 Cartridge-Slot"))
  (lib (name "arduino-library")(type "KiCad")(uri "${KIPRJMOD}/../lib/arduino-library.pretty")(options "")(descr "Alarm-Siren arduino-kicad-library, CC BY-SA 4.0"))
)
T
cat > $H/sym-lib-table <<'T'
(sym_lib_table
  (version 7)
  (lib (name "arduino-library")(type "KiCad")(uri "${KIPRJMOD}/../lib/arduino-library.kicad_sym")(options "")(descr "Alarm-Siren arduino-kicad-library, CC BY-SA 4.0"))
)
T
python3 mksch.py $B $H/$N.kicad_sch
kicad-cli sch export netlist -o $T/net.net $H/$N.kicad_sch >/dev/null
python3 verify.py $B $T/net.net
rm -f $T/route.kicad_pro $H/$N.kicad_pro
python3 mkpcb.py $B $T/route.kicad_pcb
python3 -c "import pcbnew;b=pcbnew.LoadBoard('$T/route.kicad_pcb');pcbnew.ExportSpecctraDSN(b,'$T/route.dsn')"
rm -f $T/route.ses
(cd $T && timeout 1200 xvfb-run -a java -jar ${FREEROUTING:-/opt/tools/freerouting.jar} -de $T/route.dsn -do $T/route.ses -mp ${PASSES:-60} 2>&1 | grep -E "completed|unrouted|incomplete" | tail -3)
python3 finish.py $B $T/route.kicad_pcb $T/route.ses $H/$N.kicad_pcb
python3 labels.py $B $H/$N.kicad_pcb
python3 -c "import pcbnew;b=pcbnew.LoadBoard('$H/$N.kicad_pcb');pcbnew.WriteDRCReport(b,'$H/drc-bericht.txt',pcbnew.EDA_UNITS_MILLIMETRES,True)"
grep -E "^\[" $H/drc-bericht.txt | sed 's/\]:.*/]/' | sort | uniq -c || true
grep -E "unconnected pads" $H/drc-bericht.txt
python3 plate.py $H/$N.kicad_pcb
