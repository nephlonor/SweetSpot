# Building a new real course

How to add a real golf course to Sweet Spot Golf. Follow it step by step. Every step ends with a check you **look at**, either an image or a number. Nothing goes in on trust.

The Rothley Park pipeline (`tools/course-pipeline/rothley/`) is the reference implementation. Copy it into a new folder and change the origin, the data sources and the hand-made lists. The Augusta build (`tools/course-pipeline/augusta-build.py`, `ept.py`, `chm.py`, `dem.py`) shows the US LiDAR route (USGS 3DEP point cloud).

Lessons from Rothley Park are marked **Pitfall**. Each one cost a round of feedback.

---

## 0. Before you start

**Gather these first:**
- **Name and location:** the course's exact name and its position. Look it up with Nominatim: `https://nominatim.openstreetmap.org/search?q=<name>&format=json`. Choose an origin `LAT0, LON0` near the middle of the course. Every course coordinate is in metres east and north of that point (`KX = 111320·cos(LAT0)`, `KY = 111132`).
- **Scorecard:** for every hole, the par, the stroke index and the yardage from **each** tee. Take it from the club website, GolfPass or similar. Check that the per-hole numbers add up to the card totals. Sources disagree, so prefer the one that adds up and say which one you used.
- **The club's own pictures:** the course guide and hole photos on the club website, plus a Google Images search for "<course> golf". Download them and make contact sheets (6 per image) and **look at all of them**. They give you the visual identity (step 9).

**Pick the data sources by country:**

| What | UK (England) | France | USA | Elsewhere |
|---|---|---|---|---|
| Ground (DTM) | Environment Agency LiDAR composite DTM 1 m (WCS, `environment.data.gov.uk/spatialdata/lidar-composite-digital-terrain-model-dtm-1m/wcs`, EPSG:27700) | IGN RGE ALTI / LiDAR HD MNT (geopf WMS) | USGS 3DEP ImageServer, or the EPT point cloud on S3 | national LiDAR portal, or SRTM/Copernicus 30 m as a last resort |
| Canopy (trees) | EA first-return DSM 1 m minus the DTM | IGN LiDAR HD MNH | 3DEP EPT points (DSM − ground) | national DSM; else trees from imagery only |
| Holes, paths, water, buildings | OpenStreetMap (`api.openstreetmap.org/api/0.6/map?bbox=`; Overpass may be blocked) | same | same | same |
| Aerial photo | Google satellite tiles (`mt1.google.com/vt/lyrs=s`) **and** Esri World Imagery (a second date) | same | same | same |

**Pitfall: one photo isn't enough.** Always fetch **two** imagery sources. At Rothley the Google mosaic has a dark seam over holes 1, 2, 17 and 18, which hid bunkers and greens. Esri, a different date and season, showed them.

## 1. Fetch the data

Scripts: `parse.py`, `lidar.py`, `gm.py` / `gme.py`.

1. **OSM extract:** take the course bounding box plus about 150 m. Run `parse.py`, which writes `feat.json`: holes (`golf=hole` with `ref`), greens, tees, fairways, bunkers, water, streams, paths, buildings, woods, boundary and pins.
   - **Check:** print each hole with its ref, its length along the line and its start and end points. Compare the length with the scorecard. A line that's 30–50 m short usually starts at a forward tee.
   - **Pitfall: OSM is often incomplete.** Rothley had the 18 hole lines and pins and nothing else: one green, no fairways, bunkers or tees. Find out what's missing before planning the rest.
2. **LiDAR:** use 1 m cells on the local grid, with row 0 at the south. Save `mnt.npy` (ground) and `mnh.npy` (canopy height = DSM − DTM, clipped 0..60).
   - **Check:** min and max height, no NaNs. Render a hillshade, or the "trough map" `G − median_filter(G, 9)`, and look at it.
3. **Aerial mosaic:** 0.5 m per pixel, north up (`gm.py e0 n0 e1 n1 zoom res out.jpg`). Fetch both sources.
   - **Check:** overlay the OSM hole lines on the mosaic (`ov.py` pattern). The lines must run down the fairways. If they're offset, fix the projection before anything else.

## 2. Greens: trace every one by hand

Tools: `gcrop.py` for gridded crops, `gman.py` for the traces, `vsheet.py` to verify.

- **Automatic detection is only a first guess** (`greens.py`, region growing on smooth, bright pixels). It fails on shadows, double greens and dark imagery.
  - **Pitfall:** at Rothley it took one green into the fairway (the 11th) and merged a double green (4/13).
- **Trace every green by hand:**
  1. Make crops 80–100 m across, at 6 px/m, with a labelled 10 m grid (`gcrop.py src out refs half`).
  2. Write the outline in crop pixels; `gman.py` converts it to metres.
  3. Use the photo where the green isn't in shadow, and compare both photo sources.
- **Double greens:** look for them on purpose. List every pair of hole ends within about 110 m and make a wide crop of each pair. A double green goes in as **one** green shape in the features (the hull of both halves). Each hole keeps its own half for the pin position and the green contours.
  - **Pitfall:** two touching ellipses read as two greens with fringe between them. The player saw that immediately.
- **Verify** with `vsheet.py`: magenta outlines and red bunker outlines over 6 greens per image. Re-trace anything that overlaps a bunker or misses an edge.

## 3. Fairways

Tools: `fair.py`, `fairpoly.py`.

- Fairways are fitted as a **ribbon** along the hole line. At every 4 m, the left and right edges are found from the photo: brightness minus texture, with no canopy (`fair.py`). Widths are median-filtered and smoothed (`fairpoly.py`).
- The fairway starts about 20% of the way along on par 4s and 5s (or wherever the photo shows it) and ends about 12 m short of the green. Par 3s get no fairway.
- **Check:** overlay all the fairway polygons on the photo, cluster by cluster (6 crops), and look at every hole. Mown bands in the photo must sit inside the ribbons.
  - **Where the fairway starts:** check it per hole on the aerial photo, using a crop with distance marks from the tee. A club photo taken mid-hole can make it look as if the fairway starts at the tee.

## 4. Bunkers

Tools: `bunk.py`, `bunk2.py`, `hsheet.py`.

1. **Colour pass** on the main photo (`bunk.py`), keeping blobs that are:
   - bright, low in saturation and slightly red;
   - 12–450 m²;
   - no more than 3.2 times as long as they are wide;
   - **surrounded by grass**, with a ring test;
   - within 22 m of a fairway or green;
   - not on paths or buildings.
2. **Second pass in dark areas** (`bunk2.py`): contrast against the local mean, run on **both** photos. Keep only blobs found in **both**.
3. **Review every hole** with `hsheet.py`: a crop of each whole hole with every bunker numbered. Write down false hits by number, then drop them.
   - **Typical false hits:** white tee shelters, footbridges, signs, hay fields, specks in the rough, sandy paths.
   - **Missed bunkers:** add them by number from the second pass.
   - **Pitfall:** the white blob I dropped as a "false bunker" on the 6th was a **footbridge over a ditch**. A false hit is still worth a second look, because it may be a feature you should model.

## 5. Tees: play to the card

The player's rule, which went through three rounds: **the course must play as close as possible to the scorecard yardage from the back (white) tees.**

1. Find the real rearmost tee box first, on rotated tee crops with 2 m ticks behind the OSM tee point (`tcrop2.py`), using both photo sources. That's the starting point and the sanity check.
2. Move the back tee back along the opening line until the hole measures the card length: `want = card_m − current_length`, in 0.5 m steps (`tees.py`). Stop early only for these:
   - another hole's green (8 m), a bunker (6 m), water (6 m), a building (8 m);
   - another hole's fairway;
   - the course boundary.

   Trees don't stop a tee. `build.py` clears a 10 m wide **tee chute**, from 12 m behind the tee (where the camera stands, about 9 m back) to 15 m in front of the old box, the way a club cuts a chute.
3. **Report** each hole's played length against the card, and name any hole that can't reach it and why. At Rothley the 2nd stops at 307 m of 312 because of the 1st green's bunker.
4. **Check** every tee shot (`tests/rot.js`) for a clear view and a tee that reports `surf 0`.
   - **Pitfalls:**
     - a tee in a tree chute without clearing puts the camera inside a crown;
     - clearing the chute shifts tree indices (see step 7).
5. **Forward tees:** set them along the opening leg using the scorecard differences between tee sets.

## 6. Water: streams, ditches, ponds

Tool: `ditch.py`.

- **Ponds:** use the OSM water polygons. Drop `intermittent=yes`, which is usually construction basins.
- **Streams** (OSM `waterway=stream|river`, without `tunnel`):
  - cut them into channel pieces about 12 m long, 4 m wide for a brook;
  - set `creek: true` on the course in `RDS`, so they play as penalty areas.
- **Ditches:** look at the LiDAR trough map (`G − median_filter(G, 9)`) over the whole course. Ditches are narrow dark lines 0.4 m or more deep.
  - Trace the ones that **cross play** by hand on a zoomed trough crop. Pieces are 2.6 m wide and 10 m long.
  - Field ditches under hedgerows don't matter; leave them out.
  - **Pitfall:** the same map shows medieval **ridge and furrow**. That's broad and shallow, not a ditch, and it's already in the relief.
- **Footbridges:** wherever a hole line or path crosses a stream or ditch, add an entry to `bridges` as `[e, n, walkway width, span, bearing of the water]` (timber bridges in the game).
- **Pitfall: cascading cuts.** Creek pieces must measure their banks on the **original** ground (`Hw = Float32Array.from(Hg)`, switched on by `RDS.<course>.lush` or `.creek`). Otherwise each piece is cut relative to its neighbour's already-cut bank, and the channel ends up 8 m deep.
  - **Check:** probe the profile across the water in the game (`tests/b18.js`). Banks should sit about 0.3 m above the water, and the whole cross-section should look like the LiDAR.
- **No trees in water.** Drop trees standing on any creek, ditch or pond (plus 1 m) in the build.
  - **Pitfall:** the canopy model sees bankside trees right over the brook.

## 7. Trees

These come from the canopy model, in `build.py`:

- **Peaks:** local maxima 2.5 m or more tall. Crown size comes from the radius at half height.
- **Kinds:**
  - 1: hedge or shrub (under 4.5 m)
  - 2: conifer (tall and narrow, plus a small share of the tall trees)
  - 6: silver birch (slender, mid-height)
  - 0: broadleaf
  - The game also knows 4 (loblolly pine) and 5 (dogwood).
- **Woodland fill:** a 7 m lattice where the canopy is 7 m or more.
- **Clearing:** drop trees on mown ground (fairways, greens, tees) and in water.
- **Check:** look at all 18 tee shots (`tests/rot.js`). Anything blocking the line off the tee gets hidden with `RDS.<course>.tweak[index] = { hide: true }`.
  - **Pitfall: indices shift after a rebuild.** Every rebuild that changes the tree list changes the indices. Find hidden trees again **by coordinates**: decode the old and new `trees` arrays and match the nearest point.

## 8. Build and integrate

**The build** (`build.py`) produces two parts:
- **`rd_head.js`** (`const RD_<COURSE> = {name, origin, mounds, bridges, holes, ntrees, z0, gr}`), which goes into `index.html` after the other `RD_*` lines.
- **`data-<course>.js`** (`Object.assign(RD_<COURSE>, {relief, dem, feat, trees, forest, orchard, boundary, ditch, rail, buildings, cover, streams, straw, flowers, alti}); RDS.<course>.alti = RD_<COURSE>.alti;`), which is loaded lazily.

**Each hole** has: `par`, `hcp`, `len`, `lens` (one per tee), `tee`, `green` (centroid of the traced green), `line`, `mk` (`w y b r` markers) and `desc` ("plays N m up/downhill" when it's 3 m or more).

**Places in the game to touch:**
- `<COURSE>_DEFS`, `RDS.<course>`, `DATA_FILES`, `COURSES.<course>`.
- The course dropdown options, in both `<select class="segCourse">` elements.
- `GUST_COLS`, `CLIP_COURSES` (append at the end only; clip indices are stored in saved clips), `AMB` and `musicWanted`.
- `DAILY_COURSES*`: start the new rotation on a future date so past days keep their course. Make the same change in the **leaderboard workflow** (course-of-the-day check, and par in its `COURSES` map) and in `.github/scripts/daily-overall.js`.
- An empty `leaderboard/<course>.json` (`[]`).
- The help text "The courses", with data credits and licences.
- Weather, if the course has its own climate: `WX_COURSE`.

`pages.yml` already deploys every `data-*.js`.

## 9. Visual identity: make it look like the place

Work from the club photos and Google Images. Write down what is **specific** to this course, then build each item:

- **Turf and colours** (`AUT_OFF`-style colour offsets per surface; `terrainMatFrom`, the yardage map's `colOf`, trees, tufts, reeds):
  - pick a colour scheme that no other course uses;
  - keep the rough a **classic, close-cut green** unless the photos show otherwise;
  - **Pitfall:** tall straw-coloured grass read as "not a golf course".
- **Mowing pattern:** match it exactly, including the **angle**, the **pass width** and the **contrast**. On top of the cross-cut, the **last pass** (the mower always finishes on one diagonal) shows strongest and shifts the hue slightly: lighter and a touch yellower (`lastPass()` in the shader; in the map, `crossCutJS` gives it a 45% weight). Rothley cross-cuts **on the diagonal**: two sets of mowing lines at **45° to the hole** in both directions, 9 m passes, clearly light and dark. Where they cross they form **diamonds** (`crossCut(p, angle, width)` in the shader, `crossCutJS` for the map; both must use the same numbers).
  - **Check:** compare against the club's drone photos with a drone-height render (`tests/drone.js hole name`: 45 m up, 30 m behind the ball). A view from the tee foreshortens everything, so it can't judge the pattern.
  - **Pitfall:** it took four rounds. A 45° checkerboard of squares, then lines at 34° (which read as nearly lengthwise from the tee), then too narrow and faint. Measure the angle on the photo before writing the shader.
- **Furniture:**
  - flags (colour, pennant or rectangle);
  - tee markers;
  - bins and ball washers;
  - shelters, fences, bridges, stone or brick edging on ditches.
- **Landmarks** visible from play: a railway, a clubhouse, church bells, and so on.
- **Trees:** the species mix (birches, pines, oaks) and the season.
- **Soundscape:** a piece of its own in `AMB` and `ambStep`, plus local sounds (Rothley: robin, wind in oaks, church-bell rounds, a steam train).
  - **Check:** render it offline (`tests/snd.js`) and compare the peak level with the other pieces.

## 10. Verify in the game (all of it, every time)

Run headless Chromium with `--use-gl=swiftshader`, three.js served from the scratchpad copy, and the page loaded from `file://`.

1. **Syntax and lint.** Extract the inline scripts, then run `node --check` and `eslint --no-eslintrc --env browser,es2022 --rule no-undef:error`.
   - **Pitfall:** a `//` comment inside a one-line object literal comments out the rest of the line and breaks the whole page.
2. **All 18 holes** (`tests/rot.js 0 17`), as a contact sheet:
   - every tee reports `surf 0` (on the tee) and `cupSurf 6` (cup on the green);
   - no page errors;
   - the line of play looks right on every hole.
3. **Hole maps** (`tests/mapt.js <course>`): opens and captures on every hole, with contrast greater than 0.
4. **Close views** (`tests/d7.js hole e n name`): the water crossings, bridges, ditch edging, a ball in the rough, and a rain view.
   - **Drone view** (`tests/drone.js hole name`): the mowing pattern against the club's photos.
   - **Overlays never cover the play cards:** the live boards (`#dlPanel` and `#mpPanel`) sit below the HUD and fade back while the lie and strike card (`#readout`) is up. Keep any new floating panel at `z-index: 1`.
5. **The other courses** still build (`rot.js` with `setCourse('gccb' | 'alsace' | 'augusta')`).
6. **Course-wide numbers:** the daily rotation for yesterday, today and tomorrow; the share of rain if the weather changed (simulate it); the total length against the card.

**Test pitfalls:**
- **Hiding the HUD:** use `opacity: 0`, not `display: none`, which breaks the swing dial with a negative radius.
- **Grass:** it builds one slice per frame. In headless it can take 20 s or more, so run `groundJob` to completion by hand before a screenshot.
- **Rainbow camera:** after rain, "Enjoy the rainbow" lifts the camera to the sky. That's intended, not a bug.

## 11. Ship

Before shipping, write a short report:
- **What was traced by hand** and what was automatic.
- **Where the course differs from the scorecard**, and why.
- **What the player should check**, and what you could not verify.

Then:
1. Commit on the working branch and push.
2. Open the PR, or update it.
3. **Don't merge until the player has tested**, when they ask for that.
4. Give a test link: `https://raw.githack.com/<owner>/<repo>/<branch>/index.html`.
