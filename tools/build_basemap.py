#!/usr/bin/env python3
"""Extract a vector basemap from assets/map_clean.jpg by color classification.

Buildings are color-coded by district on the printed map; walkways are gray.
Outputs assets/basemap.json with simplified polygons in map-pixel coordinates
(the same 1870x1640 space used by every other coordinate in data.json).

Run from the repo root:  python3 tools/build_basemap.py
"""
import json, pathlib
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure

root = pathlib.Path(__file__).resolve().parent.parent
im = np.asarray(Image.open(root / 'assets' / 'map_clean.jpg').convert('RGB')).astype(np.int16)
H, W = im.shape[:2]

# reference colors sampled from the print ('dark' catches text/icons/outlines so
# they never fall into the nearest district hue)
REFS = {
    'adirondacks': (45, 91, 45),
    'saratoga':    (204, 18, 54),
    'hudson':      (107, 74, 47),
    'hamptons':    (224, 138, 20),
    'niagara':     (74, 95, 192),
    'kiosk_pink':  (233, 160, 160),
    'kiosk_lav':   (170, 165, 213),
    'walk':        (206, 206, 206),
    'white':       (247, 247, 247),
    'dark':        (40, 40, 40),
}
names = list(REFS)
refs = np.array([REFS[n] for n in names], np.int16)          # (C,3)
dist = np.linalg.norm(im[:, :, None, :] - refs[None, None], axis=3)  # (H,W,C)
cls = np.argmin(dist, axis=2)
mind = np.min(dist, axis=2)
cls[mind > 80] = -1                                           # antialias halos etc.

OPEN3 = np.ones((3, 3))

def polys_from(mask, min_area, tol=1.8, close=0):
    """Labelled components -> hole-filled, simplified outer polygons."""
    out = []
    lab, n = ndimage.label(mask)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < min_area:
            continue
        if close:
            comp = ndimage.binary_closing(comp, np.ones((close, close)))
        comp = ndimage.binary_fill_holes(comp)
        pad = np.pad(comp, 1)                                 # close contours at edges
        for c in measure.find_contours(pad.astype(float), 0.5):
            poly = measure.approximate_polygon(c, tol) - 1.0  # unpad
            if len(poly) < 4:
                continue
            pts = [[round(float(p[1]) * 2) / 2, round(float(p[0]) * 2) / 2] for p in poly]
            out.append(pts)
            break                                             # outer contour only
    return out

def cls_mask(name):
    # opening drops 1-2 px antialias rings and speckle
    return ndimage.binary_opening(cls == names.index(name), OPEN3)

walk_mask = cls_mask('walk')
# absorb icons/text sitting on walkways, then smooth ragged edges
walk_mask = ndimage.binary_closing(ndimage.binary_fill_holes(walk_mask), np.ones((5, 5)))

# White areas NOT connected to the image border are candidate outlined buildings
# (Market Hall / Welcome Center / parking deck) — but enclosed landscaping
# courtyards also read as such, so keep only components whose centroid falls in
# a known building box.
white = cls == names.index('white')
border = np.zeros_like(white)
border[0, :] = border[-1, :] = border[:, 0] = border[:, -1] = True
bg = ndimage.binary_propagation(border & white, mask=white)
halls_mask = white & ~bg
HALL_BOXES = [(460, 730, 900, 1080), (350, 400, 520, 530), (1540, 30, 1840, 200)]  # x0,y0,x1,y1
lab, n = ndimage.label(halls_mask)
keep = np.zeros_like(halls_mask)
for i in range(1, n + 1):
    comp = lab == i
    if comp.sum() < 3000:
        continue
    ys, xs = np.nonzero(comp)
    cx, cy = xs.mean(), ys.mean()
    if any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1 in HALL_BOXES):
        keep |= comp
halls_polys = polys_from(keep, 3000, close=3)

# a building must touch the walkway network (drops the legend swatches)
walk_dil = ndimage.binary_dilation(walk_mask, np.ones((9, 9)))

def district_polys(mask, min_area):
    out = []
    lab, n = ndimage.label(mask)
    for i in range(1, n + 1):
        comp = lab == i
        if comp.sum() < min_area or not (comp & walk_dil).any():
            continue
        out.extend(polys_from(comp, min_area, close=5))
    return out

basemap = {'walk': polys_from(walk_mask, 1200, tol=2.2), 'halls': halls_polys, 'bldg': {}, 'kiosk': []}
for d in ('adirondacks', 'saratoga', 'hudson', 'hamptons', 'niagara'):
    basemap['bldg'][d] = district_polys(cls_mask(d), 900)
for k in ('kiosk_pink', 'kiosk_lav'):
    basemap['kiosk'].extend(district_polys(cls_mask(k), 250))

npts = sum(len(p) for p in basemap['walk']) + sum(len(p) for p in basemap['halls']) + \
       sum(len(p) for polys in basemap['bldg'].values() for p in polys) + \
       sum(len(p) for p in basemap['kiosk'])
counts = {d: len(p) for d, p in basemap['bldg'].items()}
print(f"walk {len(basemap['walk'])} polys, halls {len(basemap['halls'])}, bldg {counts}, kiosks {len(basemap['kiosk'])}, {npts} pts total")

out = root / 'assets' / 'basemap.json'
out.write_text(json.dumps(basemap, separators=(',', ':')))
print('wrote', out, out.stat().st_size, 'bytes')
