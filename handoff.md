# Handoff

**Stand:** Geheimer Kurs „The Isles" (`isles`, nur sichtbar für Spielername „Florian") ist in `main` (PR #699, Build 9.0; PR #702, Build 9.1). 18 Löcher, Par 72, 7301 yd, 4 Par 3 / 4 Par 5, schmale Inselfairways im Wasser, keine Bunker, kaum Gefälle, kleine bohnenförmige Par-3-Grüns. Pop-up beim Wählen („-10 oder besser … Good luck!"). Generator `isleHole()` in `index.html`; Wasser-Drop immer auf dem gespielten Loch (jedes Loch ist eine eigene Welt).

**Offener Fehler:** Auf Florians Gerät friert die App direkt ein, nachdem Loch 1 angezeigt wird. Im Headless-Chromium nicht reproduzierbar (Kurs wählen → Loch-Karte → „Play Hole" → address läuft, Bildrate wie GCC Basel, auch bei 4× CPU-Drosselung). PR #702 hat `polySigned` (Küstendistanz) ca. 2× schneller gemacht und den Inselumriss halbiert; ob das hilft, ist unbekannt.

**Nächste Schritte:**
1. Von Florian erfragen: Gerät/Browser, was genau friert (3D, Karte, Button), dauerhaft oder zeitweise.
2. Testversion mit Schalter `?isles=lite`, der Meeresfläche (`W.sea`, `updateSea`), Steine/Pfähle (`buildCoast`) und Wildtiere (`buildLife`, derzeit `!RDC.coast`) einzeln abschaltet, um den Verursacher am Gerät zu finden.
3. Procedural-Küste (`def.coast`) lief bisher nur im abgeschalteten Legacy-Kurs, nie live auf einem Handy.

**Weiteres:**
- Rundenwerte für `isles` landen im Leaderboard-Workflow nicht (nur Kurse aus `leaderboard.yml`); `leaderboard/isles.json` ist leer.
- Wasser sieht aus wie See; Ufermauern aus dem Foto fehlen.
- Testen ohne Beschränkung: `settings.name = 'Florian'; setCourse('isles')` in der Konsole.
- Der User will PRs in diesem Repo automatisch gemergt haben.
