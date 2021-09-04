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
ap.add_argument('-v', '--verbose', action='count', default=0,
                help='increase verbosity')
ap.add_argument('file', nargs='?',
                help='input file to process (default to stdin)')
args = ap.parse_args()

verbosity = args.verbose
fd = sys.stdin if args.file is None else open(args.file)
angle = np.radians(args.rotate)
center = args.center
translate = args.translate
fmt_str = '{{:.{}f}}'.format(args.precision)

def msg(level, arg):
    if level > -verbosity:
        print("{}: {}".format(os.path.basename(sys.argv[0]), arg), file=sys.stderr)

def error(arg):
    msg(2, arg)

def warn(arg):
    msg(1, arg)

def info(arg):
    msg(0, arg)

if angle == 0 and translate == [0, 0]:
    warn('performing no-op transform')


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
A = mT @ rT @ R @ np.linalg.inv(rT)


def transform(x, y):
    v = A @ np.array([x, y, 1])
    return v[0:2]

def format(x):
    return fmt_str.format(x)


# parsing and substitution
pos = [0, 0]
bounds_c = [None, None, None, None]
bounds_t = [None, None, None, None]
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
            pos[i] = val
    if not seen:
        print(line)
        continue

    pos_t = transform(*pos)
    nx, ny = map(format, pos_t)
    line = re.sub(r' [XY]\S+', '', line)
    line = 'G1 X{} Y{}'.format(nx, ny) + line[2:]
    print(line)

    if verbosity > 0:
        if bounds_c[0] is None:
            bounds_c[0] = bounds_c[1] = pos[0]
            bounds_c[2] = bounds_c[3] = pos[1]
            bounds_t[0] = bounds_t[1] = pos_t[0]
            bounds_t[2] = bounds_t[3] = pos_t[1]
        else:
            bounds_c[0] = min(bounds_c[0], pos[0])
            bounds_c[1] = max(bounds_c[1], pos[0])
            bounds_c[2] = min(bounds_c[2], pos[1])
            bounds_c[3] = max(bounds_c[3], pos[1])
            bounds_t[0] = min(bounds_t[0], pos_t[0])
            bounds_t[1] = max(bounds_t[1], pos_t[0])
            bounds_t[2] = min(bounds_t[2], pos_t[1])
            bounds_t[3] = max(bounds_t[3], pos_t[1])

if verbosity > 0:
    fmt_block = ' {{}}{{:-{}.{}f}}'.format(args.precision + 5, args.precision)
    print(('initial boundaries:' + fmt_block * 4).format(
        '-X', bounds_c[0], '+X', bounds_c[1], '-Y', bounds_c[2], '+Y', bounds_c[3]), file=sys.stderr)
    print(('transf. boundaries:' + fmt_block * 4).format(
        '-X', bounds_t[0], '+X', bounds_t[1], '-Y', bounds_t[2], '+Y', bounds_t[3]), file=sys.stderr)
