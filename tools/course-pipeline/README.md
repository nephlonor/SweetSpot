# Course pipeline

These are the scripts that built the real-course data files (`data-*.js` and the `RD_*` header in `index.html`). They aren't deployed (`pages.yml` copies only the game files).

The method, its checks and its pitfalls are in **[docs/NEW_COURSE_GUIDE.md](../../docs/NEW_COURSE_GUIDE.md)**. Read that first.

- `rothley/` is the reference pipeline:
  - **Fetch:** `parse.py` (OSM), `lidar.py` (Environment Agency DTM and DSM), `gm.py` / `gme.py` (Google and Esri imagery).
  - **Trace and detect:** `greens.py` (first guess), `gman.py` (hand-traced greens), `fair.py` + `fairpoly.py`, `bunk.py` + `bunk2.py`, `tees.py`, `ditch.py`.
  - **Review crops:** `grid.py`, `gcrop.py`, `vsheet.py`, `hsheet.py`, `tcrop.py`, `tcrop2.py`.
  - **Build:** `build.py`, which writes `rd_head.js` and `data-rothley.js`.
- `stpatricks/` is the route with no LiDAR and no OSM golf data:
  - **Fetch:** `dem.py` (Esri Terrain 3D elevation tiles), `gm.py` / `gme.py` / `gmw.py` (Esri Wayback, by date) / `gmb.py` (Bing).
  - **Course plan:** `reg.py` + `geo.py` (rectify the board photo and fit it to the aerial), `sbs.py` / `quad.py` / `cr.py` (gridded crops of several sources side by side).
  - **Trace:** `holes.py` (routing, tees to the card), `greens.json` (hand traces), `fw.py` (mown grass near the hole lines), `sand.py`, `feat.py` (fairways, bunkers, beach, sea, paths, boundary), `teeview.py`.
  - **Build:** `build.py`.
- `fourmile/` is the route for a US course whose point cloud has **no building or vegetation classes** (USGS CONMGaps 2026, only unclassified and ground):
  - **Fetch:** `dl.sh` (the LAZ tiles; rockyweb throttles with HTTP 429 and wants a browser User-Agent, so it resumes with retries), `parse.py` (OSM), `gm.py` / `gme.py` (imagery).
  - **Ground and canopy:** `lidar.py` (LAZ tiles into 1 m grids), `mkgrids.py` (ground from class 2, canopy = surface minus ground), `bld2.py` (houses: flat-roofed, compact canopy blobs fitted with minimum rectangles).
  - **Select and build:** `prep.py`, `build.py` (the tee goes back along the first leg to the card's length; a 9 m pad is mown where the Black tee is on no traced tee box). The desert palette, the piñon and juniper, the soundscape and the 8-course daily rotation are in `index.html`.
- `check.sh` runs the checks every edit to `index.html` needs.
- `augusta-build.py`, `ept.py`, `chm.py`, `dem.py` are the US LiDAR route (USGS 3DEP).
- `tests/` holds the headless Playwright checks:
  - `rot.js`: all holes;
  - `mapt.js`: hole maps;
  - `d7.js`: close views;
  - `tr7.js`: trees near a line of play;
  - `b18.js`: water profile;
  - `snd.js`: soundscape render;
  - `rough.js`: ball in the rough, rain;
  - `overallcard.js`: a name on the daily challenge's Overall tab opens the player card.
  - `merge2.js`: two devices merging into one account (runs the real workflow script from `leaderboard.yml` behind both browsers);
  - `merge3.js`: the request names one device id, another device of the same name answers it.

The scripts were written for a scratch session. Paths such as `/tmp/rothley` and the scratchpad folder, and the course origin, are hard-coded. Copy the folder, set the origin and paths, and run the steps in the order the guide gives.
