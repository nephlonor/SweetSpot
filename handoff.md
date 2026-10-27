# Handoff

**Stand:** Geheimer Kurs „The Isles" (`isles`, nur sichtbar für Spielername „Florian") ist in `main` (PR #699, Build 9.0; PR #702, Build 9.1). 18 Löcher, Par 72, 7301 yd, 4 Par 3 / 4 Par 5, schmale Inselfairways im Wasser, keine Bunker, kaum Gefälle, kleine bohnenförmige Par-3-Grüns. Pop-up beim Wählen („-10 oder besser … Good luck!"). Generator `isleHole()` in `index.html`; Wasser-Drop immer auf dem gespielten Loch (jedes Loch ist eine eigene Welt).

**Behoben (Build 9.4):** Das Einfrieren auf dem iPhone kam vom Multiplayer: `mpState` ruft `G.C.enu()` auf, das nur echte Kurse hatten; im Frame-Loop warf das jedes Bild einen TypeError. `makeCourse` hat jetzt `C.enu`/`C.loc` (Identität). Headless trat es nicht auf, weil dort keine MQTT-Verbindung zustande kommt.

**Weiteres:**
- Rundenwerte für `isles` landen im Leaderboard-Workflow nicht (nur Kurse aus `leaderboard.yml`); `leaderboard/isles.json` ist leer.
- Wasser sieht aus wie See; Ufermauern aus dem Foto fehlen.
- Testen ohne Beschränkung: `settings.name = 'Florian'; setCourse('isles')` in der Konsole.
- Der User will PRs in diesem Repo automatisch gemergt haben.
