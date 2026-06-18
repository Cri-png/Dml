import struct
import math
import json

def mult_matrix(A, B):
    C = [0]*16
    for i in range(4):
        for j in range(4):
            for k in range(4):
                C[i*4+j] += A[i*4+k] * B[k*4+j]
    return C

def trs_to_matrix(t, r, s):
    x, y, z, w = r
    m = [0]*16
    m[0] = 1 - 2*y*y - 2*z*z
    m[1] = 2*x*y + 2*z*w
    m[2] = 2*x*z - 2*y*w
    m[3] = 0
    m[4] = 2*x*y - 2*z*w
    m[5] = 1 - 2*x*x - 2*z*z
    m[6] = 2*y*z + 2*x*w
    m[7] = 0
    m[8] = 2*x*z + 2*y*w
    m[9] = 2*y*z - 2*x*w
    m[10] = 1 - 2*x*x - 2*y*y
    m[11] = 0
    m[15] = 1
    for i in range(3):
        m[0+i] *= s[0]
        m[4+i] *= s[1]
        m[8+i] *= s[2]
    m[12] = t[0]
    m[13] = t[1]
    m[14] = t[2]
    return m

def main():
    with open('gorilla_hierarchy.json', 'r') as f:
        root_node = json.load(f)
    world_bind_matrices = {}
    def walk(node, parent_world):
        local = trs_to_matrix(node['t'], node['r'], node['s'])
        world = mult_matrix(local, parent_world)
        if node['bone'].startswith('Bone'):
            try:
                b_idx = int(node['bone'][4:]) - 1
                world_bind_matrices[b_idx] = world
            except: pass
        for c in node['children']:
            walk(c, world)
    walk(root_node, [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        f.seek(0xDC7B8)
        palette = []
        for i in range(26):
            palette.append(struct.unpack('<16f', f.read(64)))

    print("Testing Palette * WorldBind (Row Vector style):")
    for i in range(26):
        cur_C = mult_matrix(palette[i], world_bind_matrices[i])
        print(f"Bone {i+1:2}: Pos [{cur_C[12]:8.3f} {cur_C[13]:8.3f} {cur_C[14]:8.3f}] Diag [{cur_C[0]:.4f} {cur_C[5]:.4f} {cur_C[10]:.4f}]")

main()
