#!/usr/bin/env python3
"""Dump an Atari 2600 cartridge via AtariCartReader.

usage: dump.py <port> <scheme> <file> [kb]
       dump.py <port> list
       dump.py <port> listen <prefix>   saves every dump started with the read button as <prefix>-<n>.bin
"""
import sys
import serial


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    port = serial.Serial(sys.argv[1], 115200, timeout=10)
    port.readline()  # READY (board resets on connect)
    if sys.argv[2].lower() == "list":
        port.write(b"L\n")
        for line in iter(port.readline, b"END\r\n"):
            print(line.decode().strip())
        return
    if sys.argv[2].lower() == "listen":
        listen(port, sys.argv[3])
        return
    scheme, filename = sys.argv[2], sys.argv[3]
    kb = sys.argv[4] if len(sys.argv) > 4 else ""
    port.write(f"D {scheme} {kb}\n".encode())
    answer = port.readline().decode().strip()
    if not answer.startswith("OK"):
        sys.exit(answer)
    save(port, answer, filename)


def save(port, answer, filename):
    size = int(answer.split()[1])
    data = port.read(size)
    if len(data) != size:
        sys.exit(f"only {len(data)} of {size} bytes received")
    with open(filename, "wb") as f:
        f.write(data)
    print(f"{filename}: {size} bytes")


def listen(port, prefix):
    port.timeout = None
    n = 1
    print("waiting for the read button, Ctrl+C to stop")
    while True:
        answer = port.readline().decode(errors="replace").strip()
        if answer.startswith("OK"):
            save(port, answer, f"{prefix}-{n}.bin")
            n += 1
        elif answer:
            print(answer)


if __name__ == "__main__":
    main()
