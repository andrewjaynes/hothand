# hothand

Is the hot hand real at Duke? Final project for Discrete Math and Proofs, Fall 2026.

We test whether Duke men's basketball players shot better after a run of makes during the 2025-26 season than their overall percentage predicts. The null hypothesis is that every field goal attempt is independent of the ones before it. We compare each player's real streak behavior to thousands of shuffled versions of his season, and we build Markov chain models where the state is a player's last few shots.

**Result:** no player and no team-level hot hand, after comparing each player to 10,000 shuffled versions of his own season. Several players did take more threes right after a make. The 1-page summary with all the numbers is in [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md), and the original plan is in [PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md).

## What's in the repo

```
PROJECT_SUMMARY.md              1-page summary with final results (due Dec 2)
PROJECT_DESCRIPTION.md          topic, approach, early results, check-in questions
project_meeting_notes           notes from our chat about the project
data/
  duke_fga_2025_26.csv          every Duke field goal attempt in 2025-26, in shot order
  summary_conditional_probs.csv make rates after 1, 2, 3 straight makes or misses
  README.md                     column definitions and how the data was checked
scripts/
  build_dataset.py              builds the CSV from the raw play-by-play
  summary.py                    builds the summary table
  shuffle_test_preview.py       quick within-game shuffle test for two players
  analysis.py                   full analysis: shuffle tests, Markov models, power, shot selection
results/
  shuffle_tests.csv             D_k, shuffled baseline, p-values (raw and Holm) per shooter and k
  stratified_tests.csv          same test, shuffling 2s and 3s separately
  markov_models.csv             order 0-3 chains: likelihood ratio tests, held-out log loss
  power.csv                     detection rate for simulated hot hands of size 0 to 0.20
  shot_selection.csv            share of next shots that are 3s after makes vs. misses
```

## The data

2,197 field goal attempts across all 38 games, from Nov 4, 2025 (Texas) through Mar 29, 2026 (UConn, Elite Eight). Free throws are not included.

It comes from ESPN play-by-play, packaged by [sportsdataverse/hoopR-mbb-data](https://github.com/sportsdataverse/hoopR-mbb-data). Per-player attempts and makes match the official box scores, except for one Dame Sarr attempt (207 here vs. 208).

If you only want to analyze the shots, you don't need to rebuild anything. Load the CSV:

```python
import pandas as pd

shots = pd.read_csv("data/duke_fga_2025_26.csv")
shots = shots.sort_values(["date", "game_id", "play_number"])

# one make/miss sequence per player per game
seqs = shots.groupby(["player", "game_id"])["made"].apply(list)
```

Always count streaks within a game. A make at the end of one game should not carry into the next.

## Running the scripts

Requires Python 3 with pandas, numpy, scipy, and pyarrow.

```
pip install pandas numpy scipy pyarrow

python scripts/analysis.py data/duke_fga_2025_26.csv results   # about 2 minutes

python scripts/summary.py data/duke_fga_2025_26.csv data/summary_conditional_probs.csv
python scripts/shuffle_test_preview.py data/duke_fga_2025_26.csv
```

To rebuild the CSV from scratch, first get `mbb/pbp/parquet/play_by_play_2026.parquet` from the hoopR-mbb-data repo (about 90 MB), then:

```
python scripts/build_dataset.py <path to hoopR-mbb-data> data/duke_fga_2025_26.csv
```

## Still to do

- [x] Full shuffle test (10,000 shuffles) for every player with 90+ attempts, k = 1, 2, 3
- [x] Fit order 1, 2, and 3 Markov chains and compare them to the independent model
- [x] Simulate shooters with a built-in hot hand to measure the test's power
- [x] Check whether shot selection (3s vs. 2s) changes after makes
- [x] Correct for multiple comparisons
- [ ] Charts for the poster
- [ ] ~3 page write-up
- [ ] Optional: shot distance from court coordinates as another difficulty control

## Deadlines

| Date | What's due |
| --- | --- |
| Nov 12 or 13 | Check-in meeting with Tori |
| Nov 20, Dec 2 | In-class work days |
| Dec 2, 11:59pm | 1-page project summary |
| Dec 4, 1:00pm | Poster images/PDF and ~3 page write-up on Gradescope |
| Dec 4, in class | Poster session, Gross Hall 330 |
| Dec 2 to Dec 8 | Final meeting with Tori |

## References

- Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology, 17*(3), 295–314.
- Miller, J. B., & Sanjurjo, A. (2018). Surprised by the hot hand fallacy? A truth in the law of small numbers. *Econometrica, 86*(6), 2019–2047. https://doi.org/10.3982/ECTA14943
