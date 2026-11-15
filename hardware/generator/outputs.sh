#!/bin/sh
# Exports gerbers (ZIP), schematic PDF and a board PNG for one variant: ./outputs.sh uno|mega|nano
set -e
cd "$(dirname "$0")"
B=$1
H=$(cd .. && pwd)/$B
N=atari2600-cart-reader-$B
T=${TMPDIR:-/tmp}/taxcart-out-$B
rm -rf "${T:?}" && mkdir -p $T/gerber
kicad-cli pcb export gerbers -o $T/gerber/ -l F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts $H/$N.kicad_pcb >/dev/null
kicad-cli pcb export drill -o $T/gerber/ $H/$N.kicad_pcb >/dev/null
rm -f $H/$N-gerber.zip
(cd $T/gerber && python3 -c "import zipfile,os,sys;z=zipfile.ZipFile(sys.argv[1],'w',zipfile.ZIP_DEFLATED);[z.write(f) for f in sorted(os.listdir('.'))]" $H/$N-gerber.zip)
kicad-cli sch export pdf -o $H/$N-schaltplan.pdf $H/$N.kicad_sch >/dev/null
kicad-cli pcb export svg -o $T/board.svg -l F.Cu,B.Cu,F.Silkscreen,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet $H/$N.kicad_pcb >/dev/null
python3 -c "import cairosvg,sys;cairosvg.svg2png(url=sys.argv[1],write_to=sys.argv[2],output_width=1400,background_color='white')" $T/board.svg $H/$N-platine.png
ls -la $H | grep -E "zip|pdf|png"
