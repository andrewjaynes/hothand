"""Full hot hand analysis for Duke 2025-26 field goals.

Usage: python scripts/analysis.py data/duke_fga_2025_26.csv results/

Outputs (in the results folder):
  shuffle_tests.csv     D_k, shuffled-null mean, p-values for each shooter and k
  stratified_tests.csv  same test, shuffling only among shots of the same type (2 vs 3)
  markov_models.csv     order 0-3 Markov chains: log-likelihood, LRT p-value, held-out log loss
  power.csv             how often the test catches a simulated hot hand of a given size
  shot_selection.csv    share of next shots that are 3s after makes vs. misses
"""
import sys
import os
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(2026)
N_SHUFFLES = 10_000
MIN_FGA = 90
KS = (1, 2, 3)


# ---------- helpers ----------

def to_matrix(df, value='made', group='game_id'):
    """One row per game, shots in order, padded with -1."""
    games = [g[value].to_numpy() for _, g in df.groupby(group, sort=False)]
    L = max(len(g) for g in games)
    M = np.full((len(games), L), -1, dtype=np.int8)
    for i, g in enumerate(games):
        M[i, :len(g)] = g
    return M


def streak_counts(M, k):
    """M: (..., G, L) with -1 padding. Returns made-after-k-makes etc. summed over games."""
    L = M.shape[-1]
    nxt = M[..., k:]
    all_make = np.ones(nxt.shape, dtype=bool)
    all_miss = np.ones(nxt.shape, dtype=bool)
    for j in range(1, k + 1):
        prev = M[..., k - j:L - j]
        all_make &= prev == 1
        all_miss &= prev == 0
    valid = nxt >= 0
    am = (all_make & valid).sum(axis=(-2, -1))
    bm = (all_make & (nxt == 1)).sum(axis=(-2, -1))
    af = (all_miss & valid).sum(axis=(-2, -1))
    bf = (all_miss & (nxt == 1)).sum(axis=(-2, -1))
    return am, bm, af, bf


def D(M, k):
    am, bm, af, bf = streak_counts(M, k)
    with np.errstate(invalid='ignore', divide='ignore'):
        return bm / am - bf / af


def shuffle(M, strata, n):
    """n shuffled copies of M. Makes/misses are permuted only among positions
    in the same game and the same stratum. Padding (stratum 9) stays put."""
    G, L = M.shape
    strata = strata.astype(np.int64)
    pos = np.arange(L)
    ord_pos = np.argsort(strata * 10_000 + pos, axis=1, kind='stable')
    out = np.empty((n, G, L), dtype=np.int8)
    for s in range(n):
        keys = strata * 10.0 + rng.random((G, L))
        ord_rand = np.argsort(keys, axis=1)
        vals = np.take_along_axis(M, ord_rand, axis=1)
        new = np.empty_like(M)
        np.put_along_axis(new, ord_pos, vals, axis=1)
        out[s] = new
    return out


def shuffle_test(M, strata, n=N_SHUFFLES):
    sims = shuffle(M, strata, n)
    rows = []
    for k in KS:
        obs = D(M, k)
        null = D(sims, k)
        null = null[~np.isnan(null)]
        am, bm, af, bf = streak_counts(M, k)
        rows.append(dict(k=k, after_makes=bm / am if am else np.nan, n_after_makes=am,
                         after_misses=bf / af if af else np.nan, n_after_misses=af,
                         D_obs=obs, D_null_mean=null.mean(), D_adjusted=obs - null.mean(),
                         p_hot=(np.sum(null >= obs) + 1) / (len(null) + 1),
                         p_cold=(np.sum(null <= obs) + 1) / (len(null) + 1)))
    return rows


def holm(p):
    p = np.asarray(p)
    order = np.argsort(p)
    adj = np.empty_like(p)
    running = 0
    for rank, i in enumerate(order):
        running = max(running, (len(p) - rank) * p[i])
        adj[i] = min(1, running)
    return adj


# ---------- Markov chains ----------

def markov_table(seqs, max_order=3):
    """Shots with at least max_order earlier shots in the same game, so every
    order is fit and scored on exactly the same shots."""
    rows = []
    for s in seqs:
        for i in range(max_order, len(s)):
            rows.append((s[i], tuple(s[i - max_order:i])))
    return rows


def loglik(train, test, order, smooth=0.0):
    counts = {}
    for y, h in train:
        key = h[len(h) - order:] if order else ()
        c = counts.setdefault(key, [0, 0])
        c[0] += y
        c[1] += 1
    ll = 0.0
    for y, h in test:
        key = h[len(h) - order:] if order else ()
        m, n = counts.get(key, [0, 0])
        p = (m + smooth) / (n + 2 * smooth) if n + 2 * smooth > 0 else 0.5
        p = min(max(p, 1e-9), 1 - 1e-9)
        ll += np.log(p) if y else np.log(1 - p)
    return ll


def markov_compare(df):
    by_game = [g.made.tolist() for _, g in df.groupby('game_id', sort=False)]
    tabs = [markov_table([s]) for s in by_game]
    allrows = [r for t in tabs for r in t]
    out = {'n_scored': len(allrows)}
    ll0 = loglik(allrows, allrows, 0)
    for order in (0, 1, 2, 3):
        ll = loglik(allrows, allrows, order)
        out[f'll_order{order}'] = ll
        if order:
            out[f'lrt_p_order{order}'] = stats.chi2.sf(2 * (ll - ll0), 2 ** order - 1)
        # leave one game out, add-one smoothing
        cv = 0.0
        for i, t in enumerate(tabs):
            if not t:
                continue
            train = [r for j, tt in enumerate(tabs) if j != i for r in tt]
            cv += loglik(train, t, order, smooth=1.0)
        out[f'cv_logloss_order{order}'] = -cv / len(allrows)
    out['best_cv_order'] = int(np.argmin([out[f'cv_logloss_order{o}'] for o in range(4)]))
    return out


# ---------- power ----------

def simulate_chain(game_lengths, p, delta, n_sims):
    """Order-1 hot hand shooter: P(make|make) - P(make|miss) = delta,
    long-run make rate p (stationary prob b / (1 - a + b) = p)."""
    b = p * (1 - delta)
    a = b + delta
    G, L = len(game_lengths), max(game_lengths)
    M = np.full((n_sims, G, L), -1, dtype=np.int8)
    for g, n in enumerate(game_lengths):
        cur = (rng.random(n_sims) < p).astype(np.int8)
        M[:, g, 0] = cur
        for i in range(1, n):
            prob = np.where(cur == 1, a, b)
            cur = (rng.random(n_sims) < prob).astype(np.int8)
            M[:, g, i] = cur
    return M


def power(df, deltas=(0.0, 0.05, 0.10, 0.15, 0.20), n_sims=300, n_shuf=1000, alpha=0.05):
    lengths = df.groupby('game_id').size().tolist()
    p = df.made.mean()
    rows = []
    for delta in deltas:
        fake = simulate_chain(lengths, p, delta, n_sims)
        hits = 0
        for s in range(n_sims):
            M = fake[s]
            strata = np.where(M >= 0, 0, 9)
            null = D(shuffle(M, strata, n_shuf), 1)
            null = null[~np.isnan(null)]
            obs = D(M, 1)
            pval = (np.sum(null >= obs) + 1) / (len(null) + 1)
            hits += pval < alpha
        rows.append(dict(delta=delta, power=hits / n_sims))
    return rows


# ---------- main ----------

def main(csv, outdir):
    os.makedirs(outdir, exist_ok=True)
    f = pd.read_csv(csv).sort_values(['date', 'game_id', 'play_number'])
    shooters = f.player.value_counts()
    shooters = shooters[shooters >= MIN_FGA].index.tolist()

    # 1. shuffle tests: players + team
    rows, strat_rows = [], []
    for name in shooters + ['Duke (team)']:
        d = f if name == 'Duke (team)' else f[f.player == name]
        M = to_matrix(d)
        plain = np.where(M >= 0, 0, 9)
        for r in shuffle_test(M, plain):
            rows.append(dict(shooter=name, fga=len(d), fg_pct=d.made.mean(), **r))
        if name != 'Duke (team)':
            T = to_matrix(d, value='three_pointer')
            typed = np.where(M >= 0, T, 9)
            for r in shuffle_test(M, typed):
                strat_rows.append(dict(shooter=name, **r))
        print('shuffled', name, flush=True)
    res = pd.DataFrame(rows)
    players = res.shooter != 'Duke (team)'
    res.loc[players, 'p_hot_holm'] = holm(res.loc[players, 'p_hot'])
    res.loc[players, 'p_cold_holm'] = holm(res.loc[players, 'p_cold'])
    res.to_csv(f'{outdir}/shuffle_tests.csv', index=False)
    strat = pd.DataFrame(strat_rows)
    strat['p_hot_holm'] = holm(strat.p_hot)
    strat['p_cold_holm'] = holm(strat.p_cold)
    strat.to_csv(f'{outdir}/stratified_tests.csv', index=False)

    # 2. Markov chain comparison
    mk = [dict(shooter=n, **markov_compare(f[f.player == n])) for n in shooters]
    pd.DataFrame(mk).to_csv(f'{outdir}/markov_models.csv', index=False)
    print('markov done', flush=True)

    # 3. power for the two highest-volume shooters and a ~200-shot shooter
    pw = []
    for name in [shooters[0], shooters[1], 'Cayden Boozer']:
        for r in power(f[f.player == name]):
            pw.append(dict(shooter=name, fga=int((f.player == name).sum()), **r))
        print('power', name, flush=True)
    pd.DataFrame(pw).to_csv(f'{outdir}/power.csv', index=False)

    # 4. shot selection: is the next shot more often a 3 after makes?
    sel = []
    for name in shooters:
        d = f[f.player == name]
        prev = d.groupby('game_id').made.shift(1)
        nxt3 = d.three_pointer
        a, b = nxt3[prev == 1], nxt3[prev == 0]
        table = [[a.sum(), len(a) - a.sum()], [b.sum(), len(b) - b.sum()]]
        sel.append(dict(shooter=name, three_rate_after_make=a.mean(), n_after_make=len(a),
                        three_rate_after_miss=b.mean(), n_after_miss=len(b),
                        fisher_p=stats.fisher_exact(table)[1]))
    pd.DataFrame(sel).to_csv(f'{outdir}/shot_selection.csv', index=False)
    print('done')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
