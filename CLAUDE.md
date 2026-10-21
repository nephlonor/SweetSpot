# Sweet Spot Golf

Single-file mobile browser golf game (`index.html`, three.js r128). The real courses' terrain, features and trees load lazily from `data-<course>.js`.

- **Adding or changing a real course:** follow [docs/NEW_COURSE_GUIDE.md](docs/NEW_COURSE_GUIDE.md) step by step, including every check. The scripts are in `tools/course-pipeline/`.
- **After every edit to `index.html`:** run `tools/course-pipeline/check.sh` (inline scripts through `node --check` and eslint `no-undef`, plus a scan for code swallowed by a `//` comment). A syntax error stops the whole game from loading.
- **Don't change past daily challenges:** the daily-challenge course rotation must stay identical for past days. Change it only from a future date, and make the same change in `index.html`, `.github/workflows/leaderboard.yml` and `.github/scripts/daily-overall.js`.
- **Every merge to `main` bumps the build number** shown on the title screen: raise `APP_ITER.n` in `index.html` (the number after the dot, 7.1 → 7.2 → …). A new course makes the course count go up and the number after the dot restart at 0 (set `APP_ITER.courses` to the new count and `n` to 0).
