"""Run E (far grid): signs of h_1,h_2,h_3 and of the three pole traces far from the sphere,
with adaptive node doubling until two successive levels agree to 1e-8.
Non-interval.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import json, sys
import numpy as np
import triax


def conv(l, q, n0):
    n = n0; prev = triax.ev_big(l, q, (n, n))
    while True:
        n = int(n*1.5)
        cur = triax.ev_big(l, q, (n, n))
        d = np.nanmax(np.abs(cur - prev)[1:7]) if np.isfinite(cur[4]) else np.abs(cur - prev)[1:4].max()
        if d < 1e-8 or n > 9000:
            return cur, n, float(d)
        prev = cur


rows = []
G = (1, 1.5, 2.5, 4, 8, 16, 32)
for s in G:
    for t in G:
        l = np.array([1.0, s, s*t]); a = s*t
        n0 = 128 if a <= 6 else 256 if a <= 20 else 512 if a <= 60 else 1024 if a <= 150 else 2048 if a <= 300 else 4096
        c, nc, dc = conv(l, np.zeros(3), n0)
        pt = []; dmax = dc; nmax = nc
        for i in range(3):
            p, n_, d_ = conv(l, np.eye(3)[i], n0)
            pt.append(float(p[1 + i])); dmax = max(dmax, d_); nmax = max(nmax, n_)
        rows.append(dict(s=s, t=t, h=c[4:7].tolist(), pole=pt, n=nmax, last_diff=dmax))
        print("s=%5.1f t=%5.1f h=%s pole=%s n=%d diff=%.0e" % (s, t, np.round(c[4:7], 5), np.round(pt, 5), nmax, dmax), flush=True)
json.dump(rows, open(sys.argv[1], "w"), indent=1)
# rows whose last_diff exceeds 1e-8 are NOT converged and are flagged in the report
