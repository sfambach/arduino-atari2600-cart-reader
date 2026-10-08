# Atari 2600 Cartridge Reader

Arduino firmware for dumping Atari 2600 cartridges, including bankswitched games.

Project page: https://www.fambach.net/ (Retro Projekt – Atari 2600 ROM einlesen)

## Boards

| Board | Address bus | Data bus |
|---|---|---|
| Arduino Mega 2560 | A0-A7 = PA0-PA7, A8-A12 = PC0-PC4 | D0-D7 = PL0-PL7 |
| Arduino Uno | MCP23017 (I2C 0x20): GPA0-7 = A0-A7, GPB0-4 = A8-A12 | D0-D7 = D2-D9 |

Cartridge slot: pin 23 = +5 V, pins 12 and 24 = GND.

Shields (THT, KiCad) for both boards: [`hardware/`](hardware/).

## Bankswitching

| Scheme | Size | Status |
|---|---|---|
| 2K, 4K | 2/4 KB | |
| F8, F6, F4 (+SC) | 8/16/32 KB | |
| E0 (Parker Bros.) | 8 KB | |
| E7 (M-Network) | 16 KB | |
| FA (CBS RAM+) | 12 KB | |
| FE (Activision) | 8 KB | experimental |
| 3F (Tigervision) | 8 KB+ (`D 3F <kb>`) | experimental |

Untested on hardware so far.

## Usage

Serial 115200 baud: `L` lists schemes, `D <scheme> [kb]` dumps, `P <hexaddr>` reads one byte.

```
pip install pyserial
python3 tools/dump.py /dev/ttyACM0 F8 game.bin
```

Test the dump with the emulator [Stella](https://stella-emu.github.io/).

## Credits

- [retrocartdumper](https://github.com/SvOlli/retrocartdumper) by Sven Oliver Moll (GPLv3)
- [Cart Reader](https://github.com/sanni/cartreader) by sanni (GPLv3)
- [vcsreaderfw](https://github.com/keoni29/vcsreaderfw) by Koen van Vliet (MIT)

## License

GPLv3
