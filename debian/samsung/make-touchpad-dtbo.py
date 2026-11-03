#!/usr/bin/env python3
"""Validate/fix every T870 touchpad overlay and sign the Android DTBO table."""
import argparse
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile

PART_SIZE = 10485760
PROPERTY = re.compile(r"(touchpad,invert\s*=\s*)<([^>]+)>(\s*;)")


def align(value, page):
    return (value + page - 1) // page * page


def patch_dts(dts):
    matches = list(PROPERTY.finditer(dts))
    if not matches:
        raise ValueError("overlay has no touchpad,invert property")
    changed = 0

    def replace(match):
        nonlocal changed
        values = [int(cell, 0) for cell in match[2].split()]
        if values == [0, 0, 0]:
            return match[0]
        if values != [0, 1, 1]:
            raise ValueError(f"unexpected touchpad,invert: {values}")
        changed += 1
        return f"{match[1]}<0x00 0x00 0x00>{match[3]}"

    return PROPERTY.sub(replace, dts), changed


def patch_table(data, work):
    if len(data) < 32:
        raise ValueError("truncated DTBO header")
    magic, total, hsz, esz, count, eoff, page, version = struct.unpack_from(">8I", data)
    if (magic != 0xD7B7AB1E or hsz != 32 or esz < 32 or not count
            or eoff < hsz or page not in (2048, 4096) or version != 0
            or eoff + count * esz > total or total > len(data)):
        raise ValueError("invalid Android DTBO table")
    entries, blobs, changed, ready = [], [], 0, 0
    for index in range(count):
        entry = data[eoff + index * esz:eoff + (index + 1) * esz]
        size, offset = struct.unpack_from(">2I", entry)
        if offset < eoff + count * esz or offset + size > total or size < 40:
            raise ValueError(f"overlay {index} exceeds DTBO table bounds")
        blob = data[offset:offset + size]
        source = work / f"{index}.dtb"
        source.write_bytes(blob)
        result = subprocess.run(["dtc", "-I", "dtb", "-O", "dts", str(source)],
                                check=True, capture_output=True, text=True)
        dts, edits = patch_dts(result.stdout)
        if edits:
            output = work / f"{index}-fixed.dtb"
            subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-o", str(output)],
                           input=dts, check=True, capture_output=True, text=True)
            blob = output.read_bytes()
            changed += 1
        else:
            ready += 1
        entries.append(entry[8:])
        blobs.append(blob)
    offset = align(eoff + count * esz, page)
    table, body = bytearray(), bytearray()
    for metadata, blob in zip(entries, blobs):
        table += struct.pack(">2I", len(blob), offset) + metadata
        padded = align(len(blob), page)
        body += blob + b"\x00" * (padded - len(blob))
        offset += padded
    header = struct.pack(">8I", magic, offset, hsz, esz, count, eoff, page, version)
    output = header + data[hsz:eoff] + table
    output += b"\x00" * (align(len(output), page) - len(output)) + body
    return output, changed, ready


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stock", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--key", type=Path,
                        default=Path(__file__).resolve().parents[1] / "testkey_rsa4096.pem")
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dtbo-", dir=args.out.parent) as directory:
        work = Path(directory)
        data, changed, ready = patch_table(args.stock.read_bytes(), work)
        image = work / "dtbo.img"
        image.write_bytes(data)
        subprocess.run(["avbtool", "add_hash_footer", "--image", str(image),
                        "--partition_name", "dtbo", "--partition_size", str(PART_SIZE),
                        "--algorithm", "SHA256_RSA4096", "--key", str(args.key),
                        "--rollback_index", "0"], check=True)
        subprocess.run(["avbtool", "verify_image", "--image", str(image),
                        "--key", str(args.key)], check=True)
        os.replace(image, args.out)
    print(f"OK: {args.out}: {changed} overlays patched, {ready} already correct")


if __name__ == "__main__":
    main()
