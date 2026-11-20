import pandas as pd, numpy as np, sys
rng = np.random.default_rng(0)
f = pd.read_csv(sys.argv[1])
def D(seqs, k):
    am=af=bm=bf=0
    for s in seqs:
        for i in range(k, len(s)):
            w = s[i-k:i]
            if w.all(): am+=1; bm+=s[i]
            elif not w.any(): af+=1; bf+=s[i]
    return bm/am - bf/af if am and af else np.nan
for name in ['Cameron Boozer','Isaiah Evans']:
    d = f[f.player==name]
    seqs = [g.made.to_numpy() for _, g in d.groupby('game_id')]
    for k in (1,2,3):
        obs = D(seqs,k)
        sims = np.array([D([rng.permutation(s) for s in seqs],k) for _ in range(2000)])
        sims = sims[~np.isnan(sims)]
        print(name, k, 'obs %.3f  null mean %.3f  p(one-sided) %.3f' % (obs, sims.mean(), (sims>=obs).mean()))
