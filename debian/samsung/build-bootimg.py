#!/usr/bin/env python3
"""
build-bootimg.py — turn a raw Droidian/CI boot.img into a Samsung-ABL-acceptable,
bootable boot.img for the Galaxy Tab S7 Wi-Fi (SM-T870 / gts7lwifi).

Usage:
  python3 build-bootimg.py <raw_boot.img> <output.img> [--rescue]

  --rescue  use console=null to drop into RNDIS+telnet rescue at 192.168.2.15:23

Requires: avbtool in PATH, testkey_rsa4096.pem next to this script (or via --key).
"""
import struct, sys, subprocess, os, argparse, shutil

# --- Samsung Tab S7 Wi-Fi constants ---
BOOT_PARTITION_SIZE     = 71303168     # /dev/block/by-name/boot (confirmed from BoardConfig)
RECOVERY_PARTITION_SIZE = 86888448     # /dev/block/by-name/recovery
ROLLBACK_INDEX          = 1900000000
RAMDISK_ADDR = 0x02000000
TAGS_ADDR    = 0x01e00000
OS_VERSION   = 0x1e000198  # Android 15 + 2024-12 SPL encoding (same as T970)
BOARD_NAME   = b"SRPTC16A002"  # 16 bytes, same SM8250 platform

CMDLINE_REAL = (
    "console=tty0 androidboot.hardware=qcom androidboot.memcg=1 "
    "video=vfb:640x400,bpp=32,memsize=3072000 "
    "msm_rtb.filter=0x237 service_locator.enable=1 swiotlb=2048 "
    "firmware_class.path=/vendor/firmware_mnt androidboot.usbcontroller=a600000.dwc3 "
    "buildvariant=eng androidboot.selinux=permissive"
)
CMDLINE_RESCUE = CMDLINE_REAL.replace("console=tty0", "console=null")


def patch_header(path, cmdline):
    with open(path, "rb") as f:
        d = bytearray(f.read())
    if len(d) < 1660 or d[:8] != b"ANDROID!":
        raise ValueError("not an Android boot.img v2")
    if struct.unpack_from("<I", d, 40)[0] != 2:
        raise ValueError("only Android boot header v2 is supported")
    page_size = struct.unpack_from("<I", d, 36)[0]
    kernel_size = struct.unpack_from("<I", d, 8)[0]
    if page_size != 4096 or kernel_size == 0 or page_size + kernel_size > len(d):
        raise ValueError("invalid Samsung boot image layout")
    if not d[page_size:page_size + kernel_size].endswith(b"SEANDROIDENFORCE"):
        raise ValueError("kernel is missing the Samsung SEANDROIDENFORCE trailer")
    struct.pack_into("<I", d, 20, RAMDISK_ADDR)
    struct.pack_into("<I", d, 32, TAGS_ADDR)
    struct.pack_into("<I", d, 44, OS_VERSION)
    d[48:64] = BOARD_NAME.ljust(16, b"\x00")
    cb = cmdline.encode()
    assert len(cb) < 512, "cmdline too long for v2 header"
    for i in range(64, 64 + 512):
        d[i] = 0
    # v2 has another 1024 command-line bytes after the image ID.
    d[608:1632] = b"\x00" * 1024
    d[64:64 + len(cb)] = cb
    with open(path, "wb") as f:
        f.write(bytes(d))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("out")
    ap.add_argument("--rescue", action="store_true")
    ap.add_argument("--partition", default="boot", choices=["boot", "recovery"])
    ap.add_argument("--key", default=os.path.join(os.path.dirname(__file__), "..", "testkey_rsa4096.pem"))
    a = ap.parse_args()
    psize = BOOT_PARTITION_SIZE if a.partition == "boot" else RECOVERY_PARTITION_SIZE
    cmdline = CMDLINE_RESCUE if a.rescue else CMDLINE_REAL

    shutil.copy(a.raw, a.out)
    patch_header(a.out, cmdline)
    subprocess.run(["avbtool", "erase_footer", "--image", a.out],
                   stderr=subprocess.DEVNULL)
    subprocess.run(["avbtool", "add_hash_footer",
                    "--image", a.out,
                    "--partition_size", str(psize),
                    "--partition_name", a.partition,
                    "--algorithm", "SHA256_RSA4096",
                    "--key", a.key,
                    "--rollback_index", str(ROLLBACK_INDEX)], check=True)
    print(f"OK: {a.out}  partition={a.partition} size={psize} "
          f"cmdline={'RESCUE/console=null' if a.rescue else 'REAL/console=tty0'}")


if __name__ == "__main__":
    main()
