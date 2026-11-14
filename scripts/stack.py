"""Stack consecutive GUNW pairs over Quetta into cumulative line-of-sight change.
Usage: python stack.py 041_A_017
"""
import sys, glob, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
from utm import ll2utm

track = sys.argv[1]
C = 299792458.0
files = sorted(glob.glob(f"sub/{track}_*.npz"))
print("pairs:", len(files))

def deramp(a, valid):
    """Remove a best-fit plane and the median, fitted on valid pixels only."""
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    A = np.c_[xx[valid], yy[valid], np.ones(valid.sum())]
    coef, *_ = np.linalg.lstsq(A, a[valid], rcond=None)
    out = a - (coef[0] * xx + coef[1] * yy + coef[2])
    return out - np.nanmedian(out[valid])

stack_raw, stack_ion, names, cohs = [], [], [], []
ref = None
for f in files:
    d = np.load(f)
    if ref is None:
        ref = (d['x'], d['y']); epsg = int(d['epsg']); lam = C / float(d['f0'])
    if d['x'].shape != ref[0].shape or d['y'].shape != ref[1].shape or not np.allclose(d['x'], ref[0]):
        print("grid mismatch, skipping", f); continue
    unw = d['unwrappedPhase'].astype('f8'); ion = d['ionospherePhaseScreen'].astype('f8')
    coh = d['coherenceMagnitude']; cc = d['connectedComponents']
    good = np.isfinite(unw) & (cc > 0) & (cc < 65535) & (coh > 0.3)
    # keep only the largest connected component so unwrapping is self-consistent
    labs, cnt = np.unique(cc[good], return_counts=True)
    good &= (cc == labs[cnt.argmax()])
    raw = np.where(good, unw, np.nan)
    cor = np.where(good & np.isfinite(ion), unw - ion, np.nan)
    stack_raw.append(deramp(raw, np.isfinite(raw)))
    stack_ion.append(deramp(cor, np.isfinite(cor)))
    names.append(os.path.basename(f)[len(track) + 1:-4]); cohs.append(float(np.nanmean(coh)))
    print(f"{names[-1]}  valid {good.mean():.2f}  coh {cohs[-1]:.2f}  "
          f"raw sd {np.nanstd(stack_raw[-1]) * lam / (4 * np.pi) * 100:.2f} cm  "
          f"iono-corrected sd {np.nanstd(stack_ion[-1]) * lam / (4 * np.pi) * 100:.2f} cm")

x, y = ref
zone = epsg - 32600
qx, qy = ll2utm(67.00, 30.20, zone)
ix = int(np.abs(x - qx).argmin()); iy = int(np.abs(y - qy).argmin())
px = abs(float(x[1] - x[0]))
print(f"wavelength {lam * 100:.2f} cm, pixel {px:.0f} m, Quetta pixel ({ix},{iy}) of {len(x)}x{len(y)}")

def report(stack, label):
    # range change in cm; sign convention still to be confirmed against the product spec
    los = np.array(stack) * lam / (4 * np.pi) * 100.0
    cum = np.nansum(los, axis=0); n = np.isfinite(los).sum(axis=0)
    cum[n < len(stack)] = np.nan
    yy, xx = np.mgrid[0:cum.shape[0], 0:cum.shape[1]]
    r_km = np.hypot((xx - ix), (yy - iy)) * px / 1000.0
    near = (r_km < 12) & np.isfinite(cum); far = (r_km > 30) & np.isfinite(cum)
    print(f"\n== {label}: cumulative over {len(stack)} pairs")
    print(f"   background (>30 km from Quetta): median {np.nanmedian(cum[far]):+.2f} cm, sd {np.nanstd(cum[far]):.2f} cm")
    if near.sum():
        v = cum[near]
        print(f"   within 12 km of Quetta: median {np.nanmedian(v):+.2f}, min {np.nanmin(v):+.2f}, max {np.nanmax(v):+.2f} cm")
        for name, fn in (("min", np.nanargmin), ("max", np.nanargmax)):
            tmp = np.where(near, cum, np.nan); k = fn(tmp); j, i = np.unravel_index(k, cum.shape)
            win = cum[max(0, j - 3):j + 4, max(0, i - 3):i + 4]
            ts = np.nancumsum([np.nanmean(l[max(0, j - 3):j + 4, max(0, i - 3):i + 4]) for l in los])
            print(f"   {name} at {(i - ix) * px / 1000:+.1f} km E, {(iy - j) * px / 1000:+.1f} km N of centre: "
                  f"7x7 mean {np.nanmean(win):+.2f} cm; running sum {np.round(ts, 2).tolist()}")
    return cum

def render(cum, fn, lim):
    """Diverging blue-white-red image, +-lim cm, grey where no data, cross at Quetta."""
    t = np.clip(cum / lim, -1, 1)
    r = np.where(t < 0, 1 + t * 0.85, 1.0); g = 1 - np.abs(t) * 0.8; b = np.where(t > 0, 1 - t * 0.85, 1.0)
    img = np.stack([r, g, b], -1); img[~np.isfinite(cum)] = 0.35
    im = (img * 255).astype('u1')
    for dd in range(-12, 13):
        for a, bb in ((iy + dd, ix), (iy, ix + dd)):
            if 0 <= a < im.shape[0] and 0 <= bb < im.shape[1] and abs(dd) > 4: im[a, bb] = (0, 0, 0)
    Image.fromarray(im).save(fn); print("   saved", fn, im.shape[:2])

c1 = report(stack_raw, "RAW unwrapped phase"); render(c1, f"stack_{track}_raw.png", 6)
c2 = report(stack_ion, "IONOSPHERE-CORRECTED"); render(c2, f"stack_{track}_ion.png", 6)
np.savez_compressed(f"stack_{track}.npz", raw=c1, ion=c2, x=x, y=y, epsg=epsg, names=names)
