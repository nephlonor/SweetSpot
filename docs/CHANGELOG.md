# Changelog / erledigt

Alles Erledigte aus `handoff.md` wandert hierher (neueste oben). Dazu: Lobby-Leaderboard zeigt die eigene beste Runde als Geist „Name · PB" (Builds 9.18–9.20).

- Build 9.38: Landmand-Grüns spielbar: Das LiDAR (2020) zeigt den Rohhang vor dem Bau (bis 30 % Neigung, 3 m Wellen). Jedes Grün behält Fallrichtung und Konturform, aber höchstens 3,5 % Grundneigung, ca. 9 % lokale Neigung und etwa 1 m Welligkeit (`RDS.landmand.greenFlat`, im Spiel nachgemessen: 2,5–3,6 %). `realGreen`: Mit `flat[2]` werden die Konturen von der echten Ebene gemessen, sonst kam ein Teil der weggenommenen Neigung zurück (St Patrick's unverändert).
- Build 9.37: Eigene Musik für die beiden Test-Plätze: Westminster „Bear Branch“, ein Old-Time-Reel in A-Mixolydisch (Clawhammer-Banjo „bum-ditty“, Fiddle mit Bordun, Kontrabass, AABB); Landmand „Loess Hills Waltz“, ein Cowboy-Walzer in D, pentatonisch (Mundharmonika mit Bendings, Gitarre Bass-Schlag-Schlag, fernes Güterzughorn aus dem Missouri-Tal). Pegel an die anderen Plätze angeglichen.
- Build 9.36: Zwei neue Plätze im Test (nur für den Spieler „Florian“ sichtbar, `beta: true` in `COURSES`, zählen noch nicht zur Build-Nummer; „im Bau“-Hinweis): **Westminster National** (Maryland, Blue tees, 5945 yd, Par 71) und **Landmand** (Nebraska, Red tees, 7200 yd, Par 73). Pipeline in `tools/course-pipeline/westminster|landmand` (OSM + USGS-3DEP-LiDAR, Abschläge auf Kartenlänge). Eigene Identität aus den Club-Fotos: Westminster gelbliches Olivgrün statt Herbstlaub, blaue Fahnen, Bach (Bear Branch), Kardinal/Blauhäher/Gänse/Truthahngeier, Fiddle-Stück; Landmand gelbgrüne Fairways, strohgoldene Prärie, Truthahn/Fasan/Rotschulterstärling/Bussard, Wiesenstärling und Präriewind, Mundharmonika-Stück. Nicht in der Daily-Rotation.
- Build 9.30: Neues Titel-Logo (`logo.png`, roter Hintergrund freigestellt, 1200×451 RGBA).
- Build 9.31: Ladebildschirm = rotes Logo-Bild (`splash.jpg`) mit „Loading…“, mindestens 1 s sichtbar.
- Build 9.32: Ladebildschirm = Golfplatz-Bild mit App-Icon und Logo (`splash.jpg`, unten in Grün ausgeblendet), „Loading…“ darunter.
- Build 9.33: Ladebildschirm = Pebble-Beach-Screenshot + freigestelltes Icon+Logo (`splash-logo.webp`), passt sich jedem Seitenverhältnis an. Erststart: Icon-Zwischenbild im Intro-Video entfernt, Video startet erst, wenn der Ladebildschirm ausblendet (`afterSplash`). sw.js: fehlendes `splash-hero.webp` aus dem Precache entfernt.
- Build 9.34: `pages.yml` kopiert jetzt auch `*.webp` (Splash-Logo fehlte live), Splash-Bilder ohne Alt-Text/Fehler-Icon, Ausblenden 0,5 s.
- Build 9.35: Ladebildschirm mind. 2 s. Startmenü aufgeräumt: Logo frei ohne Karte, Platzname als kleines Label, Kurs+Spieler in einem Panel, Daily-Untertitel kürzer („… left“, einzeilig), Anleitungskarten im Querformat ausgeblendet.

## Stand bis Build 9.17 (aus handoff.md)


**Stand:** Geheimer Kurs „The Isles" (`isles`, sichtbar für Florian und für alle, die irgendwo eine Runde mit -10 oder besser beendet haben: `isleOK()`, Flag `ssg-isle-q`; Rangliste nur für sie) ist jetzt **eine gemeinsame Inselwelt** (Build 9.6). Alle 18 Löcher liegen auf einer Karte (Kleeblatt-Route, ca. 2,8 × 2,5 km) und sind beim Spielen sichtbar; Löcher kreuzen sich (Loch 5 über 14, Loch 7 über 18). Jedes Loch wird im eigenen, gedrehten Rahmen gespielt (`C.enu`/`C.loc` wie bei den echten Kursen).

**Aufbau in `index.html`** (Blöcke „The Isles"):
- Welt: `islBuildWorld()` (einmalig, `ISL.wd`), Löcher `islHoleSpec(i)` (lokaler Rahmen: Abschlag bei 0/0, f vorwärts), Platzierung `islLayout()` (Parameter `ISL.shape/A/gap/s0` per Scan gewählt: keine Überlappung), Inselchen `islIslets`, zentraler Strand `islCentral`.
- Boden/Flächen: `islEval` (Höhe, Küstenabstand, Mauer-/Strandmaske) und `islSurface`; `makeIslesCourse` baut das C-Objekt. Räumlicher Index in 128-m-Zellen.
- Rendering: `buildIslesHole` (Kacheln, Terrain nur im Lochfenster mit Feldern, sonst Weltraster `islRaster` als „far"-Textur), `islesSea`, `islesExtras` (Mauern, Felsen, Stapel, Blumen), Meerestiere `initMarine`.
- Shader: `isIsle` in `TERRAIN_GLSL` (Seegrund, Gischt, Fels außerhalb des Fensters).

**Früher behoben (Build 9.4):** Das Einfrieren auf dem iPhone kam vom Multiplayer: `mpState` ruft `G.C.enu()` auf; `makeIslesCourse` hat jetzt `C.enu`/`C.loc`.

**Inhalt:** Fairways halb so schmal an Engstellen; Grüns schrumpfen von Loch 1 bis 18 auf ein Drittel der Fläche (`islGS`); Loch 18 mit Wasser direkt ums Grün; 5 Inselgrüns (3, 7, 12, 13, 16); Risiko-/Belohnungslöcher mit mehreren Fairways (2, 5, 9, 11, 14); Plateaus/Klippen (6, 8, 17, 18, Inseln der Gabellöcher), Steigung max. 4,5 % entlang der Mittellinie; Steinmauern bis ans Fairway (kein Rough an der Mauer); ~150 Inselchen; Strände: 3 kleine (4, 10, 15) und ein großer Halbmond in der Mitte der Karte; Blumen; Delfine, Schildkröten, Robben, Fischschwärme, Wal.

**Spielregeln:** Wasser-Drop nur auf dem gespielten Loch (`C.holeLand`, `dryGround`, `waterOptions` wie Pebble Beach: nächstes Fairway/Abschlag).

**Leaderboard-Workflow (Build 9.17):** `gitCommit` überspringt den Commit, wenn nichts geändert ist (doppelte Stimme `[vote]` ließ den Lauf mit „nothing to commit" scheitern).

**Offen / Ideen:**
- Auf dem iPhone noch nicht gemessen: Aufbauzeit pro Loch (Desktop ca. 0,2–0,8 s) und Bildrate (Kacheln, 120×120-Meer, ~150 Inselchen).
- `isles` steht seit Build 9.11 im Leaderboard-Workflow (`leaderboard.yml`: Par 72); `leaderboard/isles.json` füllt sich mit den ersten Runden.
- Testen ohne Beschränkung: `settings.name = 'Florian'; setCourse('isles')` in der Konsole.
- Der User will PRs in diesem Repo automatisch gemergt haben.
