import sys
import struct

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: crypt_rld.py in.rld key.bin out.rld")
        exit(1)
    with open(sys.argv[1], "rb") as f:
        content = bytearray(f.read())
        header = content[:0x10]
        content = content[0x10:]
    with open(sys.argv[2], "rb") as f:
        key = struct.unpack("<I", f.read(4))[0]
        key_list = [struct.unpack("<I", f.read(4))[0] ^ key for _ in range(0x100)]
    for i in range(min(len(content) >> 2, 0x3ff0)):
        key = key_list[i & 0xff]
        i *= 4
        content[i:i + 4] = struct.pack("<I", struct.unpack("<I", content[i:i + 4])[0] ^ key)
    with open(sys.argv[3], "wb") as f:
        f.write(header)
        f.write(content)
