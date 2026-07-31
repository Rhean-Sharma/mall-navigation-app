# Woodbury Common Navigator

A single-file interactive wayfinding app for **Woodbury Common Premium Outlets**, built
from the official Map & Directory. Open `index.html` on your phone — no build step, no
server, no dependencies.

## Features

- **Interactive map** — pan, pinch-zoom, and rotate the full mall map with all six
  color-coded districts (Adirondacks, Saratoga, Hudson Valley, Hamptons, Niagara,
  Market Hall). Tap a district chip to highlight its area and list its stores.
- **Live position** — uses the browser Geolocation API to show where you are inside the
  mall (the outlet is open-air, so GPS works well), with an accuracy ring.
  Long-press the map while GPS is on to fine-tune calibration; the offset is remembered.
- **Compass orientation** — a heading cone on your position marker, plus a
  heading-up mode that rotates the whole map with the direction you're facing
  (tap the compass button; iOS asks for motion permission).
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

The official PDF map was rendered to an image and hand-digitized:

- `assets/map_embed.webp` — the map raster embedded into the app
- `assets/data.json` — 240 stores (name, suite, category, district, map position),
  a ~100-node walkway graph, district polygons, parking lots, and amenities
- `tools/build_data.py` — parses the PDF directory text and regenerates
  `data.json` plus a verification overlay render
- `tools/app_template.html` — the app source; `__DATA__` and `__MAPIMG__` are
  placeholders filled in by `tools/assemble.py`

To rebuild after editing the template or data:

```bash
python3 tools/build_data.py   # optional: regenerate data.json (needs Pillow + poppler)
python3 tools/assemble.py     # writes index.html
```

`tools/test_app.mjs` is a Playwright smoke test (boot, search, select, route).

## GPS calibration notes

Lat/lng is projected onto map pixels with a simple equirectangular transform
(`GEO` constants at the top of the script: reference point, meters-per-pixel, map
bearing). The defaults assume map-up ≈ north with the gazebo as the anchor. If your
position looks offset on site, stand somewhere recognizable and long-press that spot
on the map — the app stores the correction and applies it from then on.

## Disclaimer

Store list and map are from the center's 2016 Map & Directory and may be out of date.
This is an unofficial personal project, not affiliated with Simon Property Group.
