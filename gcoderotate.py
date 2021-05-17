#!/usr/bin/env python3
# rotate g-code along Z
import argparse as ap
import os, sys
import re
import numpy as np

# params
def coord_pair(string):
    return list(map(float, string.split('x')))

ap = ap.ArgumentParser(description='rotate G-Code along Z')
ap.add_argument('-r', '--rotate', type=float, default=0,
                help='Z rotation angle (degrees)')
ap.add_argument('-c', '--center', type=coord_pair, default="125x100",
                help='XxY rotation center (mm, default: 125x100)')
ap.add_argument('-t', '--translate', type=coord_pair, default="0x0",
                help='XxY translation (mm, default: 0x0)')
ap.add_argument('--precision', type=int, default=3,
                help='output coordinate decimal precision (default: 3)')
ap.add_argument('file', nargs='?',
                help='input file to process (default to stdin)')
args = ap.parse_args()

fd = sys.stdin if args.file is None else open(args.file)
angle = np.radians(args.rotate)
center = args.center
translate = args.translate
fmt_str = '{{:.{}f}}'.format(args.precision)

def error(msg):
    print("{}: {}".format(os.path.basename(sys.argv[0]), msg), file=sys.stderr)

if angle == 0 and translate == [0, 0]:
    error('performing no-op transform')


# setup transform
R = np.array([[ np.cos(angle), np.sin(angle), 0],
              [-np.sin(angle), np.cos(angle), 0],
              [0, 0, 1]])
rT = np.array([[1, 0, center[0]],
               [0, 1, center[1]],
               [0, 0, 1]])
mT = np.array([[1, 0, translate[0]],
               [0, 1, translate[1]],
               [0, 0, 1]])
A = rT @ R @ np.linalg.inv(rT) @ mT


def transform(x, y):
    v = A @ np.array([x, y, 1])
    return v[0:2]


# parsing and substitution
cursor = [None, None]
for line in fd:
    line = line.rstrip('\n')

    if re.match(r'G91\b', line):
        error('relative moves are not handled!')
        exit(1)

    if re.match(r'G1\b', line) is None:
        print(line)
        continue

    seen = False
    for i, p in enumerate(['X', 'Y']):
        m = re.search(r' {}(\S+)'.format(p), line)
        if m is not None:
            val = float(m.group(1))
            seen = True
            cursor[i] = val
    if not seen:
        print(line)
        continue

    nx, ny = map(lambda x: fmt_str.format(x), transform(*cursor))
    line = re.sub(r' [XY]\S+', '', line)
    line = 'G1 X{} Y{}'.format(nx, ny) + line[2:]
    print(line)
