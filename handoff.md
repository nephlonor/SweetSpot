# Handoff

Nur offene Tasks hier. Was erledigt ist, gehört nach `docs/CHANGELOG.md` (und wird hier gelöscht).

MODELL: claude-sonnet-5-5
STATUS: OPEN
PUSH: ja

# Ziel
Westminster National (MD) und Landmand (NE) fertigbauen. Beide sind nur für den Spieler „Florian“ sichtbar (`beta: true`), spielbar, zeigen aber den „im Bau“-Hinweis (`PBN_SHOW`) und sind noch nicht in der Daily-Rotation.

# Offen
- **Landmand-Gelände:** Das LiDAR (USGS NE Northeast 2020) zeigt den Platz noch im Bau: Das Großrelief stimmt, die Konturen der Grüns und Bunker fehlen weitgehend. Prüfen, ob es neueres LiDAR gibt; sonst Grüns und Bunker formen.
- **Landmand-Routing:** Im Luftbild liegen zwischen den 18 OSM-Löchern weitere Spielbahnen (vermutlich Kurzplatz oder Putting-Kurs). Prüfen, ob die Zuordnung stimmt.
- **Westminster-Abschläge:** Loch 14 (OSM-Linie 225 m, Karte 291 m) und Loch 15 (233 m statt 294 m) wurden 57–59 m nach hinten verlängert. Die echten Abschläge auf den Luftbildern prüfen (`tcrop2.py`).
- Noch nicht gemacht (Guide Schritte 2–7): Grüns von Hand nachzeichnen, Bunker-Review, Baum-Tweaks pro Abschlag, Mähmuster, Drohnenansicht, Kartentest (`mapt.js`), Klangpegel (`snd.js`).
- Wenn fertig: `beta: true` entfernen (Build wird dann 11.0), `PBN_SHOW` auf false setzen, Daily-Rotation ab einem künftigen Datum erweitern (index.html, leaderboard.yml, daily-overall.js).
