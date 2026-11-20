# Is the Hot Hand Real at Duke? Project Description

## Topic and problem

We are testing whether Duke men's basketball players had a "hot hand" in the 2025-26 season: after making shots, was a player more likely to make the next one than his overall percentage would predict?

Our null hypothesis is that each field goal attempt is independent of the ones before it, so a player's shots behave like flips of a weighted coin with his season FG% as the weight. We test this for individual high-volume shooters and for the team as a whole, using every Duke field goal attempt from all 38 games.

## Data

We have all 2,197 Duke field goal attempts from the 2025-26 season, in the order they were taken, across 38 games (Nov 4 vs. Texas through the Elite Eight loss to UConn on Mar 29).

- **Source:** ESPN play-by-play, collected by the open-source [hoopR / sportsdataverse](https://github.com/sportsdataverse/hoopR-mbb-data) project.
- **Check:** per-player attempts and makes match the official box scores. The only gap is one Dame Sarr attempt (207 vs. 208), out of 2,198 total.
- **Fields per shot:** game, date, opponent, half, game clock, shooter, made/missed, 2 or 3 pointer, shot type (jumper, layup, dunk, tip), court coordinates, and shot number within the game.
- **Excluded:** free throws. They are cleaner but too few per player for long streaks, so we use all field goals as a team decision.

Streaks are counted only within a game. A make at the end of one game does not carry into the next.

See [`data/README.md`](data/README.md) for the full column list.

## Mathematical approach

Our test statistic for each player is the gap between his make rate after k straight makes and after k straight misses, for k = 1, 2, 3:

```math
D_k = \hat{P}(\text{make} \mid k \text{ makes}) - \hat{P}(\text{make} \mid k \text{ misses})
```

A hot hand means D_k > 0. To decide whether an observed D_k is bigger than chance, we compare it to simulated data.

1. **Independent baseline (null).** For each player, shuffle his makes and misses within each game, keeping the number of shots and makes per game fixed. Recompute D_k. Repeat 10,000 times to get the null distribution.
2. **p-value.** The fraction of shuffled seasons with D_k at least as large as the real one.
3. **Markov models.** Model each player as a Markov chain whose state is his last k shots (2 states for k = 1, 4 for k = 2, 8 for k = 3). We estimate the transition matrix from the data and compare it to the independent model, where every row of the matrix is the same.
4. **Dependent simulations.** Generate fake shooters from Markov chains with a built-in hot hand (for example, a 5 percentage point boost after a make) and run the same test. This tells us how often our test would catch a real effect of that size with this many shots, which is the test's power.

For the 2-state chain, with a = P(make | make) and b = P(make | miss), the long-run make rate is the stationary probability

```math
\pi_{\text{make}} = \frac{b}{1 - a + b}
```

so a hot-hand chain and an independent shooter can share the same FG% while producing very different streaks. That is why season percentages alone cannot answer the question.

## Why this is mathematically rich

The naive test (is D_k bigger than 0?) is wrong, and showing why is a core part of our project.

- **Streak selection bias.** Miller and Sanjurjo (2018) proved that in a finite sequence of independent shots, the observed make rate right after a streak of makes is expected to fall below the true percentage. This pulls the null value of D_k below 0, and it is the main reason the original 1985 "no hot hand" result has been re-examined.
- **Pooling across games.** Combining games can push the other way. On nights a player shoots well, he has both more streaks and more makes, which can inflate D_k even when shots are independent within each game.
- **Our data shows both.** In a first run of 2,000 shuffles, the null average of D_3 was about +0.07 for Cameron Boozer and about -0.06 for Isaiah Evans. Comparing to the simulated baseline instead of to 0 handles both effects.
- **Shot difficulty.** A player who just made a few shots may take harder ones (more threes, deeper jumpers), which would hide a real hot hand. We have shot type and court coordinates, so we can check whether shot selection changes after makes and compare results for 2s and 3s.
- **Comparing models.** Independent vs. order 1, 2 and 3 Markov chains, judged by how well each predicts held-out games.

## First look at the data

Raw numbers point in different directions for different players, and most streak samples are small. Cameron Boozer looks "hot" and Isaiah Evans looks "cold," but neither result holds up yet once compared to the shuffled baseline.

| Shooter | FGA | FG% | After 1 make | After 1 miss | After 3 makes | After 3 misses |
| --- | --- | --- | --- | --- | --- | --- |
| Duke (team) | 2,197 | .491 | .480 (n=1,055) | .499 (n=1,104) | .519 (n=233) | .494 (n=269) |
| Cameron Boozer | 522 | .556 | .557 (n=264) | .555 (n=220) | .612 (n=67) | .500 (n=42) |
| Isaiah Evans | 430 | .433 | .438 (n=169) | .435 (n=223) | .227 (n=22) | .551 (n=49) |
| Caleb Foster | 226 | .447 | .412 (n=85) | .481 (n=108) | .286 (n=7) | .476 (n=21) |
| Cayden Boozer | 210 | .500 | .471 (n=87) | .570 (n=86) | .200 (n=15) | .545 (n=11) |
| Dame Sarr | 207 | .406 | .356 (n=73) | .406 (n=96) | .400 (n=5) | .600 (n=20) |
| Patrick Ngongba II | 188 | .606 | .559 (n=93) | .635 (n=63) | .438 (n=16) | .833 (n=6) |
| Nikolas Khamenia | 169 | .444 | .435 (n=62) | .471 (n=70) | .444 (n=9) | .500 (n=4) |
| Maliq Brown | 132 | .629 | .619 (n=63) | .606 (n=33) | .455 (n=11) | .500 (n=2) |

n = number of shots that followed that streak, within the same game. The team row treats every Duke shot as one sequence, regardless of shooter.

Preliminary shuffle test (2,000 shuffles, one-sided p-value for a hot hand): Cameron Boozer D_3 = +0.112 vs. a null average of +0.068, p ≈ 0.30. Isaiah Evans D_3 = -0.324 vs. -0.056, p ≈ 0.99 for hot, which suggests a possible cold-hand pattern worth a closer look.

## Hypothesized conclusion and limitations

We expect no statistically significant hot hand for most Duke players in 2025-26. Our power simulations should show how large an effect we could have detected, so "no evidence" can be stated precisely rather than read as "no hot hand."

- **Sample size.** Even the highest-volume shooter has only 67 shots after three straight makes.
- **Shot difficulty.** Play-by-play doesn't record defender distance, so shot location and type are our only controls.
- **Many tests.** Testing nine shooters at three values of k raises the chance of a false positive, so we will adjust for multiple comparisons.
- **Team sequence.** Consecutive team shots come from different players, so a team-level result measures something closer to momentum than to an individual hot hand.

## Questions for our check-in with Tori

- Is shuffling within games the right null, or should we simulate from a fixed season FG% like the free throw example from class?
- Is it enough to explain the Miller-Sanjurjo bias with our own simulations, or should we also present part of the proof?
- How should we judge which Markov model fits best: held-out prediction, a likelihood ratio test, or both?
- Should the poster focus on a few players in depth, or cover the whole roster?

## References

- Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology, 17*(3), 295–314.
- Miller, J. B., & Sanjurjo, A. (2018). Surprised by the hot hand fallacy? A truth in the law of small numbers. *Econometrica, 86*(6), 2019–2047. <https://doi.org/10.3982/ECTA14943>
- sportsdataverse. (2026). *hoopR-mbb-data: Men's college basketball play-by-play, 2025-26 season* [Data set]. <https://github.com/sportsdataverse/hoopR-mbb-data>
