# Data

## duke_fga_2025_26.csv

Every Duke field goal attempt from the 2025-26 season, one row per shot, in game order. 38 games (Nov 4, 2025 vs. Texas through Mar 29, 2026 vs. UConn), 2,197 attempts.

Source: ESPN play-by-play via the sportsdataverse hoopR dataset (https://github.com/sportsdataverse/hoopR-mbb-data, file `mbb/pbp/parquet/play_by_play_2026.parquet`). Free throws are excluded.

Checked against the official box scores: attempts and makes match for every player except Dame Sarr, who has 207 attempts here vs. 208 in the box score.

| Column | Meaning |
| --- | --- |
| game_id | ESPN game id |
| date | Game date |
| opponent | Opponent name |
| home | True if Duke was the home team |
| season_type | 2 = regular season, 3 = postseason |
| play_number | Order of the play within the game (use this to sort) |
| half | 1 or 2 (3+ = overtime) |
| clock | Game clock when the shot happened |
| game_seconds_remaining | Seconds left in regulation at the start of the play |
| player_id, player | Shooter |
| shot_type | JumpShot, LayUpShot, DunkShot, TipShot |
| three_pointer | 1 if a 3-point attempt |
| made | 1 = make, 0 = miss |
| x, y | ESPN court coordinates (check orientation before computing shot distance) |
| team_shot_num_in_game | 1st, 2nd, ... Duke attempt in that game |
| player_shot_num_in_game | 1st, 2nd, ... attempt by that player in that game |
| description | ESPN's play text |

Streaks should be computed within a game only (group by `game_id`, sort by `play_number`).

## summary_conditional_probs.csv

Raw make rates after 1, 2 and 3 straight makes or misses, for the team and every player with 90+ attempts. These are not bias-corrected; compare them to the shuffled baseline, not to the season FG%.

## Rebuilding

```
pip install pandas pyarrow
python scripts/build_dataset.py <path to hoopR-mbb-data checkout> data/duke_fga_2025_26.csv
python scripts/summary.py data/duke_fga_2025_26.csv data/summary_conditional_probs.csv
python scripts/shuffle_test_preview.py data/duke_fga_2025_26.csv
```

`shuffle_test_preview.py` is a quick first pass (2,000 within-game shuffles for two players), not the final analysis.
