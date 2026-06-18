import struct
import json
import math

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

def sample_track(content, row, stride, frame):
    row_table_base = 0x6604
    entry_addr = row_table_base + row * 8
    if entry_addr + 4 > len(content): return None
    rel_offset = struct.unpack('<i', content[entry_addr : entry_addr+4])[0]
    samples_base = entry_addr + rel_offset
    sample_addr = samples_base + frame * stride
    if sample_addr + stride > len(content): return None
    if stride == 16:
        return struct.unpack('<4f', content[sample_addr:sample_addr+16])
    elif stride == 12:
        return struct.unpack('<3f', content[sample_addr:sample_addr+12])
    return None

def main():
    with open('gorilla_hierarchy.json', 'r') as f:
        root_node = json.load(f)
    with open('gorilla_tracks.json', 'r') as f:
        tracks = json.load(f)
    with open('dragon_gorillabody_anim.bdae', 'rb') as f:
        content = f.read()

    # Pre-map tracks by node name
    node_to_tracks = {}
    for t in tracks:
        name = t['node']
        if name not in node_to_tracks: node_to_tracks[name] = []
        node_to_tracks[name].append(t)

    frame = 30 # Midpoint of idle_basic

    def compute_animated_world(node, parent_world, world_matrices):
        # Default TRS
        t, r, s = node['t'], node['r'], node['s']

        # Override with sampled tracks if they exist
        if node['name'] in node_to_tracks:
            for track in node_to_tracks[node['name']]:
                sampled = sample_track(content, track['row'], track['stride'], frame)
                if sampled:
                    if track['prop'] == 'translation': t = sampled
                    elif track['prop'] == 'rotation': r = sampled
                    elif track['prop'] == 'scale': s = sampled

        local = trs_to_matrix(t, r, s)
        world = mult_matrix(local, parent_world)
        world_matrices[node['name']] = world

        for c in node['children']:
            compute_animated_world(c, world, world_matrices)

    animated_world_matrices = {}
    compute_animated_world(root_node, [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1], animated_world_matrices)

    # Check head_ctrl rotation at frame 30
    print(f"head_ctrl-node world pos at frame {frame}: {animated_world_matrices['head_ctrl-node'][12:15]}")

    # Save animated matrices
    with open('gorilla_animated_matrices.json', 'w') as f:
        json.dump(animated_world_matrices, f, indent=2)

main()
