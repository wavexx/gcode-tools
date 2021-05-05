#!/usr/bin/env python3
# rotate g-code along Z
import argparse as ap
import sys
import re
import numpy as np

# params
def center_str(string):
    return list(map(float, string.split('x')))

ap = ap.ArgumentParser(description='rotate G-Code along Z')
ap.add_argument('angle', type=float, help='rotation angle (degrees)')
ap.add_argument('center', type=center_str, nargs='?', default="125x100",
                help='XxY rotation center (mm)')
args = ap.parse_args()

angle = args.angle
center = args.center


# setup transform
R = np.array([[ np.cos(angle), np.sin(angle), 0],
              [-np.sin(angle), np.cos(angle), 0],
              [0, 0, 1]])
T = np.array([[1, 0, center[0]],
              [0, 1, center[1]],
              [0, 0, 1]])
A = T @ R @ np.linalg.inv(T)


def transform(x, y):
    v = A @ np.array([x, y, 1])
    return v[0], v[1]


# parsing and substitution
x = None
y = None
for line in sys.stdin:
    line = line.rstrip('\n')

    if re.match(r'G91\b', line):
        print('relative moves are not handled!')
        exit(1)

    if re.match(r'G1\b', line) is None:
        print(line)
        continue

    v = {}
    for p in ['X', 'Y']:
        m = re.search(r' {}(\S+)'.format(p), line)
        if m is not None:
            val = float(m.group(1))
            v[p] = val
            if p == 'X':
                x = val
            elif p == 'Y':
                y = val

    if len(v) == 0:
        print(line)
        continue

    nx, ny = transform(x, y)

    for p in v.keys():
        line = re.sub(r' {}\S+'.format(p), '', line)
    line = 'G1 X{:.3f} Y{:.3f}'.format(nx, ny) + line[2:]
    print(line)
