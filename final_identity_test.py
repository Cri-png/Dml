import struct
import json
import math

def mult_matrix(A, B):
    C = [0]*16
    for i in range(4):
        for j in range(4):
            for k in range(4): C[i*4+j] += A[i*4+k] * B[k*4+j]
    return C

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

def main():
    # 1. Load data
    with open('gorilla_hierarchy.json', 'r') as f: root_node = json.load(f)
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        f.seek(0xDC7B8)
        palette = [struct.unpack('<16f', f.read(64)) for _ in range(26)]

    # 2. Compute WorldBind
    world_bind_matrices = {}
    def walk(node, parent_world):
        local = trs_to_matrix(node['t'], node['r'], node['s'])
        world = mult_matrix(local, parent_world)
        if node['bone'].startswith('Bone'):
            try:
                b_idx = int(node['bone'][4:]) - 1
                world_bind_matrices[b_idx] = world
            except: pass
        for c in node['children']: walk(c, world)
    walk(root_node, [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1])

    # C = WorldBind * Palette
    C = mult_matrix(world_bind_matrices[0], palette[0])

    # 3. Load Mesh
    v_count = 514
    with open('gorilla_verts.bin', 'rb') as f: verts = [struct.unpack('<6f', f.read(24)) for _ in range(v_count)]
    with open('gorilla_weights.bin', 'rb') as f:
        weights = []
        for _ in range(v_count):
            data = f.read(20); slots = struct.unpack('<4B', data[:4]); w = struct.unpack('<4f', data[4:])
            weights.append((slots, w))

    # 4. Bind Pose Identity Test
    # v_skel = Σ weight_i * (v_model * Palette_i * WorldBind_i)
    # should yield v_model * C

    identity_errors = []
    for i in range(v_count):
        v_raw = verts[i]
        pos_model = [v_raw[0], v_raw[4], v_raw[5], 1.0]
        slots, wts = weights[i]
        pos_skeleton = [0.0, 0.0, 0.0, 0.0]
        for j in range(4):
            if wts[j] == 0: continue
            slot = slots[j]
            if slot >= 26: continue

            # Use formula: Palette[slot] * WorldBind[slot]
            # Since User confirmed: Palette_i * WorldBind_i = C
            M = mult_matrix(palette[slot], world_bind_matrices[slot])
            v_trans = [0.0, 0.0, 0.0, 0.0]
            for col in range(4):
                for row in range(4): v_trans[col] += pos_model[row] * M[row*4 + col]
            for k in range(4): pos_skeleton[k] += v_trans[k] * wts[j]

        # Predicted Pos in Skeleton Space: v_model * C
        pos_predicted = [0.0, 0.0, 0.0, 0.0]
        for col in range(4):
            for row in range(4): pos_predicted[col] += pos_model[row] * C[row*4 + col]

        error = math.sqrt(sum((pos_skeleton[k] - pos_predicted[k])**2 for k in range(3)))
        identity_errors.append(error)

    avg_error = sum(identity_errors)/len(identity_errors)
    print(f"Bind Pose Identity Test (v_skel vs v_model*C): Avg Error = {avg_error:.6f}")

main()
