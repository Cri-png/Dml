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

def parse_node(content, addr, visited):
    if addr in visited: return None
    visited.add(addr)
    if addr + 0x60 > len(content): return None
    data = content[addr:addr+0x60]

    name_ptr = struct.unpack('<Q', data[0x08:0x10])[0]
    name = get_str(content, name_ptr)
    if not name: return None

    bone_ptr = struct.unpack('<Q', data[0x18:0x20])[0]
    bone = get_str(content, bone_ptr)

    t = struct.unpack('<3f', data[0x20:0x2C])
    r = struct.unpack('<4f', data[0x2C:0x3C])
    s = struct.unpack('<3f', data[0x3C:0x48])

    child_count = struct.unpack('<I', data[0x4C:0x50])[0]
    child_rel = struct.unpack('<I', data[0x50:0x54])[0]

    children = []
    if child_count > 0 and child_rel != 0:
        child_base = addr + 0x48 + child_rel
        for i in range(child_count):
            child_addr = child_base + i * 0x60
            child_node = parse_node(content, child_addr, visited)
            if child_node:
                children.append(child_node)

    return {
        'addr': hex(addr),
        'name': name,
        'bone': bone,
        't': list(t),
        'r': list(r),
        's': list(s),
        'children': children
    }

def main():
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        content = f.read()
    root = parse_node(content, 0xD2DB0, set())
    with open('gorilla_hierarchy.json', 'w') as out:
        json.dump(root, out, indent=2)

if __name__ == "__main__":
    main()
