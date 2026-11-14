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
- `westminster/` and `landmand/` share one set of scripts; only `cfg.py` differs (origin, grid, 3DEP project, scorecard). Order: `parse.py` (OSM, env `LAT0 LON0 CNAME`), `ept.py`, `chm.py`, `gnd.py`, `mkgrids.py`, `gme.py`, `prep.py` (features, tees to the card, the boundary as the playing corridor), `build.py`.
- `ledgeview/` is a copy of those scripts with its own `cfg.py` (Ledgeview, Wisconsin, `WI_Brown_2_2020`), a Ledgeview tree mix in `build.py`, footbridges where the holes and cart paths cross the brooks. Every `prep.py` now draws its review image north up (before Ledgeview, Westminster, Landmand and Mountain Valley drew the photo upside down under the overlay).
- `fieldsranch/` (Fields Ranch East, Texas) is the Ledgeview scripts for a site with **no LiDAR of the finished course** (3DEP and TxGIO were flown before it was built, and the 2022 3DEP EPT stops south of Frisco): `dem.py` (Esri Terrain 3D tiles, from `stpatricks/`), `chm_img.py` (a canopy model from the Esri photograph: dark, textured, off the water and the mown ground), `gme.py` / `gmg.py` (Esri and Google imagery). Two courses share the site, so `parse.py` keeps the holes inside East's OSM outline and `prep.py` the features within 30 m of it; `cfg.py` holds what OSM lacks or gets wrong: a pond (`PONDS_HAND`), five sand areas (`SAND_HAND`), the 11th tee (`TEE_BOX`) and the housing no trees are taken from (`RESIDENTIAL`). Review sheets: `tcrop.py` (tees, rotated, both photos), `gcrop.py` (greens and bunkers), `bunkcand.py` (sand in both photos missing from OSM), `tsheet.py` (the built trees over the photo). Order: `LAT0=33.2068 LON0=-96.85 CNAME=East python3 parse.py` (OSM bbox `-96.8640,33.1975,-96.8370,33.2160` → `r.osm`), `dem.py`, `gme.py -1150 -950 1150 950 19 0.5 course_esri.jpg`, `prep.py`, `chm_img.py`, `build.py`.
- `sawgrass/` (TPC Sawgrass, THE PLAYERS Stadium Course, Florida) is the Fields Ranch scripts on the LiDAR route again (`ept.py`, `chm.py`, `gnd.py`, `mkgrids.py` from Ledgeview; 3DEP `FL_Peninsular_FDEM_StJohns_2018`). The Stadium and Dye's Valley courses share one OSM outline, so `parse.py` keeps the holes named `Stadium N`. `build.py` adds the Florida tree mix (slash pine 4, cabbage palm 9, live oak 0, palmetto 1) and places the **grandstands** (`stands` in the header: [e, n, facing bearing, length, rows, hole index]) clear of the mown ground, the sand, the water and 16 m from every hole's line, three each at the 17th and 18th, two at the 16th and some others, one elsewhere. Order: OSM bbox `-81.408,30.186,-81.380,30.212` → `r.osm`, `LAT0=30.1975 LON0=-81.3930 CNAME=TPC python3 parse.py`, `python3 ept.py 13 && python3 chm.py && python3 gnd.py && python3 mkgrids.py`, `python3 gme.py -750 -850 750 850 19 0.5 course_esri.jpg`, `python3 prep.py`, `python3 build.py`.
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
