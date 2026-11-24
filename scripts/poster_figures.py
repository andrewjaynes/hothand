"""Poster figures for the Duke hot hand project.

Usage: python scripts/poster_figures.py data/duke_fga_2025_26.csv results poster

Every figure is saved as PNG (300 dpi) and PDF, sized to print on letter paper
in landscape (10 x 7.5 in leaves a 0.5 in margin) unless noted.
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

sys.path.insert(0, os.path.dirname(__file__))
import analysis as A

# ---------- style ----------
NAVY = '#012169'      # Duke navy: headings, text accents
BLUE = '#00539B'      # Duke royal blue: main data color
ORANGE = '#E0662C'    # highlight: the real (observed) value
GRAY = '#8E8C85'      # chance / shuffled baseline
LIGHT = '#D9D8D3'     # chance bands, gridlines
INK = '#1B1B1B'
INK2 = '#55534E'
BG = 'white'

plt.rcParams.update({
    'font.family': 'Inter',
    'font.size': 13,
    'axes.edgecolor': LIGHT,
    'axes.labelcolor': INK2,
    'axes.titlecolor': INK,
    'xtick.color': INK2,
    'ytick.color': INK2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'savefig.facecolor': BG,
    'mathtext.fontset': 'dejavusans',
})

W, H = 10, 7.5


def title(fig, main, sub=None, y=None):
    h = fig.get_size_inches()[1]
    if y is None:
        y = 1 - 0.35 / h
    fig.text(0.055, y, main, fontsize=24, fontweight='bold', color=NAVY, ha='left', va='top')
    if sub:
        fig.text(0.055, y - 0.5 / h, sub, fontsize=13.5, color=INK2, ha='left', va='top', linespacing=1.35)


def save(fig, out, name):
    fig.savefig(f'{out}/{name}.png', dpi=300)
    fig.savefig(f'{out}/{name}.pdf')
    plt.close(fig)
    print('saved', name)


def short(name):
    return {'Patrick Ngongba II': 'Patrick Ngongba II'}.get(name, name)


# ---------- data helpers ----------

def null_draws(d, k_list=(1, 2, 3), n=10_000):
    M = A.to_matrix(d)
    strata = np.where(M >= 0, 0, 9)
    sims = A.shuffle(M, strata, n)
    out = {}
    for k in k_list:
        null = A.D(sims, k)
        out[k] = (float(A.D(M, k)), null[~np.isnan(null)])
    return out


# ---------- 1. shot strip ----------

def fig_shot_strip(f, out):
    g = f[(f.player == 'Cameron Boozer') & (f.opponent.str.contains('Boston College'))]
    seq = g.made.tolist()
    fig = plt.figure(figsize=(W, 4.2))
    title(fig, 'What a streak looks like',
          'Cameron Boozer\'s 17 shots vs. Boston College (Feb 3, 2026), in order')
    ax = fig.add_axes([0.04, 0.02, 0.92, 0.66])
    ax.set_xlim(-0.8, len(seq) - 0.2)
    ax.set_ylim(-1.6, 1.4)
    ax.set_aspect('equal')
    ax.axis('off')
    for i, m in enumerate(seq):
        if m:
            ax.add_patch(Circle((i, 0), 0.36, color=BLUE))
        else:
            ax.add_patch(Circle((i, 0), 0.36, facecolor='white', edgecolor=BLUE, lw=2.2))
    # bracket the hot and cold runs
    def bracket(a, b, text, color):
        ax.plot([a - 0.35, a - 0.35, b + 0.35, b + 0.35], [-0.55, -0.7, -0.7, -0.55], color=color, lw=2)
        ax.text((a + b) / 2, -1.0, text, ha='center', va='top', fontsize=13, color=color, fontweight='semibold')
    bracket(0, 4, '5 straight makes', ORANGE)
    bracket(9, 13, '5 straight misses', GRAY)
    ax.annotate('', xy=(5, 0.5), xytext=(4.25, 0.95),
                arrowprops=dict(arrowstyle='->', color=INK2, lw=1.4, connectionstyle='arc3,rad=-0.3'))
    ax.text(3.3, 1.05, 'Is this shot more likely to go in?', fontsize=12.5, color=INK2, ha='center', va='bottom')
    # legend
    lx = len(seq) - 3.6
    ax.add_patch(Circle((lx, 1.0), 0.2, color=BLUE))
    ax.text(lx + 0.35, 1.0, 'make', va='center', fontsize=12, color=INK2)
    ax.add_patch(Circle((lx + 1.9, 1.0), 0.2, facecolor='white', edgecolor=BLUE, lw=2))
    ax.text(lx + 2.25, 1.0, 'miss', va='center', fontsize=12, color=INK2)
    save(fig, out, '01_shot_strip')


# ---------- 2. data at a glance ----------

def fig_data_stats(f, out):
    fig = plt.figure(figsize=(W, 3.2))
    stats = [('2,197', 'field goal attempts'), ('38', 'games, Nov 4 to Mar 29'),
             ('9', 'players with 90+ attempts')]
    for i, (num, lab) in enumerate(stats):
        x = 0.055 + i * 0.315
        fig.text(x, 0.64, num, fontsize=54, fontweight='bold', color=NAVY, va='center')
        fig.text(x, 0.37, lab, fontsize=15, color=INK2, va='center')
    fig.text(0.055, 0.08, 'Source: ESPN play-by-play via sportsdataverse/hoopR. Matches official box scores.',
             fontsize=11.5, color=GRAY)
    save(fig, out, '02_data_stats')


# ---------- 5. why not compare to zero ----------

def fig_null_hist(nulls, official, out):
    fig = plt.figure(figsize=(W, H))
    title(fig, 'The "no hot hand" baseline isn\'t zero',
          'D₃ for 10,000 shuffled seasons (same shots, makes randomly reordered within each game).\n'
          'Comparing the real value to 0 would mislead in opposite directions for these two players.')
    kx, ky = 0.055, 0.775
    for lab, c, ls, lw in [('Real season', ORANGE, '-', 3), ('Chance (average of shuffles)', GRAY, '-', 2.4),
                           ('Naive baseline of 0', INK2, (0, (4, 3)), 1.4)]:
        fig.add_artist(plt.Line2D([kx, kx + 0.03], [ky, ky], color=c, lw=lw, ls=ls))
        fig.text(kx + 0.038, ky, lab, fontsize=12, color=INK2, va='center')
        kx += 0.06 + len(lab) * 0.0095
    for j, name in enumerate(['Cameron Boozer', 'Isaiah Evans']):
        obs, null = nulls[name][3]
        off = official.loc[(name, 3)]
        ax = fig.add_axes([0.075 + j * 0.48, 0.12, 0.4, 0.55])
        bins = np.linspace(-0.6, 0.6, 49)
        ax.hist(null, bins=bins, color=LIGHT, edgecolor='white', linewidth=0.8)
        top = ax.get_ylim()[1]
        yl = top * 1.28           # label height; real and chance lines rise to meet their labels
        ax.plot([0, 0], [0, top * 1.06], color=INK2, lw=1.4, ls=(0, (4, 3)))
        ax.plot([off.D_null_mean] * 2, [0, yl + top * 0.06], color=GRAY, lw=2.4)
        ax.plot([obs] * 2, [0, yl + top * 0.06], color=ORANGE, lw=3)
        ax.set_ylim(0, top * 1.4)
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.set_xlim(-0.6, 0.6)
        ax.set_xticks([-0.5, -0.25, 0, 0.25, 0.5])
        ax.set_xticklabels(['-0.50', '-0.25', '0', '+0.25', '+0.50'])
        ax.set_xlabel('D₃ = P(make | 3 makes) − P(make | 3 misses)', fontsize=11.5)
        real_right = obs > off.D_null_mean   # put each label on the outer side of its own line
        ax.text(obs + (0.015 if real_right else -0.015), yl, f'Real\n{obs:+.3f}', color=ORANGE, fontsize=12.5,
                fontweight='bold', ha='left' if real_right else 'right', va='center', linespacing=1.1)
        ax.text(off.D_null_mean + (-0.015 if real_right else 0.015), yl, f'Chance\n{off.D_null_mean:+.3f}',
                color=GRAY, fontsize=12.5, fontweight='bold', ha='right' if real_right else 'left', va='center',
                linespacing=1.1)
        ax.set_title(f'{name}', fontsize=17, fontweight='bold', color=INK, loc='left', pad=10)
        ax.text(1.0, 1.035, f'p (hot) = {off.p_hot:.2f}', transform=ax.transAxes, ha='right', va='bottom',
                fontsize=12.5, color=INK2)
    save(fig, out, '05_baseline_not_zero')


# ---------- 6. effect sizes vs chance ----------

def fig_effects(nulls, official, order, out):
    fig = plt.figure(figsize=(W, H))
    title(fig, 'No player shot hotter than chance',
          'Dot = real hot-hand effect: $D_k$ minus its shuffled baseline. Gray bar = middle 95% of\n'
          '10,000 shuffled seasons. A dot inside the bar is what chance alone produces.')
    rows = order + ['Duke (team)']
    y = np.arange(len(rows))[::-1].astype(float)
    y[-1] -= 0.6  # gap before team row
    for j, k in enumerate((1, 2, 3)):
        ax = fig.add_axes([0.27 + j * 0.245, 0.16, 0.21, 0.6])
        for yi, name in zip(y, rows):
            obs, null = nulls[name][k]
            if official.loc[(name, k)].n_after_makes < 5:
                ax.text(0, yi, f'too few shots (n = {int(official.loc[(name, k)].n_after_makes)})',
                        ha='center', va='center', fontsize=10.5, color=GRAY,
                        bbox=dict(facecolor='white', edgecolor='none', pad=1))
                continue
            m = official.loc[(name, k)].D_null_mean
            lo, hi = np.percentile(null, [2.5, 97.5]) - null.mean()
            ax.plot([lo, hi], [yi, yi], color=LIGHT, lw=9, solid_capstyle='round', zorder=1)
            eff = obs - m
            outside = eff < lo or eff > hi
            ax.scatter([eff], [yi], s=70, color=ORANGE if outside else BLUE, zorder=3,
                       edgecolor='white', linewidth=1.5)
        ax.axvline(0, color=INK2, lw=1, zorder=0)
        ax.set_xlim(-0.75, 0.75)
        ax.set_xticks([-0.5, 0, 0.5])
        ax.set_xticklabels(['−0.5', '0', '+0.5'])
        ax.set_ylim(min(y) - 0.7, max(y) + 0.7)
        ax.set_yticks(y if j == 0 else [])
        if j == 0:
            ax.set_yticklabels([short(r) for r in rows], fontsize=12.5, color=INK)
        ax.tick_params(axis='y', length=0)
        ax.spines['left'].set_visible(False)
        ax.set_title(f'k = {k}', fontsize=15, fontweight='bold', color=INK, pad=8)
        ax.set_xlabel('← colder      hotter →', fontsize=11)
    fig.text(0.055, 0.055, 'Orange: Isaiah Evans after 3 makes falls outside the bar on the cold side (raw p = 0.009),\n'
             'but not after correcting for 27 tests (Holm p = 0.24).',
             fontsize=11.5, color=INK2, va='center', linespacing=1.35)
    save(fig, out, '06_effects_vs_chance')


# ---------- 7. power ----------

def fig_power(res, out):
    pw = pd.read_csv(f'{res}/power.csv')
    fig = plt.figure(figsize=(W, H))
    title(fig, 'Big hot hands would show up. Small ones could hide.',
          'Share of simulated seasons with a built-in hot hand that our shuffle test flags (p < 0.05),\n'
          'using each player\'s real FG% and shots per game. 300 simulated seasons per point.')
    ax = fig.add_axes([0.1, 0.12, 0.66, 0.6])
    styles = {'Cameron Boozer': (NAVY, '-'), 'Isaiah Evans': (BLUE, '-'), 'Cayden Boozer': (GRAY, '-')}
    for name, (c, ls) in styles.items():
        d = pw[pw.shooter == name]
        x = d.delta * 100
        yv = d.power * 100
        ax.plot(x, yv, color=c, lw=3, ls=ls, marker='o', markersize=8, markeredgecolor='white', markeredgewidth=1.5)
        dy = {'Cameron Boozer': 7, 'Isaiah Evans': -7, 'Cayden Boozer': 0}[name]
        ax.text(20.6, yv.iloc[-1] + dy, f'{name}\n{int(d.fga.iloc[0])} shots', color=c, fontsize=12.5,
                fontweight='bold', va='center', ha='left', linespacing=1.15)
    ax.axhline(5, color=GRAY, lw=1.2, ls=(0, (4, 3)))
    ax.text(19.8, 7, 'False-alarm rate with no hot hand ≈ 5%', fontsize=11, color=INK2, ha='right')
    b = pw[(pw.shooter == 'Cameron Boozer') & (np.isclose(pw.delta, 0.10))].power.iloc[0] * 100
    ax.annotate(f'{b:.0f}%', xy=(10, b), xytext=(7.2, b + 12), fontsize=13, color=NAVY, fontweight='bold',
                arrowprops=dict(arrowstyle='-', color=NAVY, lw=1))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 100)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xticklabels(['0', '5', '10', '15', '20'])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlabel('Size of hot hand: P(make | make) − P(make | miss), percentage points')
    ax.set_ylabel('Chance our test catches it')
    ax.grid(axis='y', color=LIGHT, lw=0.8)
    ax.set_axisbelow(True)
    save(fig, out, '07_power')


# ---------- 8. shot selection ----------

def fig_shot_selection(res, out):
    s = pd.read_csv(f'{res}/shot_selection.csv')
    s['diff'] = s.three_rate_after_make - s.three_rate_after_miss
    s = s.sort_values('diff')
    fig = plt.figure(figsize=(W, H))
    title(fig, 'After a make, players reach for more threes',
          'Share of a player\'s next shot that was a three-pointer, after a miss vs. after a make.\n'
          'Orange: difference significant at p < 0.05 (Fisher\'s exact test).')
    ax = fig.add_axes([0.27, 0.12, 0.6, 0.6])
    y = np.arange(len(s))
    for yi, (_, r) in zip(y, s.iterrows()):
        sig = r.fisher_p < 0.05
        borderline = 0.05 <= r.fisher_p < 0.06
        c = ORANGE if sig else BLUE
        a, b = r.three_rate_after_miss * 100, r.three_rate_after_make * 100
        ax.plot([a, b], [yi, yi], color=c if sig else LIGHT, lw=3, zorder=1)
        ax.scatter([a], [yi], s=90, facecolor='white', edgecolor=c, linewidth=2.2, zorder=3)
        ax.scatter([b], [yi], s=90, color=c, zorder=3, edgecolor='white', linewidth=1.2)
        if sig or borderline:
            note = '  borderline' if borderline else ''
            ax.text(max(a, b) + 2.5, yi, f'{a:.0f}% → {b:.0f}%  (p = {r.fisher_p:.3f}{note})', va='center',
                    fontsize=11.5, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([short(n) for n in s.shooter], fontsize=12.5, color=INK)
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xlabel('Next shot is a three')
    ax.grid(axis='x', color=LIGHT, lw=0.8)
    ax.set_axisbelow(True)
    # key
    ax.scatter([3], [len(s) + 0.1], s=80, facecolor='white', edgecolor=BLUE, linewidth=2, clip_on=False)
    ax.text(5, len(s) + 0.1, 'after a miss', va='center', fontsize=11.5, color=INK2)
    ax.scatter([27], [len(s) + 0.1], s=80, color=BLUE, clip_on=False)
    ax.text(29, len(s) + 0.1, 'after a make', va='center', fontsize=11.5, color=INK2)
    ax.set_ylim(-0.7, len(s) + 0.5)
    save(fig, out, '08_shot_selection')


# ---------- 9. model comparison table ----------

def fig_models(res, order, out):
    m = pd.read_csv(f'{res}/markov_models.csv').set_index('shooter').loc[order]
    fig = plt.figure(figsize=(W, H))
    title(fig, 'The no-memory model predicts best',
          'Markov chains whose state is the last 0 to 3 shots, fit to each player. Held-out score = average\n'
          'log loss on games left out of fitting (lower is better). LRT = likelihood ratio test vs. order 0.')
    cols = ['Player', 'Shots\nscored', 'Best order\non held-out games', 'Smallest LRT p\n(order)', 'Significant\nafter Holm?']
    xs = [0.055, 0.36, 0.5, 0.7, 0.87]
    top = 0.71
    for x, c in zip(xs, cols):
        fig.text(x, top, c, fontsize=12, fontweight='bold', color=INK2, va='bottom', ha='left' if x < 0.3 else 'center'
                 if False else 'left')
    fig.add_artist(plt.Line2D([0.055, 0.95], [top - 0.012, top - 0.012], color=INK2, lw=1))
    rowh = 0.066
    for i, (name, r) in enumerate(m.iterrows()):
        yy = top - 0.05 - i * rowh
        ps = {o: r[f'lrt_p_order{o}'] for o in (1, 2, 3)}
        o_min = min(ps, key=ps.get)
        best = int(r.best_cv_order)
        vals = [short(name), f'{int(r.n_scored)}',
                'order 0 (independent)' if best == 0 else f'order {best}',
                f'{ps[o_min]:.3f}  ({o_min})', 'No']
        for x, v in zip(xs, vals):
            bold = (x == xs[2] and best == 0)
            fig.text(x, yy, v, fontsize=12.5, color=NAVY if bold else INK, fontweight='semibold' if bold else 'normal',
                     va='center')
        if i < len(m) - 1:
            fig.add_artist(plt.Line2D([0.055, 0.95], [yy - rowh / 2, yy - rowh / 2], color=LIGHT, lw=0.8))
    fig.text(0.055, 0.045, 'Shots scored = shots with at least 3 earlier shots in the same game, so every model is '
             'tested on the same shots.\nHolm correction across all 27 likelihood ratio tests (9 players × orders 1, 2, 3).',
             fontsize=10.5, color=INK2, va='center', linespacing=1.4)
    save(fig, out, '09_model_comparison')


# ---------- main ----------

def main(csv, res, out):
    os.makedirs(out, exist_ok=True)
    f = pd.read_csv(csv).sort_values(['date', 'game_id', 'play_number'])
    order = f.player.value_counts()
    order = order[order >= A.MIN_FGA].index.tolist()

    nulls = {n: null_draws(f[f.player == n]) for n in order}
    nulls['Duke (team)'] = null_draws(f)
    for n in ['Cameron Boozer', 'Isaiah Evans']:
        print(n, {k: (round(v[0], 3), round(float(v[1].mean()), 3)) for k, v in nulls[n].items()})

    fig_shot_strip(f, out)
    fig_data_stats(f, out)
    official = pd.read_csv(f'{res}/shuffle_tests.csv').set_index(['shooter', 'k'])
    fig_null_hist(nulls, official, out)
    fig_effects(nulls, official, order, out)
    fig_power(res, out)
    fig_shot_selection(res, out)
    fig_models(res, order, out)




# ---------- diagrams and conclusion (added) ----------

def _arrow(ax, p1, p2, rad=0.0, color=INK2, lw=2.2):
    ax.add_patch(FancyArrowPatch(p1, p2, connectionstyle=f'arc3,rad={rad}', arrowstyle='-|>',
                                 mutation_scale=22, color=color, lw=lw, shrinkA=0, shrinkB=0))


def fig_markov(out):
    fig = plt.figure(figsize=(W, H))
    title(fig, 'Modeling a shooter as a Markov chain',
          'The state is the result of the last shot. Arrows give the chance of a make or miss next.')
    ax = fig.add_axes([0.03, 0.1, 0.5, 0.66])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    mk, ms = (2.8, 5), (7.4, 5)
    r = 1.25
    ax.add_patch(Circle(mk, r, color=BLUE))
    ax.add_patch(Circle(ms, r, facecolor='white', edgecolor=BLUE, lw=3))
    ax.text(*mk, 'Make', ha='center', va='center', fontsize=17, fontweight='bold', color='white')
    ax.text(*ms, 'Miss', ha='center', va='center', fontsize=17, fontweight='bold', color=BLUE)
    _arrow(ax, (mk[0] + 0.9, mk[1] + 0.9), (ms[0] - 0.9, ms[1] + 0.9), rad=-0.35)
    _arrow(ax, (ms[0] - 0.9, ms[1] - 0.9), (mk[0] + 0.9, mk[1] - 0.9), rad=-0.35)
    ax.text(5.1, 7.35, '1 − a', ha='center', fontsize=15, color=INK)
    ax.text(5.1, 2.35, 'b', ha='center', va='top', fontsize=16, color=INK, fontweight='bold')
    # self loops
    _arrow(ax, (mk[0] - 0.55, mk[1] + 1.15), (mk[0] + 0.55, mk[1] + 1.15), rad=-2.2, color=ORANGE)
    ax.text(mk[0], mk[1] + 2.85, 'a', ha='center', fontsize=17, color=ORANGE, fontweight='bold')
    _arrow(ax, (ms[0] - 0.55, ms[1] - 1.15), (ms[0] + 0.55, ms[1] - 1.15), rad=2.2)
    ax.text(ms[0], ms[1] - 3.15, '1 − b', ha='center', fontsize=15, color=INK)
    ax.text(5.1, 0.2, 'a = P(make | make)     b = P(make | miss)', ha='center', fontsize=12.5, color=INK2)

    x0 = 0.57
    fig.text(x0, 0.72, 'Hot hand means a > b', fontsize=16, fontweight='bold', color=NAVY)
    fig.text(x0, 0.64, r'$D_1 = a - b$', fontsize=17, color=INK)
    fig.text(x0, 0.56, 'More generally, for streaks of k = 1, 2, 3:', fontsize=12.5, color=INK2)
    fig.text(x0, 0.5, r'$D_k = P(\mathrm{make}\mid k\ \mathrm{makes}) - P(\mathrm{make}\mid k\ \mathrm{misses})$',
             fontsize=13, color=INK)
    fig.add_artist(plt.Line2D([x0, 0.95], [0.43, 0.43], color=LIGHT, lw=1))
    fig.text(x0, 0.38, 'Long-run FG% (stationary distribution)', fontsize=13, fontweight='bold', color=NAVY)
    fig.text(x0, 0.29, r'$\pi_{\mathrm{make}} = \dfrac{b}{1 - a + b}$', fontsize=19, color=INK)
    fig.text(x0, 0.19, 'Streaky (a = .60, b = .40) and independent\n(a = b = .50) shooters both make 50%.',
             fontsize=12.5, color=INK2, linespacing=1.4, va='center')
    fig.text(x0, 0.105, 'So FG% alone can\'t reveal a hot hand.', fontsize=12.5, color=INK, fontweight='semibold')
    fig.text(0.055, 0.035, 'Higher-order chains use the last 2 or 3 shots as the state (4 or 8 states).',
             fontsize=11.5, color=INK2)
    save(fig, out, '03_markov_chain')


def _dots(ax, seq, y, x0=0.0, step=0.42, r=0.15):
    for i, m in enumerate(seq):
        if m:
            ax.add_patch(Circle((x0 + i * step, y), r, color=BLUE))
        else:
            ax.add_patch(Circle((x0 + i * step, y), r, facecolor='white', edgecolor=BLUE, lw=1.6))


def fig_shuffle_flow(f, nulls, official, out):
    g = f[(f.player == 'Cameron Boozer') & (f.opponent.str.contains('Boston College'))]
    seq = g.made.tolist()
    rng = np.random.default_rng(4)
    shuf = list(rng.permutation(seq))
    fig = plt.figure(figsize=(W, H))
    title(fig, 'The shuffle test',
          'How we find what streaks look like when there is no hot hand (a permutation test)')
    ax = fig.add_axes([0.0, 0.0, 1.0, 0.8])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12)
    ax.set_aspect('equal')
    ax.axis('off')
    steps = [
        ('Start with the real season', 'Each player\'s makes and misses, game by game, in order.'),
        ('Shuffle within each game', 'Same shots and same makes per game, random order.'),
        ('Repeat 10,000 times', f'Compute $D_k$ each time to get its "no hot hand" distribution.'),
        ('Compare the real $D_k$', 'p-value = share of shuffles at least as hot as the real season.'),
    ]
    ys = [10.0, 7.3, 4.6, 1.9]
    for i, ((h, d), y) in enumerate(zip(steps, ys)):
        ax.add_patch(Circle((1.0, y), 0.5, color=NAVY))
        ax.text(1.0, y, str(i + 1), ha='center', va='center', color='white', fontsize=15, fontweight='bold')
        ax.text(1.85, y + 0.28, h, fontsize=14.5, fontweight='bold', color=INK, va='center')
        ax.text(1.85, y - 0.42, d, fontsize=11.5, color=INK2, va='center')
        if i < 3:
            _arrow(ax, (1.0, y - 0.65), (1.0, ys[i + 1] + 0.65), lw=1.6, color=LIGHT)
    gx = 11.6
    _dots(ax, seq, ys[0], x0=gx)
    _dots(ax, shuf, ys[1], x0=gx)
    # mini histogram for step 3 and 4
    obs, null = nulls['Cameron Boozer'][3]
    counts, edges = np.histogram(null, bins=np.linspace(-0.35, 0.45, 25))
    cw = 0.27
    for step_y, show_obs in [(ys[2], False), (ys[3], True)]:
        base = step_y - 0.9
        for c_i, c in enumerate(counts):
            hgt = 1.8 * c / counts.max()
            ax.add_patch(plt.Rectangle((gx + c_i * cw, base), cw * 0.85, hgt, color=LIGHT))
        if show_obs:
            xo = gx + (obs - edges[0]) / (edges[-1] - edges[0]) * len(counts) * cw
            ax.plot([xo, xo], [base, base + 2.0], color=ORANGE, lw=2.6)
            ax.text(xo + 0.15, base + 1.85, f'real {obs:+.3f}', color=ORANGE, fontsize=11, fontweight='bold',
                    va='center')
            ax.text(gx + len(counts) * cw, base - 0.25,
                    f'Boozer, k = 3: p = {official.loc[("Cameron Boozer", 3)].p_hot:.2f}',
                    ha='right', va='top', fontsize=11, color=INK2)
    save(fig, out, '04_shuffle_test')


def fig_conclusion(out):
    fig = plt.figure(figsize=(W, H))
    fig.text(0.055, 0.945, 'No hot hand at Duke.', fontsize=30, fontweight='bold', color=NAVY, va='top')
    fig.text(0.055, 0.865, 'But players shoot like they believe in one.', fontsize=23, fontweight='bold',
             color=ORANGE, va='top')
    items = [
        ('0 of 9', 'players had a significant hot hand\nafter comparing to 10,000 shuffled seasons'),
        ('48.0% vs. 49.9%', 'Duke\'s FG% after a make vs. after a miss:\nno team momentum (p = 0.79)'),
        ('31% → 52%', 'Caleb Foster\'s share of threes after a miss\nvs. after a make (p = 0.005)'),
    ]
    for i, (num, lab) in enumerate(items):
        y = 0.745 - i * 0.11
        fig.text(0.055, y, num, fontsize=27, fontweight='bold', color=NAVY, va='center')
        fig.text(0.5, y, lab, fontsize=13, color=INK2, va='center', linespacing=1.35)
    fig.text(0.055, 0.385, 'No evidence isn\'t proof of absence: a hot hand of 15+ percentage points would very likely '
             'have\nshown up for our top two shooters (87-91% power), but a smaller one could hide in one season.',
             fontsize=12.5, color=INK, va='center', linespacing=1.45)
    fig.add_artist(plt.Line2D([0.055, 0.945], [0.315, 0.315], color=LIGHT, lw=1))
    fig.text(0.055, 0.28, 'References', fontsize=12.5, fontweight='bold', color=NAVY, va='center')
    fig.text(0.945, 0.28, 'Code and data: github.com/andrewjaynes/hothand', fontsize=10.5, color=INK2,
             va='center', ha='right')
    refs = ('Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of\n'
            '      random sequences. Cognitive Psychology, 17(3), 295-314.\n'
            'Miller, J. B., & Sanjurjo, A. (2018). Surprised by the hot hand fallacy? A truth in the law of small\n'
            '      numbers. Econometrica, 86(6), 2019-2047.\n'
            'sportsdataverse. (2026). hoopR-mbb-data: Men\'s college basketball play-by-play, 2025-26 [Data set].\n'
            '      github.com/sportsdataverse/hoopR-mbb-data')
    fig.text(0.055, 0.25, refs, fontsize=10, color=INK2, va='top', linespacing=1.35)
    fig.text(0.055, 0.04, 'AI disclosure: We used Claude (Anthropic) to write our data cleaning and analysis code.',
             fontsize=10, color=INK2, va='center', style='italic')
    save(fig, out, '10_conclusion')


def main_extra(csv, res, out):
    f = pd.read_csv(csv).sort_values(['date', 'game_id', 'play_number'])
    official = pd.read_csv(f'{res}/shuffle_tests.csv').set_index(['shooter', 'k'])
    nulls = {'Cameron Boozer': null_draws(f[f.player == 'Cameron Boozer'], k_list=(3,))}
    fig_markov(out)
    fig_shuffle_flow(f, nulls, official, out)
    fig_conclusion(out)




# ---------- assembly map ----------

def fig_layout(out):
    """Board at 1:3 scale (24 x 36 in), each panel placed at its printed size."""
    from PIL import Image
    BW, BH = 24, 36
    fig = plt.figure(figsize=(BW / 3, BH / 3 + 1.3))
    ax = fig.add_axes([0.02, 0.02, 0.96, BH / (BH + 3.9)])
    ax.set_xlim(0, BW)
    ax.set_ylim(0, BH)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.add_patch(plt.Rectangle((0, 0), BW, BH, facecolor='#F4F1EA', edgecolor=INK2, lw=1.2))
    L, R = 1.7, 12.3
    slots = [  # (file, x, y_bottom, w, h, label)
        (None, L, 32.5, 20.6, 3.0, 'Title + team names (Canva or by hand)'),
        ('01_shot_strip', L, 27.9, 10, 4.2, '1'),
        ('02_data_stats', L, 24.3, 10, 3.2, '2'),
        ('03_markov_chain', L, 16.4, 10, 7.5, '3'),
        ('04_shuffle_test', L, 8.5, 10, 7.5, '4'),
        ('05_baseline_not_zero', L, 0.6, 10, 7.5, '5'),
        ('06_effects_vs_chance', R, 24.6, 10, 7.5, '6'),
        ('08_shot_selection', R, 16.7, 10, 7.5, '7'),
        ('07_power', R, 8.8, 10, 7.5, '8'),
        ('10_conclusion', R, 0.9, 10, 7.5, '9'),
    ]
    for fn, x, y, w, h, lab in slots:
        if fn:
            img = Image.open(f'{out}/{fn}.png').convert('RGB')
            ax.imshow(img, extent=(x, x + w, y, y + h), zorder=2)
            ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, edgecolor=INK2, lw=0.6, zorder=3))
            ax.add_patch(Circle((x + w - 0.45, y + h - 0.45), 0.38, color=ORANGE, zorder=4))
            ax.text(x + w - 0.45, y + h - 0.45, lab, ha='center', va='center', color='white', fontsize=8,
                    fontweight='bold', zorder=5)
        else:
            ax.add_patch(plt.Rectangle((x, y), w, h, facecolor='white', edgecolor=NAVY, lw=1, ls='--'))
            ax.text(x + w / 2, y + h / 2 + 0.35, 'Do Duke Shooters Really Get Hot?', ha='center', va='center',
                    fontsize=13, fontweight='bold', color=NAVY)
            ax.text(x + w / 2, y + h / 2 - 0.65, lab, ha='center', va='center', fontsize=8.5, color=INK2)
    # section tags in the margins
    for txt, x, y0, y1 in [('TOPIC', 0.85, 24.3, 32.1), ('METHODS', 0.85, 0.6, 23.9),
                           ('RESULTS', 23.15, 8.8, 32.1), ('CONCLUSION', 23.15, 0.9, 8.4)]:
        ax.plot([x, x], [y0, y1], color=NAVY, lw=1.5)
        ax.text(x + (-0.35 if x < 12 else 0.35), (y0 + y1) / 2, txt, rotation=90, ha='center', va='center',
                fontsize=8, fontweight='bold', color=NAVY)
    fig.text(0.04, 0.985, 'Poster assembly map', fontsize=15, fontweight='bold', color=NAVY, va='top')
    fig.text(0.04, 0.962, '24" × 36" board shown at 1/3 scale. Panels 3-9 print 10" × 7.5"; panel 1 is 10" × 4.2", '
             'panel 2 is 10" × 3.2".\nPrint each at 100% on letter paper (landscape), trim to the image, and glue. '
             'Read down the left column, then the right.', fontsize=8.5, color=INK2, va='top', linespacing=1.4)
    fig.savefig(f'{out}/00_assembly_map.png', dpi=200)
    fig.savefig(f'{out}/00_assembly_map.pdf')
    plt.close(fig)
    print('saved 00_assembly_map')


if __name__ == '__main__':
    main(*sys.argv[1:4])
    main_extra(*sys.argv[1:4])
    fig_layout(sys.argv[3])
