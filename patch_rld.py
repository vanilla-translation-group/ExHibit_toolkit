import sys
import struct
import pathlib

DEBUG = False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: patch_rld.py script.rld [i18n]")
        exit(1)
    p = pathlib.Path(sys.argv[1])
    with open(p, "rb") as f:
        content = bytearray(f.read())
        if content[:4] != b"RLD\0"[::-1]:
            print("invalid RLD script")
            exit(1)

    is_not_def = p.stem != "def"
    i18n = sys.argv[2].lower() if len(sys.argv) > 2 else "cns"
    match i18n:
        case "en":
            font = "Arial"
        case "cns":
            font = "Microsoft YaHei"
        case "cnt":
            font = "Microsoft JhengHei"
        case _:
            print("unknown i18n option")
            exit(1)
    charset = 0
    match i18n[:2]:
        case "cn":
            charset = 134
    font = font.encode()
    charset = str(charset).encode()

    offset, count = struct.unpack("<II", content[8:16])
    offset += 4
    strings = []

    for _ in range(count):
        op, int_argc, str_argc = struct.unpack("<HBB", content[offset:offset + 4])
        str_argc &= 0xf
        if DEBUG:
            print(hex(op), int_argc, str_argc)
        offset += 4
        for _ in range(int_argc):
            if DEBUG:
                print(struct.unpack("<I", content[offset:offset + 4])[0], end=" ")
            offset += 4
        if DEBUG and int_argc > 0:
            print()
        for _ in range(str_argc):
            start = offset
            end = content.find(b"\0", offset)
            offset = end + 1
            b = content[start:end]
            if DEBUG:
                print(b.decode("cp932"))
            content[start:end] = b.replace(b"\x81\x81", b"==").replace(b"\x81\x82", b"!=")
            split = [bytes(i) for i in b.split(b",")]
            if is_not_def or b.find(b"16777215") == -1:
                continue
            if b.startswith(b"0,") or b.startswith(b"res\\"):
                split[-4] = charset
                split[-9] = font
            if not b.startswith(b"res\\"):
                split[-13] = charset
                split[-18] = font
            split = b",".join(split)
            content[start:end] = split
            offset += len(split) - len(b)
        if DEBUG:
            print()

    with open(p.with_stem("_" + p.stem), "wb") as f:
        f.write(content)
