# Woodbury Common Navigator

A single-file interactive wayfinding app for **Woodbury Common Premium Outlets**, built
from the official Map & Directory. Open `index.html` on your phone — no build step, no
server, no dependencies.

## Features

- **Vector map** — buildings, walkways, and kiosks are real polygons (extracted
  from the official map art), rendered natively in light and dark themes with all
  six color-coded districts (Adirondacks, Saratoga, Hudson Valley, Hamptons,
  Niagara, Market Hall) and suite numbers at high zoom. Pan, pinch-zoom, rotate;
  tap a district chip to highlight its area and list its stores.
- **Live position** — uses the browser Geolocation API to show where you are inside the
  mall (the outlet is open-air, so GPS works well), with an accuracy ring.
  Long-press the map while GPS is on to fine-tune calibration; the offset is remembered.
- **Compass orientation** — a heading cone on your position marker, plus a
  heading-up mode that rotates the map around your own dot with the direction
  you're facing — smoothed, magnetic-declination corrected, and rendered through
  a single animation loop (tap the compass button; iOS asks for motion permission).
- **Store search & navigation** — search all 240 stores by name, suite, or category.
  Pick one and tap **Navigate** for the quickest walking route along the mall's
  walkway network (Dijkstra over a hand-digitized graph), with live distance and
  ETA that update as you move.
- **Parking & amenities** — route back to any color-coded parking lot or the deck,
  find restrooms, ATMs, the Welcome Center, and Market Hall food court.
- **Demo mode** — when you're not at the mall (or deny location), set a simulated
  position with a long-press and drag it around to try everything.
- Light and dark themes follow your system preference.

## How it was built

The official PDF map was rendered to an image and digitized:

- `assets/data.json` — 240 stores (name, suite, category, district, map position),
  a ~100-node walkway graph, district polygons, suite label positions, parking
  lots, and amenities
- `assets/basemap.json` — vector building/walkway/hall polygons extracted from
  `assets/map_clean.jpg` by color classification and contour tracing
- `tools/build_data.py` — parses the PDF directory text and regenerates
  `data.json` plus a verification overlay render
- `tools/build_basemap.py` — regenerates `basemap.json` from the map raster
  (needs Pillow, numpy, scipy, scikit-image)
- `tools/app_template.html` — the app source; `__DATA__` is a placeholder filled
  in by `tools/assemble.py`

To rebuild after editing the template or data:

```bash
python3 tools/build_data.py     # optional: regenerate data.json (needs Pillow + poppler)
python3 tools/build_basemap.py  # optional: regenerate basemap.json
python3 tools/assemble.py       # writes index.html
```

`tools/test_app.mjs` is a Playwright smoke test (boot, GPS projection, heading-up
rotation, search, select, route).

## GPS calibration notes

Lat/lng is projected onto map pixels with an equirectangular transform (`GEO`
constants at the top of the script). The map art is not north-up: its "up"
points 115.5° in the real world, at 0.397 m per map pixel — both fitted by least
squares against surveyed store positions, anchored at The North Face storefront.
If your position still looks offset on site, stand somewhere recognizable and
long-press that spot on the map — the app stores the correction and applies it
from then on.

## Disclaimer

Store list and map are from the center's 2016 Map & Directory and may be out of date.
This is an unofficial personal project, not affiliated with Simon Property Group.
