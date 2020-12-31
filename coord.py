#!/usr/bin/env python3

import sys


UL = [34.746399, 87.518497]
UR = [34.746321, 87.516236]
LL = [34.741893, 87.518503]
LR = [34.741841, 87.516373]

def areaOfTriangle(p1, p2, p3):
    p1 = [abs(c) for c in p1]
    p2 = [abs(c) for c in p2]
    p3 = [abs(c) for c in p3]
    return 0.5 * ((p1[0] * (p2[1] - p3[1])) + (p2[0] * (p3[1] - p1[1])) + (p3[0] * (p1[1] - p2[1])))

if len(sys.argv) < 3:
    print('usage:  coord.py x y')
    exit(1)

p = [float(sys.argv[1].replace(',', '')), abs(float(sys.argv[2]))]

a1 = areaOfTriangle(p, UL, UR)
a2 = areaOfTriangle(p, UL, LL)
a3 = areaOfTriangle(p, LL, LR)
a4 = areaOfTriangle(p, LR, UR)

sumOfRectTriangles = areaOfTriangle(UL, LL, LR) + areaOfTriangle(UL, LR, UR)

#print(f'a1: {a1}')
#print(f'a2: {a2}')
#print(f'a3: {a3}')
#print(f'a4: {a4}')
sumOfPointTriangles = a1 + a2 + a3 + a4
print(f'Sum of point triangles: {sumOfPointTriangles}')
print(f'Sum of rect  triangles: {sumOfRectTriangles}')

print('Point is ' + ('inside' if sumOfRectTriangles >= sumOfPointTriangles else 'outside'))
