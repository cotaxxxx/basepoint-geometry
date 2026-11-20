/* triax_big.c -- one (l,q) item with many nodes, parallel over chunks of tau-nodes.
 * Reuses eval_one of triax_kernel.c unchanged (a sub-array of Gauss nodes gives a partial sum).
 * DIAGNOSTIC_ONLY / NOT_EVIDENCE. */
#define triax_eval_many triax_eval_many_unused
#include "triax_kernel.c"
#undef triax_eval_many
#define NCHUNK 64
void triax_eval_big(const double *l, const double *q, int nt, const double *x, const double *wt,
                    int nphi, const double *cph, const double *sph, double *out)
{
    double tmp[NCHUNK][10];
    int nc = nt < NCHUNK ? nt : NCHUNK;
#pragma omp parallel for schedule(dynamic, 1)
    for (int c = 0; c < nc; c++) {
        int a = (int)((long)nt*c/nc), b = (int)((long)nt*(c + 1)/nc);
        eval_one(l, q, b - a, x + a, wt + a, nphi, cph, sph, tmp[c]);
    }
    for (int i = 0; i < 10; i++) { double s = 0; for (int c = 0; c < nc; c++) s += tmp[c][i]; out[i] = s; }
}
