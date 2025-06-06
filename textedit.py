import sys
import pathlib
import struct
import csv

DEBUG = False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("USAGE: textedit.py script.rld encoding dialog.txt")
        print("Extract text if dialog.txt does not exist; Reinsert text if it exists")
        exit(1)
    with open(sys.argv[1], "rb") as f:
        content = f.read()
        if content[:4] != b"RLD\0"[::-1]:
            print("invalid RLD script")
            exit(1)
    table = {}
    try:
        with open("defChara.txt") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    table[int(row[0])] = row[3]
    except:
        pass
    offset, count = struct.unpack("<II", content[8:16])
    offset += 4
    strings = []

    for _ in range(count):
        op, int_argc, str_argc = struct.unpack("<HBB", content[offset:offset + 4])
        str_argc &= 0xf
        int_argv = []
        str_argv = []
        offset += 4
        for _ in range(int_argc):
            int_argv.append(struct.unpack("<I", content[offset:offset + 4])[0])
            offset += 4
        for i in range(str_argc):
            str_argv.append((offset, content.find(b"\0", offset), op, i, 0))
            offset = str_argv[-1][1] + 1
        if op == 0x1c: # dialog
            dialog = list(str_argv[1])
            dialog[-1] = int_argv[0]
            strings.append(tuple(dialog))
        elif op == 0x15: # selection
            strings.extend(str_argv)
        elif op == 0x30: # name definition
            strings.append(str_argv[0])
    strings = filter(lambda x: x[0] != x[1], strings)

    if pathlib.Path(sys.argv[3]).exists():
        with open(sys.argv[3]) as f:
            texts = [i.split("\n")[-1].replace("\\n", "\n") for i in f.read().split("\n\n") if i.strip()]
        p = pathlib.Path(sys.argv[1])
        with open(p.with_stem("_" + p.stem), "wb") as f:
            start = 0
            for text, data in zip(texts, strings):
                f.write(content[start:data[0]])
                f.write(text.encode(sys.argv[2]))
                start = data[1]
            f.write(content[start:])
    else:
        with open(sys.argv[3], "w") as f:
            for start, end, op, i, chara in strings:
                string = content[start:end].decode(sys.argv[2])
                if DEBUG:
                    print(hex(start), hex(end), hex(op), i, chara)
                    print(string)
                if chara >= 3:
                    name = table[chara] if chara in table else f"[{chara}]"
                    f.write(name + "\n")
                f.write(string.replace("\n", "\\n") + "\n\n")
