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
- `check.sh` runs the checks every edit to `index.html` needs.
- `augusta-build.py`, `ept.py`, `chm.py`, `dem.py` are the US LiDAR route (USGS 3DEP).
- `tests/` holds the headless Playwright checks:
  - `rot.js`: all holes;
  - `mapt.js`: hole maps;
  - `d7.js`: close views;
  - `tr7.js`: trees near a line of play;
  - `b18.js`: water profile;
  - `snd.js`: soundscape render;
  - `rough.js`: ball in the rough, rain.

The scripts were written for a scratch session. Paths such as `/tmp/rothley` and the scratchpad folder, and the course origin, are hard-coded. Copy the folder, set the origin and paths, and run the steps in the order the guide gives.
