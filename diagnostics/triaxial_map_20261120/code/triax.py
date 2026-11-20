"""triax.py -- ctypes wrapper of triax_kernel.c + helpers.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import ctypes, os
import numpy as np

_here = os.path.dirname(os.path.abspath(__file__))
_lib = ctypes.CDLL(os.path.join(_here, "libtriax.so"))
_dp = np.ctypeslib.ndpointer(dtype=np.float64, flags="C_CONTIGUOUS")
_lib.triax_eval_many.argtypes = [ctypes.c_int, _dp, _dp, ctypes.c_int, _dp, _dp,
                                 ctypes.c_int, _dp, _dp, _dp]
_lib.triax_eval_many.restype = None
_cache = {}


def _nodes(nt, nphi):
    key = (nt, nphi)
    if key not in _cache:
        x, w = np.polynomial.legendre.leggauss(nt)
        ph = 2*np.pi*(np.arange(nphi) + 0.5)/nphi
        _cache[key] = tuple(np.ascontiguousarray(a) for a in (x, w, np.cos(ph), np.sin(ph)))
    return _cache[key]


def ev(l, q, n=(96, 96)):
    """l: (...,3) semi-axes (any scale), q: (...,3) reference-ball points (broadcast).
    Returns (...,10): E, E_1..E_3, E_11,E_22,E_33,E_12,E_13,E_23."""
    l = np.asarray(l, float); q = np.asarray(q, float)
    shp = np.broadcast_shapes(l.shape, q.shape)
    L = np.ascontiguousarray(np.broadcast_to(l, shp).reshape(-1, 3))
    Q = np.ascontiguousarray(np.broadcast_to(q, shp).reshape(-1, 3))
    out = np.empty((L.shape[0], 10))
    x, w, c, s = _nodes(*n)
    _lib.triax_eval_many(L.shape[0], L, Q, n[0], x, w, n[1], c, s, out)
    return out.reshape(shp[:-1] + (10,))


def shape(s, t):
    """reference normalisation L = diag(1, s, s t)"""
    s = np.asarray(s, float); t = np.asarray(t, float)
    return np.stack(np.broadcast_arrays(np.ones_like(s*t), s, s*t), axis=-1)


def hess_matrix(o):
    return np.array([[o[4], o[7], o[8]], [o[7], o[5], o[9]], [o[8], o[9], o[6]]])
