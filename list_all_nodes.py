import struct
import json

def get_str(content, ptr):
    if ptr == 0 or ptr >= len(content): return ""
    s = b""
    j = ptr
    while j < len(content) and content[j] != 0:
        s += content[j:j+1]
        j += 1
    return s.decode(errors='replace')

def main():
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        content = f.read()

    import re
    node_str_addrs = [m.start() for m in re.finditer(b'[a-zA-Z0-9_-]+-node\x00', content)]
    node_addrs = set()
    for s_addr in node_str_addrs:
        for i in range(0, len(content) - 8, 4):
            ptr = struct.unpack('<Q', content[i:i+8])[0]
            if ptr == s_addr:
                 node_addrs.add(i - 8)

    # Just list all unique node records and their names
    for addr in sorted(node_addrs):
        data = content[addr:addr+0x60]
        name_ptr = struct.unpack('<Q', data[0x08:0x10])[0]
        name = get_str(content, name_ptr)
        print(f"Record 0x{addr:X}: {name}")

if __name__ == "__main__":
    main()
