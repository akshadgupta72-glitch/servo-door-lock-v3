# SPDX-License-Identifier: MIT
"""Check the released binary STLs without requiring FreeCAD."""
import hashlib
import json
import math
from pathlib import Path
import struct
from collections import Counter

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "Print_servo_arm_FIT_CHECK.stl": (10, 45, 4),
    "Print_clamp_yoke_FIT_CHECK.stl": (37, 53, 23.5),
    "Print_servo_mount_FIT_CHECK.stl": (39, 20, 16),
}


def check(path, expected):
    raw = path.read_bytes()
    assert len(raw) >= 84, f"{path.name}: truncated header"
    count = struct.unpack_from("<I", raw, 80)[0]
    assert count > 0 and len(raw) == 84 + 50 * count, "Invalid binary STL length"
    vertices, edges, directions = [], Counter(), Counter()
    volume = 0.0
    for index in range(count):
        record = struct.unpack_from("<12fH", raw, 84 + 50 * index)
        assert all(math.isfinite(v) for v in record[:12]), "Nonfinite value"
        a, b, c = [tuple(record[i:i + 3]) for i in (3, 6, 9)]
        ab = tuple(b[i] - a[i] for i in range(3))
        ac = tuple(c[i] - a[i] for i in range(3))
        cross = (ab[1]*ac[2] - ab[2]*ac[1],
                 ab[2]*ac[0] - ab[0]*ac[2],
                 ab[0]*ac[1] - ab[1]*ac[0])
        assert sum(v*v for v in cross) > 1e-16, "Degenerate triangle"
        volume += sum(a[i] * cross[i] for i in range(3)) / 6.0
        vertices.extend((a, b, c))
        for u, v in ((a, b), (b, c), (c, a)):
            key = tuple(sorted((u, v)))
            edges[key] += 1
            directions[key] += 1 if (u, v) == key else -1
    assert all(n == 2 for n in edges.values()), "Open or non-manifold edge"
    assert all(n == 0 for n in directions.values()), "Inconsistent winding"
    assert volume > 0, "Nonpositive signed volume"
    lower = [min(v[i] for v in vertices) for i in range(3)]
    upper = [max(v[i] for v in vertices) for i in range(3)]
    size = [upper[i] - lower[i] for i in range(3)]
    assert all(abs(v) < 0.1 for v in lower), f"Unexpected minimum bounds: {lower}"
    assert all(abs(a - b) < 0.1 for a, b in zip(size, expected)), size
    return {"file": path.name, "triangles": count,
            "dimensions_mm": [round(v, 3) for v in size],
            "volume_mm3": round(volume, 3),
            "sha256": hashlib.sha256(raw).hexdigest()}


if __name__ == "__main__":
    print(json.dumps([check(ROOT / name, bounds)
                      for name, bounds in EXPECTED.items()], indent=2))
