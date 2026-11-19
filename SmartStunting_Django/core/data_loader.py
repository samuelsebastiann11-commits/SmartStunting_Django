"""Pembaca dataset stunting (CSV titik-koma, desimal koma, kolom kosong di ujung)."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd


def load_wide(path: str | Path) -> tuple[pd.DataFrame, list[int]]:
    text = Path(path).read_text(encoding="utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # file asli memakai CR saja
    df = pd.read_csv(io.StringIO(text), sep=";", dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, [c for c in df.columns if c and not c.startswith("Unnamed")]]

    if "Provinsi" not in df.columns:
        raise ValueError(f"Kolom 'Provinsi' tidak ditemukan. Kolom tersedia: {list(df.columns)}")
    year_cols = [c for c in df.columns if c.isdigit()]
    if len(year_cols) < 2:
        raise ValueError("Dataset harus memiliki minimal dua kolom tahun.")

    for c in year_cols:
        df[c] = pd.to_numeric(df[c].str.strip().str.replace(",", ".", regex=False), errors="coerce")
    df["Provinsi"] = df["Provinsi"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=["Provinsi"]).query("Provinsi != ''").reset_index(drop=True)
    return df[["Provinsi"] + year_cols], [int(c) for c in year_cols]


def display_name(name: str) -> str:
    out = name.title()
    for a, b in (("Dki ", "DKI "), ("Di ", "DI ")):
        if out.startswith(a):
            out = b + out[len(a):]
    return out
