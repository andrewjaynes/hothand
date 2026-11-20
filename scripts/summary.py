import pandas as pd, sys
f = pd.read_csv(sys.argv[1])
def stats(df, key):
    rows = []
    for name, d in df.groupby(key):
        seqs = [g.made.tolist() for _, g in d.groupby('game_id')]
        r = dict(who=name, fga=len(d), fg_pct=d.made.mean())
        for k in (1, 2, 3):
            am = af = bm = bf = 0
            for s in seqs:
                for i in range(k, len(s)):
                    prev = s[i-k:i]
                    if all(prev): am += 1; bm += s[i]
                    elif not any(prev): af += 1; bf += s[i]
            r[f'after_{k}_makes'] = f'{bm/am:.3f} (n={am})' if am else '-'
            r[f'after_{k}_misses'] = f'{bf/af:.3f} (n={af})' if af else '-'
        rows.append(r)
    return pd.DataFrame(rows).sort_values('fga', ascending=False)
pd.set_option('display.width', 250)
t = stats(f, 'player'); t = t[t.fga >= 90]
f2 = f.assign(team='Duke (team sequence)')
out = pd.concat([stats(f2, 'team'), t])
out['fg_pct'] = out.fg_pct.round(3)
print(out.to_string(index=False))
out.to_csv(sys.argv[2], index=False)
