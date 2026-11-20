"""Independent reference: E_K(p) straight from the physical definition on the ellipsoid
x = (a1 sin(th) cos(ph), a2 sin(th) sin(ph), a3 cos(th)), with nu = grad(sum x_i^2/a_i^2) normalised,
dA = |x_th x x_ph| dth dph, alpha = arccos((x-p).nu/|x-p|), dmu = (x-p).nu dA/(3 Vol).
No reference-ball identities are used.  DIAGNOSTIC_ONLY / NOT_EVIDENCE."""
import numpy as np


def E_physical(a, p, n=400):
    a = np.asarray(a, float); p = np.asarray(p, float)
    x, w = np.polynomial.legendre.leggauss(n)
    th = 0.5*np.pi*(x + 1); wth = 0.5*np.pi*w
    ph = 2*np.pi*(np.arange(2*n) + 0.5)/(2*n); wph = 2*np.pi/(2*n)
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    X = np.stack([a[0]*np.sin(TH)*np.cos(PH), a[1]*np.sin(TH)*np.sin(PH), a[2]*np.cos(TH)], -1)
    Xth = np.stack([a[0]*np.cos(TH)*np.cos(PH), a[1]*np.cos(TH)*np.sin(PH), -a[2]*np.sin(TH)], -1)
    Xph = np.stack([-a[0]*np.sin(TH)*np.sin(PH), a[1]*np.sin(TH)*np.cos(PH), 0*TH], -1)
    cr = np.cross(Xth, Xph); dA = np.linalg.norm(cr, axis=-1)
    nu = X/a**2; nu /= np.linalg.norm(nu, axis=-1, keepdims=True)
    v = X - p; rr = np.linalg.norm(v, axis=-1)
    h = np.sum(v*nu, -1)
    al = np.arccos(np.clip(h/rr, -1, 1))
    vol = 4*np.pi/3*np.prod(a)
    W = wth[:, None]*wph
    return np.sum(W*al**2*h*dA)/(3*vol), np.sum(W*h*dA)/(3*vol)
