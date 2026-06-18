import struct
import math
import json
import os
import sys

def mult_matrix(A, B):
    C = [0]*16
    for i in range(4):
        for j in range(4):
            for k in range(4):
                C[i*4+j] += A[i*4+k] * B[k*4+j]
    return C

def invert_matrix_4x4(m):
    inv = [0]*16
    m00, m01, m02, m03 = m[0:4]
    m10, m11, m12, m13 = m[4:8]
    m20, m21, m22, m23 = m[8:12]
    m30, m31, m32, m33 = m[12:16]
    v0 = m22 * m33 - m23 * m32
    v1 = m21 * m33 - m23 * m31
    v2 = m21 * m32 - m22 * m31
    v3 = m20 * m33 - m23 * m30
    v4 = m20 * m32 - m22 * m30
    v5 = m20 * m31 - m21 * m30
    t00 = + (m11 * v0 - m12 * v1 + m13 * v2)
    t10 = - (m10 * v0 - m12 * v3 + m13 * v4)
    t20 = + (m10 * v1 - m11 * v3 + m13 * v5)
    t30 = - (m10 * v2 - m11 * v4 + m12 * v5)
    det = m00 * t00 + m01 * t10 + m02 * t20 + m03 * t30
    if abs(det) < 1e-10: return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    inv_det = 1.0 / det
    inv[0] = t00 * inv_det; inv[4] = t10 * inv_det; inv[8] = t20 * inv_det; inv[12] = t30 * inv_det
    inv[1] = - (m01 * v0 - m02 * v1 + m03 * v2) * inv_det; inv[5] = + (m00 * v0 - m02 * v3 + m03 * v4) * inv_det; inv[9] = - (m00 * v1 - m01 * v3 + m03 * v5) * inv_det; inv[13] = + (m00 * v2 - m01 * v4 + m02 * v5) * inv_det
    v0 = m12 * m33 - m13 * m32; v1 = m11 * m33 - m13 * m31; v2 = m11 * m32 - m12 * m31; v3 = m10 * m33 - m13 * m30; v4 = m10 * m32 - m12 * m30; v5 = m10 * m31 - m11 * m30
    inv[2] = + (m01 * v0 - m02 * v1 + m03 * v2) * inv_det; inv[6] = - (m00 * v0 - m02 * v3 + m03 * v4) * inv_det; inv[10] = + (m00 * v1 - m01 * v3 + m03 * v5) * inv_det; inv[14] = - (m00 * v2 - m01 * v4 + m02 * v5) * inv_det
    v0 = m12 * m23 - m13 * m22; v1 = m11 * m23 - m13 * m21; v2 = m11 * m22 - m12 * m21; v3 = m10 * m23 - m13 * m20; v4 = m10 * m22 - m12 * m20; v5 = m10 * m21 - m11 * m20
    inv[3] = - (m01 * v0 - m02 * v1 + m03 * v2) * inv_det; inv[7] = + (m00 * v0 - m02 * v3 + m03 * v4) * inv_det; inv[11] = - (m00 * v1 - m01 * v3 + m03 * v5) * inv_det; inv[15] = + (m00 * v2 - m01 * v4 + m02 * v5) * inv_det
    return inv

def trs_to_matrix(t, r, s):
    x, y, z, w = r
    m = [0]*16
    m[0] = 1 - 2*y*y - 2*z*z; m[1] = 2*x*y + 2*z*w; m[2] = 2*x*z - 2*y*w; m[3] = 0
    m[4] = 2*x*y - 2*z*w; m[5] = 1 - 2*x*x - 2*z*z; m[6] = 2*y*z + 2*x*w; m[7] = 0
    m[8] = 2*x*z + 2*y*w; m[9] = 2*y*z - 2*x*w; m[10] = 1 - 2*x*x - 2*y*y; m[11] = 0
    m[15] = 1
    for i in range(3): m[0+i] *= s[0]; m[4+i] *= s[1]; m[8+i] *= s[2]
    m[12] = t[0]; m[13] = t[1]; m[14] = t[2]
    return m

class BDAEAnimator:
    def __init__(self, model_file, anim_file=None):
        with open(model_file, 'rb') as f:
            self.model_data = f.read()
        self.anim_data = None
        if anim_file:
            with open(anim_file, 'rb') as f:
                self.anim_data = f.read()

        self.nodes = {}
        self.hierarchy = []
        self.tracks = {}
        self.palette = []
        self.bone_to_node = {}
        self.C = None
        self.C_inv = None

    def get_str(self, data, ptr):
        if ptr == 0 or ptr >= len(data): return ""
        s = b""
        j = ptr
        while j < len(data) and data[j] != 0:
            s += data[j:j+1]
            j += 1
        return s.decode(errors='replace')

    def parse_hierarchy(self, data, addr, visited):
        if addr in visited: return None
        visited.add(addr)
        if addr + 0x60 > len(data): return None

        node_data = data[addr:addr+0x60]
        name = self.get_str(data, struct.unpack('<Q', node_data[0x08:0x10])[0])
        if not name: return None

        bone = self.get_str(data, struct.unpack('<Q', node_data[0x18:0x20])[0])
        t = struct.unpack('<3f', node_data[0x20:0x2C])
        r = struct.unpack('<4f', node_data[0x2C:0x3C])
        s = struct.unpack('<3f', node_data[0x3C:0x48])

        child_count = struct.unpack('<I', node_data[0x4C:0x50])[0]
        child_rel = struct.unpack('<I', node_data[0x50:0x54])[0]

        children = []
        if child_count > 0 and child_rel != 0:
            child_base = addr + 0x48 + child_rel
            for i in range(child_count):
                child_node = self.parse_hierarchy(data, child_base + i * 0x60, visited)
                if child_node: children.append(child_node)

        node = {'name': name, 'bone': bone, 't': list(t), 'r': list(r), 's': list(s), 'children': children}
        self.nodes[name] = node
        return node

    def extract_tracks(self):
        if not self.anim_data: return
        import re
        node_str_addrs = {m.start(): m.group(0).decode() for m in re.finditer(b'[a-zA-Z0-9_-]+-node\x00', self.anim_data)}
        for s_addr, name in node_str_addrs.items():
            for i in range(0, len(self.anim_data) - 8, 4):
                ptr = struct.unpack('<Q', self.anim_data[i:i+8])[0]
                if ptr == s_addr:
                    addr = i - 0x18
                    if addr < 0 or addr + 0x28 > len(self.anim_data): continue
                    data = self.anim_data[addr:addr+0x28]
                    desc_qword = struct.unpack('<Q', data[0x10:0x18])[0]
                    row = desc_qword & 0xFFFFFFFF
                    stride = (desc_qword >> 48) & 0xFFFF
                    if stride in [12, 16] and row < 1000:
                        vk = struct.unpack('<I', data[0x0C:0x10])[0]
                        prop = "rotation" if vk == 4 else ("scale" if row > 0x80 else "translation")
                        node_name = name.strip('\0')
                        if node_name not in self.tracks: self.tracks[node_name] = []
                        self.tracks[node_name].append({'prop': prop, 'row': row, 'stride': stride})

    def sample_track(self, row, stride, frame):
        row_table_base = 0x6604
        entry_addr = row_table_base + row * 8
        rel_offset = struct.unpack('<i', self.anim_data[entry_addr : entry_addr+4])[0]
        samples_base = entry_addr + rel_offset
        sample_addr = samples_base + frame * stride
        if sample_addr + stride > len(self.anim_data): return None
        if stride == 16: return struct.unpack('<4f', self.anim_data[sample_addr:sample_addr+16])
        elif stride == 12: return struct.unpack('<3f', self.anim_data[sample_addr:sample_addr+12])
        return None

    def initialize(self, root_addr, palette_offset, palette_count):
        self.hierarchy = [self.parse_hierarchy(self.model_data, root_addr, set())]
        self.extract_tracks()
        for i in range(palette_count):
            pos = palette_offset + i * 64
            self.palette.append(struct.unpack('<16f', self.model_data[pos:pos+64]))

        def map_bones(node):
            if node['bone'].startswith('Bone'):
                try:
                    b_idx = int(node['bone'][4:]) - 1
                    self.bone_to_node[b_idx] = node['name']
                except: pass
            for c in node['children']: map_bones(c)
        map_bones(self.hierarchy[0])

        # Compute WorldBind and C
        world_bind = {}
        def walk_bind(node, parent_world):
            world = mult_matrix(trs_to_matrix(node['t'], node['r'], node['s']), parent_world)
            world_bind[node['name']] = world
            for c in node['children']: walk_bind(c, world)
        walk_bind(self.hierarchy[0], [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])

        self.C = mult_matrix(self.palette[0], world_bind[self.bone_to_node[0]])
        self.C_inv = invert_matrix_4x4(self.C)

    def compute_animated_world(self, frame):
        animated_world = {}
        def walk_anim(node, parent_world):
            t, r, s = node['t'], node['r'], node['s']
            if node['name'] in self.tracks:
                for track in self.tracks[node['name']]:
                    sampled = self.sample_track(track['row'], track['stride'], frame)
                    if sampled:
                        if track['prop'] == 'translation': t = sampled
                        elif track['prop'] == 'rotation': r = sampled
                        elif track['prop'] == 'scale': s = sampled
            world = mult_matrix(trs_to_matrix(t, r, s), parent_world)
            animated_world[node['name']] = world
            for c in node['children']: walk_anim(c, world)
        walk_anim(self.hierarchy[0], [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])
        return animated_world

    def skin_mesh(self, v_offset, v_count, w_offset, animated_world):
        skinned_verts = []
        for i in range(v_count):
            # Pos lanes: (0, 4, 5)
            v_raw = struct.unpack('<6f', self.model_data[v_offset+i*24 : v_offset+i*24+24])
            pos_model = [v_raw[0], v_raw[4], v_raw[5], 1.0]

            w_data = self.model_data[w_offset+i*20 : w_offset+i*20+20]
            slots = struct.unpack('<4B', w_data[:4])
            weights = struct.unpack('<4f', w_data[4:])

            pos_skeleton = [0.0, 0.0, 0.0, 0.0]
            for j in range(4):
                if weights[j] == 0: continue
                slot = slots[j]
                if slot >= len(self.palette): continue
                node_name = self.bone_to_node[slot]
                wa = animated_world.get(node_name, [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])
                M = mult_matrix(self.palette[slot], wa)
                for col in range(4):
                    for row in range(4): pos_skeleton[col] += pos_model[row] * M[row*4 + col] * weights[j]

            pos_final = [0.0, 0.0, 0.0, 0.0]
            for col in range(4):
                for row in range(4): pos_final[col] += pos_skeleton[row] * self.C_inv[row*4 + col]
            skinned_verts.append(pos_final)
        return skinned_verts

def export_obj(filename, verts, indices):
    with open(filename, 'w') as f:
        for v in verts: f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for tri in indices: f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")

def main():
    # Gorilla
    print("Animating Gorilla...")
    gorilla = BDAEAnimator('dragon_gorillabody_anim.bdae', 'dragon_gorillabody_anim.bdae')
    gorilla.initialize(root_addr=0xD2DB0, palette_offset=0xDC7B8, palette_count=26)
    anim_world = gorilla.compute_animated_world(frame=30)
    v_gorilla = gorilla.skin_mesh(v_offset=0xD7580, v_count=514, w_offset=0xDD260, animated_world=anim_world)

    # Extract Gorilla Indices
    indices = []
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        f.seek(0xDA5B0)
        for _ in range(757):
            indices.append(struct.unpack('<3H', f.read(6)))
    export_obj('gorilla_animated.obj', v_gorilla, indices)

    # Tiki
    print("Animating Tiki...")
    tiki = BDAEAnimator('dragon_tiki_2024.bdae', 'dragon_gorillabody_anim.bdae')
    tiki.initialize(root_addr=0x34A0, palette_offset=0xA400, palette_count=24)
    anim_world_tiki = tiki.compute_animated_world(frame=30)
    v_tiki = tiki.skin_mesh(v_offset=0x69B8, v_count=437, w_offset=0x85D0, animated_world=anim_world_tiki)

    # Extract Tiki Indices
    indices_tiki = []
    with open('dragon_tiki_2024.bdae', 'rb') as f:
        f.seek(0x92A8)
        for _ in range(601):
            indices_tiki.append(struct.unpack('<3H', f.read(6)))
    export_obj('tiki_animated.obj', v_tiki, indices_tiki)

if __name__ == "__main__":
    main()
