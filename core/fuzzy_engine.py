"""
Mesin inferensi fuzzy Mamdani (2 input) untuk Sistem Pakar Stunting.

Input 1 : Prevalensi stunting (%)            -> Rendah / Sedang / Tinggi / Sangat Tinggi
Input 2 : Tren perubahan (poin persen/tahun) -> Menurun / Stagnan / Meningkat
Output  : Skor prioritas penanganan (0-100)  -> Rendah / Sedang / Tinggi / Kritis

Ditulis murni dengan numpy (tanpa scikit-fuzzy) supaya mudah dijalankan dan
mudah dijelaskan saat presentasi.
"""
from __future__ import annotations

import numpy as np

PREV_RANGE = (0.0, 40.0)
TREND_RANGE = (-8.0, 8.0)
OUT_RANGE = (0.0, 100.0)

# Himpunan fuzzy trapesium (a, b, c, d). Segitiga = trapesium dengan b == c.
PREV_SETS = {
    "Rendah": (0, 0, 7, 12),
    "Sedang": (8, 13, 17, 22),
    "Tinggi": (18, 23, 28, 33),
    "Sangat Tinggi": (28, 33, 40, 40),
}
TREND_SETS = {
    "Menurun": (-8, -8, -1.5, -0.5),
    "Stagnan": (-1.5, 0, 0, 1.5),
    "Meningkat": (0.5, 1.5, 8, 8),
}
OUT_SETS = {
    "Rendah": (0, 0, 15, 30),
    "Sedang": (20, 40, 40, 60),
    "Tinggi": (50, 65, 65, 80),
    "Kritis": (70, 85, 100, 100),
}
LEVELS = list(OUT_SETS)

# Basis aturan: (prevalensi, tren) -> prioritas
RULES = [
    ("Rendah", "Menurun", "Rendah"),
    ("Rendah", "Stagnan", "Rendah"),
    ("Rendah", "Meningkat", "Sedang"),
    ("Sedang", "Menurun", "Sedang"),
    ("Sedang", "Stagnan", "Sedang"),
    ("Sedang", "Meningkat", "Tinggi"),
    ("Tinggi", "Menurun", "Sedang"),
    ("Tinggi", "Stagnan", "Tinggi"),
    ("Tinggi", "Meningkat", "Kritis"),
    ("Sangat Tinggi", "Menurun", "Tinggi"),
    ("Sangat Tinggi", "Stagnan", "Kritis"),
    ("Sangat Tinggi", "Meningkat", "Kritis"),
]

UNIVERSE = np.linspace(*OUT_RANGE, 1001)


def trapmf(x, a, b, c, d):
    """Fungsi keanggotaan trapesium (mendukung bahu kiri/kanan)."""
    x = np.asarray(x, dtype=float)
    up = np.ones_like(x) if b == a else np.clip((x - a) / (b - a), 0, 1)
    down = np.ones_like(x) if d == c else np.clip((d - x) / (d - c), 0, 1)
    return np.minimum(up, down)


def membership(sets: dict, x) -> dict:
    return {name: float(trapmf(x, *p)) for name, p in sets.items()}


def slope(years, values) -> float:
    """Kemiringan garis tren (poin persen per tahun) lewat regresi linear."""
    y = np.asarray(values, dtype=float)
    x = np.asarray(years, dtype=float)
    ok = ~np.isnan(y)
    if ok.sum() < 2:
        return 0.0
    return float(np.polyfit(x[ok], y[ok], 1)[0])


def _label_at(score: float) -> str:
    best, best_mu = LEVELS[0], -1.0
    for name in LEVELS:  # urutan naik -> jika seri, ambil level lebih berat
        mu = float(trapmf(score, *OUT_SETS[name]))
        if mu >= best_mu:
            best, best_mu = name, mu
    return best


def level_edges() -> list[tuple[str, float, float]]:
    """Rentang skor untuk tiap level (dipakai untuk warna gauge)."""
    edges, start, cur = [], UNIVERSE[0], _label_at(UNIVERSE[0])
    for u in UNIVERSE[1:]:
        lab = _label_at(u)
        if lab != cur:
            edges.append((cur, float(start), float(u)))
            start, cur = u, lab
    edges.append((cur, float(start), float(UNIVERSE[-1])))
    return edges


def infer(prevalensi: float, tren: float) -> dict:
    """Fuzzifikasi -> inferensi Mamdani (min/max) -> defuzzifikasi centroid."""
    p = float(np.clip(prevalensi, *PREV_RANGE))
    t = float(np.clip(tren, *TREND_RANGE))
    mu_p = membership(PREV_SETS, p)
    mu_t = membership(TREND_SETS, t)
    out_mf = {k: trapmf(UNIVERSE, *v) for k, v in OUT_SETS.items()}

    agg = np.zeros_like(UNIVERSE)
    fired = []
    for i, (pl, tl, ol) in enumerate(RULES, 1):
        alpha = min(mu_p[pl], mu_t[tl])  # operator AND = min
        agg = np.maximum(agg, np.minimum(alpha, out_mf[ol]))  # implikasi min, agregasi max
        fired.append({"no": i, "prevalensi": pl, "tren": tl, "prioritas": ol, "alpha": alpha})

    area = agg.sum()
    score = float((UNIVERSE * agg).sum() / area) if area > 0 else 0.0
    return {
        "prevalensi": p, "tren": t, "skor": score, "level": _label_at(score),
        "mu_prevalensi": mu_p, "mu_tren": mu_t, "rules": fired,
        "agg": agg, "out_mf": out_mf,
    }
