import sys
import struct
import pathlib

DEBUG = False
DEFAULT_CHARSET = "cp932"
replace_special_symbols = lambda b: b.decode(DEFAULT_CHARSET).replace("\uff1d", "==").replace("\u2260", "!=").encode(DEFAULT_CHARSET)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: patcher.py script.rld|config.rnf [i18n]")
        exit(1)
    p = pathlib.Path(sys.argv[1])
    with open(p, "rb") as f:
        content = bytearray(f.read())
        if content[:4] != b"RLD\0"[::-1]:
            plaintext = True
        else:
            plaintext = False

    specific_file = p.stem.startswith("backlog.") if plaintext else p.stem == "def"
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
    charset = str(charset).encode(DEFAULT_CHARSET)

    if plaintext:
        content = replace_special_symbols(content).decode(DEFAULT_CHARSET)
        processed = ""
        for i in content.splitlines():
            if specific_file and i.find("fontName") != -1:
                i = f"{i.split('=')[0]}={font}\r\n{i.rsplit('.', 1)[0]}.fontCharset={i18n}"
            processed += i + "\r\n"
        content = processed.encode(DEFAULT_CHARSET)

    else:
        font = font.encode(DEFAULT_CHARSET)
        offset, count = struct.unpack("<II", content[8:16])
        offset += 4
        strings = []
        for _ in range(count):
            op, int_argc, str_argc = struct.unpack("<HBB", content[offset:offset + 4])
            str_argc &= 0xf
            if DEBUG:
                print(hex(offset), hex(op), int_argc, str_argc)
            offset += 4 * (int_argc + 1)
            for _ in range(str_argc):
                start = offset
                end = content.find(b"\0", offset)
                offset = end + 1
                b = content[start:end]
                if DEBUG:
                    print(b.decode(DEFAULT_CHARSET))
                content[start:end] = replace_special_symbols(b)
                split = [bytes(i) for i in b.split(b",")]
                if not specific_file or b.find(b"16777215") == -1:
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
