# Hot Hand at Duke: Project Summary

## Topic

Did Duke men's basketball players have a "hot hand" in 2025-26? Using all 2,197 Duke field goal attempts from 38 games, we tested whether a player who had just made one, two, or three straight shots was more likely to make the next one, for the nine players with 90+ attempts and for the team. Null hypothesis: within a game, each shot is independent of earlier shots.

## Mathematical meat

**From class.** Our statistic is a difference of conditional probabilities, D_k = P(make | k straight makes) - P(make | k straight misses), for k = 1, 2, 3. A hot hand means D_k > 0. We modeled each shooter as a Markov chain whose state is his last k shots and compared the estimated transition matrix to the independent model, where every row is the same. The 2-state chain's stationary make rate, b / (1 - a + b) with a = P(make | make) and b = P(make | miss), shows a streaky shooter and an independent one can share the same FG%, so season percentages can't settle it.

**Beyond class.** A permutation test (10,000 within-game shuffles of each player's makes and misses) gave the null distribution of D_k. Likelihood ratio tests and leave-one-game-out cross-validation compared Markov chains of order 0 to 3. Power simulations used Markov chains with a built-in hot hand, and a Holm correction covered our 27 player tests.

## Why it is mathematically rich

Just checking D_k > 0 is biased, and the bias differs by player. Miller and Sanjurjo (2018) proved that in short independent sequences, the make rate right after a streak is expected to fall below the true rate. Pooling games pushes the other way, since good nights bring both streaks and makes. Under shuffling, D_3 averaged +0.066 for Boozer and -0.055 for Evans, so comparing to 0 misleads both ways.

## Results

- **No player had a significant hot hand** (all Holm-corrected p = 1.0). Cameron Boozer's .612 after three makes (vs. .500 after three misses) is just 0.046 above the shuffled baseline (p = 0.29).
- **Cold, not hot.** Isaiah Evans hit 5 of 22 after three makes (raw p = 0.009, Holm p = 0.24).
- **No team momentum.** Duke shot .480 after a make vs. .499 after a miss (p = 0.79).
- **Independent model wins** on held-out games for 6 of 9 players; no likelihood ratio test survived correction.
- **Power is limited.** A hot hand worth 10 percentage points would be caught 64% of the time for Boozer (522 shots) but 32% for a 210-shot player.
- **Shot selection shifts.** After a make, Caleb Foster's next shot was a three 52% of the time vs. 32% after a miss (Fisher p = 0.005), and Ngongba and Khamenia shifted similarly. Shuffling 2s and 3s separately still found no hot hand.

## Conclusion

We found no evidence of a hot hand at Duke in 2025-26, for any player or for the team. That isn't proof it doesn't exist: a hot hand of 15 percentage points or more would very likely have shown up for our two top shooters (87-91% power), but a smaller one could hide in one season. Still, several players took more threes after a make, acting as if they believe in a hot hand their results don't show.

*AI disclosure: We used Claude (Anthropic) to write our data cleaning and analysis code.*
