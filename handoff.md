# Handoff

Nur offene Tasks hier. Was erledigt ist, gehört nach `docs/CHANGELOG.md` (und wird hier gelöscht).

MODELL: claude-sonnet-5-5
STATUS: OPEN
PUSH: ja

# Ziel
Westminster National (MD) und Landmand (NE) fertigbauen. Beide sind für alle spielbar (seit Build 11.0), der „im Bau“-Hinweis ist seit Build 11.9 aus; noch nicht in der Daily-Rotation.

# Offen
- **Landmand-Gelände:** Das LiDAR (USGS NE Northeast 2020) zeigt den Platz noch im Bau: Das Großrelief stimmt, die Konturen der Grüns und Bunker fehlen weitgehend. Prüfen, ob es neueres LiDAR gibt; sonst Grüns und Bunker formen.
- **Landmand-Routing:** Im Luftbild liegen zwischen den 18 OSM-Löchern weitere Spielbahnen (vermutlich Kurzplatz oder Putting-Kurs). Prüfen, ob die Zuordnung stimmt.
- **Westminster-Abschläge:** 6, 11, 13, 14 und 15 wurden auf Kartenlänge nach hinten verlängert (14/15 um 57–59 m); 6, 11, 13 und 15 stehen dadurch im Wald (Schneise, Sicht frei). Die echten Abschläge auf den Luftbildern prüfen (`tcrop2.py`) und wie Loch 7 per `TEE_BOX` setzen.
- Noch nicht gemacht (Guide Schritte 2–7): Grüns von Hand nachzeichnen, Bunker-Review, Baum-Tweaks pro Abschlag, Mähmuster, Drohnenansicht, Kartentest (`mapt.js`), Klangpegel (`snd.js`).
- Wenn fertig: Daily-Rotation ab einem künftigen Datum erweitern (index.html, leaderboard.yml, daily-overall.js).

# Ledgeview (WI), seit Build 12.0 für alle spielbar
- Pipeline `tools/course-pipeline/ledgeview/` (Kopie von Westminster; OSM vollständig, LiDAR `WI_Brown_2_2020` EPT). Daten neu: Skripte in einen Arbeitsordner kopieren, dort `python3 ept.py 13 && python3 chm.py && python3 gnd.py && python3 mkgrids.py`, Luftbild `python3 gme.py -560 -460 560 500 19 0.5 course_esri.jpg`, OSM-Extrakt (`api.openstreetmap.org/api/0.6/map?bbox=-88.004,44.420,-87.982,44.434` → `r.osm`), `LAT0=44.4272 LON0=-87.9936 CNAME=Ledgeview python3 parse.py`, `python3 prep.py`, `python3 build.py`.
- Noch nicht gemacht (Guide Schritte 2–7): Grüns von Hand nachzeichnen, Bunker-Review, Abschläge auf den Luftbildern prüfen (4 und 11 sind um 16 m nach hinten verlängert), Baum-Tweaks pro Abschlag, Drohnenansicht gegen Fotos.
- Unbestätigt: Fahnenfarbe (gold mit grüner Zahl nach den Club-Farben, kein Foto der echten Fahnen gefunden). RED (Heimkurs) fragen.
- Nicht in der Daily-Rotation.

# Metropolis Links (Test, nur Florian)
- Pipeline `tools/course-pipeline/metro/` (README dort). Daten neu: `python3 build.py write` (braucht OSM-Cache `/tmp/metro-osm` → `fetchall.py`, SRTM in `/tmp/metro-dem`).
- Offen: Rückmeldung von Florian zu den Bahnen. `data-metro.js` ist 1,8 MB (Gebäude bis 430 m um die Bahn); bei Bedarf `keep` in `cfg.py` kleiner. Big-Ben-Modell nicht gesetzt (OSM-Teile ohne Namen, der Turm steht als OSM-Gebäude). Montmartre/Rio-Gelände aus SRTM (30 m, in Städten teils mit Gebäuden verrauscht).
