#!/bin/bash
# resumable download of the LiDAR tiles, three at a time, backing off when the server says 429
cd "$(dirname "$0")"; B=https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/CO_CONMGaps_D24/CO_CONMGaps_1_D24/LAZ
get() { t=$1; for i in $(seq 1 60); do curl -sS -f -m 3000 -C - -A "Mozilla/5.0 (X11; Linux x86_64) SweetSpot-course-builder" -o laz/$t.laz $B/USGS_LPC_CO_CONMGaps_D24_13SDC$t.laz && { echo done $t; return; }; sleep $((15 + i)); done; echo gaveup $t; }
export -f get; export B
printf '%s\n' 8458 8457 8557 8558 8556 8657 8656 8456 8658 | xargs -P 6 -I{} bash -c 'get {}'
