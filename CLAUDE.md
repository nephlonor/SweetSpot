# Sweet Spot Golf

Single-file mobile browser golf game (`index.html`, three.js r128). The real courses' terrain, features and trees load lazily from `data-<course>.js`.

- **Adding or changing a real course:** follow [docs/NEW_COURSE_GUIDE.md](docs/NEW_COURSE_GUIDE.md) step by step, including every check. The scripts are in `tools/course-pipeline/`.
- **Don't change past daily challenges:** the daily-challenge course rotation must stay identical for past days. Change it only from a future date, and make the same change in `index.html`, `.github/workflows/leaderboard.yml` and `.github/scripts/daily-overall.js`.
- **Every merge to `main` bumps the build number** shown on the title screen: raise `APP_ITER.n` in `index.html` (the number after the dot, 7.1 → 7.2 → …). A new course makes the course count go up and the number after the dot restart at 0 (set `APP_ITER.courses` to the new count and `n` to 0).
- **Feature requests:** players' requests and votes live in `leaderboard/features.json` (`[{id, t, d, n, by, at, s:'open'|'done', v:{deviceHash:±1}}]`, written by `leaderboard.yml`). When a request is implemented, in the same PR set its `s` to `'done'` and add `done: <Date.now() ms>`; it then leaves the request list and shows in the Archive tab. Don't delete entries.

## Arbeitsweise
- Antworte auf Deutsch, knapp. Eine Session = eine Aufgabe, lange Aufgaben in Phasen.
- Beim Start zuerst `handoff.md` lesen, am Ende aktualisieren, committen und pushen.
- Bei neuer Projektidee, Feature oder mehrstufigem Bugfix (ohne laufende `handoff.md`): lies `.claude/workflow.md` und folge dem Planen-Ablauf. Kleine Änderungen direkt ausführen.
- Modell: Haiku/Sonnet für Routine, Opus nur für Architektur und schwierige Fehler.
