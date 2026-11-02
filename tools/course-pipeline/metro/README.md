# Metropolis Links (`metro`)

A made-up course of 18 holes laid into six real cities (New York, London, Paris, Tokyo, Amsterdam, Rio de Janeiro), three holes each.
The cities are taken 1:1 from OpenStreetMap: every building outline with its height (`height`, else `building:levels` × 3.3 m; `building:part`s replace their outline;
`min_height` parts float, e.g. bridges and arcades), water (rivers, canals, the sea built from the coastline), parks and woods (turf), beaches (sand), street trees.
Montmartre and Rio get their ground from SRTM (1″). Nothing is moved or left out to make room: the holes go where there is room (streets, squares, parks,
over rivers), and on two holes from roof to roof. Only the Eiffel Tower, the Arc de Triomphe and Tokyo Tower are drawn as models (at their OSM position and size),
plus the London Eye and Christ the Redeemer, which are not buildings in OSM.

Files:
- `areas.py` the 18 places (anchor lat/lon, radius); `osm.py` downloads OSM tiles (api.openstreetmap.org `map` call, splits when too big, `relation/full` for big water); cache in `/tmp/metro-osm`.
- `parse.py` OSM XML → features; `geo.py` features in metres east/north of the anchor (shapely), parts replace outlines, sea from the coastline.
- `route.py` open-ground raster (1 m) and clearance; least-cost path through the streets; `snap` to the roomiest spot.
- `search.py` tees for a green at a given path length; `roofscan.py` / `roofpair.py` rooftop lines and pairs; `find.py` buildings by name; `plot.py` top-down pictures.
- `cfg.py` the holes (tee, green, waypoints, options); `build.py check` (clashes of fairway/green/tee with any building on the ground: must be none),
  `build.py plot i out.png`, `build.py write` → `data-metro.js` = `metro-engine.js` + `METRO_DATA`.
- `metro-engine.js` the course's code (defs, buildings, colliders, water/turf/sand raster, drawing, landmarks). Edit it here, then `build.py write`.

SRTM tiles: `curl https://s3.amazonaws.com/elevation-tiles-prod/skadi/S23/S23W044.hgt.gz` (and `N48/N48E002`), unpacked to `/tmp/metro-dem`.
