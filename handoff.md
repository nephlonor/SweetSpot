# Handoff

Nur offene Tasks hier. Was erledigt ist, gehört nach `docs/CHANGELOG.md` (und wird hier gelöscht).

MODELL: claude-sonnet-5-5
STATUS: OPEN
PUSH: ja

# Ziel
Westminster National (MD) und Landmand (NE) fertigbauen. Beide sind für alle spielbar (seit Build 11.0), der „im Bau“-Hinweis ist seit Build 11.9 aus, seit 08.11.2026 in der Daily-Rotation.

# Offen
- **Landmand-Gelände:** Das LiDAR (USGS NE Northeast 2020) zeigt den Platz noch im Bau: Das Großrelief stimmt, die Konturen der Grüns und Bunker fehlen weitgehend. Prüfen, ob es neueres LiDAR gibt; sonst Grüns und Bunker formen.
- **Landmand-Routing:** Im Luftbild liegen zwischen den 18 OSM-Löchern weitere Spielbahnen (vermutlich Kurzplatz oder Putting-Kurs). Prüfen, ob die Zuordnung stimmt.
- **Westminster-Abschläge:** 6, 11, 13, 14 und 15 wurden auf Kartenlänge nach hinten verlängert (14/15 um 57–59 m); 6, 11, 13 und 15 stehen dadurch im Wald (Schneise, Sicht frei). Die echten Abschläge auf den Luftbildern prüfen (`tcrop2.py`) und wie Loch 7 per `TEE_BOX` setzen.
- Noch nicht gemacht (Guide Schritte 2–7): Grüns von Hand nachzeichnen, Bunker-Review, Baum-Tweaks pro Abschlag, Mähmuster, Drohnenansicht, Kartentest (`mapt.js`), Klangpegel (`snd.js`).

# TPC Sawgrass (FL), seit Build 14.0 für alle spielbar, „im Bau“-Hinweis an
- Pipeline `tools/course-pipeline/sawgrass/` (Reihenfolge im README). OSM vollständig, LiDAR 3DEP St Johns 2018. Tribünen von `build.py` automatisch gesetzt (nicht die echten Turnier-Standorte), Publikum-Jubel in `crowdReact`/`crowdBuf`.
- Auf echten Geräten prüfen: Lautstärke und Klang von Jubel/Applaus/Raunen, Bildrate an 16–18 (bis ~2500 Fans je Loch), Erzeugung der Klangpuffer (~0,8 s in Headless, wird 2,5 s nach Lochaufbau vorab gerechnet).
- Noch nicht gemacht (Guide Schritte 2–7, 9): Grüns von Hand nachzeichnen, Bunker-Review, Abschläge auf den Luftbildern prüfen (2, 6, 9, 12 um 15–23 m verlängert), Baum-Tweaks pro Abschlag, Mähmuster, Drohnenansicht, Farbvergleich mit Fotos, Fahnenfarbe (rot mit weißer Zahl, unbestätigt).
- Wenn fertig: `PBN_SHOW.sawgrass` auf `false`, Daily-Rotation ab einem künftigen Datum erweitern.

# Fields Ranch East (TX), seit Build 13.0 für alle spielbar, „im Bau“-Hinweis seit 14.0 aus
- Pipeline `tools/course-pipeline/fieldsranch/` (Reihenfolge im README). Kein LiDAR vom gebauten Platz: Gelände Esri World Elevation (vor dem Bau), Bäume aus dem Esri-Luftbild (`chm_img.py`, Wohnsiedlung `RESIDENTIAL` ausgenommen). Wenn TxGIO/3DEP neueres LiDAR veröffentlicht (Kachel 3396501c2), Gelände und Bäume daraus neu bauen; dann fehlen auch die Grün- und Bunkerkonturen nicht mehr.
- Abschläge 10 und 18 per `teeAim` (13.4); alle anderen geprüft: vorgeschlagener Drive landet auf dem Fairway. Bäume halbiert (13.4); falls weitere Abschläge falsch zielen: Ziel per `teeAim` setzen ([m entlang der Linie zum Grün, m links], Lochindex ab 0).
- Grüns auf höchstens 2,5 % Neigung begrenzt (13.3, `greenFlat` in `RDS.fieldsranch`); mit echtem LiDAR später wieder lockern.
- Erledigt in 13.2: Abschläge geprüft (11 von Hand, `TEE_BOX`), Grüns geprüft, 5 Sandflächen ergänzt (`SAND_HAND`), Bäume gesäubert, Farben/Fahne/Mähmuster nach Spielerfotos.
- Längen: 18 spielt 524 m statt 509 m (OSM-Abschlag hinten), 11 nur 334 m statt 358 m (die I-Box liegt nicht weiter hinten; die Kartenlänge gilt wohl für eine Box, die OSM nicht kennt).
- Offen: Baumdichte am Panther Creek grob (aus dem Foto geschätzt, Höhen synthetisch). Grüne Konturen fehlen im Gelände (Vorbau-Relief). Drohnenansicht nicht geprüft.
- Daily-Rotation ab einem künftigen Datum erweitern, wenn gewünscht.

# Ledgeview (WI), seit Build 12.0 für alle spielbar
- Pipeline `tools/course-pipeline/ledgeview/` (Kopie von Westminster; OSM vollständig, LiDAR `WI_Brown_2_2020` EPT). Daten neu: Skripte in einen Arbeitsordner kopieren, dort `python3 ept.py 13 && python3 chm.py && python3 gnd.py && python3 mkgrids.py`, Luftbild `python3 gme.py -560 -460 560 500 19 0.5 course_esri.jpg`, OSM-Extrakt (`api.openstreetmap.org/api/0.6/map?bbox=-88.004,44.420,-87.982,44.434` → `r.osm`), `LAT0=44.4272 LON0=-87.9936 CNAME=Ledgeview python3 parse.py`, `python3 prep.py`, `python3 build.py`.
- Noch nicht gemacht (Guide Schritte 2–7): Grüns von Hand nachzeichnen, Bunker-Review, Abschläge auf den Luftbildern prüfen (4 und 11 sind um 16 m nach hinten verlängert), Baum-Tweaks pro Abschlag, Drohnenansicht gegen Fotos.
- Unbestätigt: Fahnenfarbe (gold mit grüner Zahl nach den Club-Farben, kein Foto der echten Fahnen gefunden). RED (Heimkurs) fragen.
- Seit 08.11.2026 in der Daily-Rotation.

# Grafik-Update (Builds 13.7, 13.8)
- Auf echten Geräten prüfen (nur im Headless-Chromium getestet): Bildrate auf iPhone/Android in Auto und High, Fernschatten und Boden-Details bei Dawn/Dusk, Blick zur Sonne (Sonnenscheibe, Dunst).
- Farben: Sonne stärker, Himmelslicht kühler, dazu die Farbabstimmung im letzten Durchgang. Die an Fotos abgeglichenen Platzfarben (Fields Ranch, Ledgeview, Landmand …) wirken etwas satter; falls zu kräftig: `hemW`/Sonnenstärke in `updateWeatherVisuals` oder die Grade-Zeilen im Tilt-Shift-Shader zurücknehmen.
- Fernschatten nehmen die Baumhöhe aus dem Kronenradius (echte Plätze) und ignorieren das Gelände; wenn Schatten an Hängen falsch liegen, Höhe in `plan` mitgeben.
- 13.8: Neue Baum-/Fels-/Wolkenmodelle und Unterwuchs nur im Headless-Chromium geprüft. Liegende Stämme, Stümpfe, Farne und Steine haben keine Kollision; falls das beim Spielen stört, Kollider ergänzen oder weiter von der Spiellinie weg setzen (`buildUndergrowth`). Menschengemachte Objekte (Bank, Schilder, Abfalleimer, Gebäude, Brücken) sind noch die alten.
