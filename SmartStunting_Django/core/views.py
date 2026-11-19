from pathlib import Path
import random
import io
import pandas as pd
import plotly.graph_objects as go
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages
from . import fuzzy_engine as fz
from .data_loader import load_wide, display_name

DATA_PATH = Path(settings.BASE_DIR) / "data" / "Data Stunting Indonesia.csv"
LEVEL_COLOR = {"Rendah": "#2E9E6B", "Sedang": "#E3A81F", "Tinggi": "#E8743B", "Kritis": "#C73A4B"}
PREV_COLOR = {"Rendah": "#2E9E6B", "Sedang": "#E3A81F", "Tinggi": "#E8743B", "Sangat Tinggi": "#C73A4B"}
TREND_COLOR = {"Menurun": "#2E9E6B", "Stagnan": "#E3A81F", "Meningkat": "#C73A4B"}
REKOMENDASI = {
    "Rendah": ["Pertahankan program gizi dan Posyandu yang sudah berjalan.", "Lanjutkan pengukuran tinggi dan berat badan balita secara rutin setiap bulan.", "Jaga kualitas pencatatan dan pelaporan data agar tren tetap terpantau."],
    "Sedang": ["Perkuat pengukuran tinggi badan balita dan telusuri anak yang pertumbuhannya melambat.", "Tingkatkan edukasi gizi seimbang dan MP-ASI bergizi kepada orang tua.", "Pantau tren setiap tahun; jangan menunggu angka naik sebelum bertindak."],
    "Tinggi": ["Prioritaskan intervensi gizi spesifik: tablet tambah darah ibu hamil, ASI eksklusif, MP-ASI bergizi.", "Perkuat intervensi sensitif: air bersih, sanitasi layak, dan ketahanan pangan keluarga.", "Bentuk koordinasi lintas sektor dengan target terukur per tahun."],
    "Kritis": ["Tetapkan sebagai wilayah prioritas utama dan lakukan koordinasi lintas sektor segera.", "Percepat pemeriksaan dan rujukan balita pendek serta pendampingan keluarga berisiko stunting.", "Sediakan pemberian makanan tambahan dan evaluasi capaian setiap triwulan."],
}
LEVEL_NOTE = {
    "Rendah": "Situasi relatif terkendali. Fokusnya menjaga capaian.",
    "Sedang": "Perlu perhatian. Prevalensi atau tren belum sepenuhnya aman.",
    "Tinggi": "Penanganan perlu diprioritaskan dalam waktu dekat.",
    "Kritis": "Penanganan mendesak dan perlu langkah terkoordinasi.",
}

def get_data():
    return load_wide(DATA_PATH)

def get_table():
    wide, years = get_data()
    rows = []
    for _, r in wide.iterrows():
        vals = [float(r[str(y)]) for y in years]
        trend = fz.slope(years, vals)
        result = fz.infer(vals[-1], trend)
        row = {"Provinsi": display_name(r["Provinsi"]), **{str(y): v for y, v in zip(years, vals)},
               "Tren": trend, "Skor": result["skor"], "Prioritas": result["level"], "Riwayat": vals}
        rows.append(row)
    return pd.DataFrame(rows), years

def fmt(value, digits=1):
    return f"{float(value):.{digits}f}".replace(".", ",")

def chart_html(fig):
    fig.update_layout(
        font=dict(family="Arial, sans-serif", color="#12313A"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=20, t=55, b=35), height=330,
        legend=dict(orientation="h", y=-0.22),
    )
    return fig.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False, "responsive": True})

def base_context(active, **kwargs):
    return {"active": active, "levels": fz.LEVELS, **kwargs}

def home(request):
    try:
        table, years = get_table()
        last, first = str(years[-1]), str(years[0])
        top = table.sort_values(last, ascending=False).iloc[0]
        context = base_context("home", total=len(table), last=last, first=first,
            average=fmt(table[last].mean()), drop=fmt(table[first].mean()-table[last].mean()),
            top_province=top["Provinsi"], top_value=fmt(top[last]))
    except Exception as exc:
        context = base_context("home", error=str(exc))
    return render(request, "core/home.html", context)

def consultation(request):
    table, years = get_table()
    provinces = sorted(table["Provinsi"].tolist())
    result = None
    label = ""
    selected_province = request.POST.get("province", "Jawa Timur")
    if selected_province not in provinces:
        selected_province = provinces[0]
    mode = request.POST.get("mode", "manual")
    if request.method == "POST":
        try:
            if mode == "dataset":
                year = int(request.POST.get("year", years[-1]))
                row = table[table["Provinsi"] == selected_province].iloc[0]
                ys = [y for y in years if y <= year]
                vals = [float(row[str(y)]) for y in ys]
                prevalence, trend = vals[-1], fz.slope(ys, vals)
                label = f"{selected_province} ({year})"
            else:
                prevalence = float(request.POST.get("prevalence", 12))
                trend = float(request.POST.get("trend", -1))
                label = f"Prevalensi {fmt(prevalence)}% dan tren {fmt(trend, 2)} poin/tahun"
            result = fz.infer(prevalence, trend)
        except Exception as exc:
            messages.error(request, f"Input tidak valid: {exc}")
    return render(request, "core/consultation.html", base_context("consultation",
        provinces=provinces, years=years, result=result, label=label, mode=mode,
        selected_province=selected_province, recommendations=REKOMENDASI,
        level_note=LEVEL_NOTE, level_colors=LEVEL_COLOR, prev_colors=PREV_COLOR, trend_colors=TREND_COLOR,
        fmt=fmt, rules=fz.RULES))

def knowledge(request):
    prev_specs = [{"name": n, "params": p, "color": PREV_COLOR[n]} for n,p in fz.PREV_SETS.items()]
    trend_specs = [{"name": n, "params": p, "color": TREND_COLOR[n]} for n,p in fz.TREND_SETS.items()]
    output_specs = [{"name": n, "params": p, "color": LEVEL_COLOR[n]} for n,p in fz.OUT_SETS.items()]
    return render(request, "core/knowledge.html", base_context("knowledge",
        rules=fz.RULES, prev_specs=prev_specs, trend_specs=trend_specs, output_specs=output_specs))

def quiz(request):
    table, years = get_table()
    provinces = sorted(table["Provinsi"].tolist())
    province = request.POST.get("province") or request.session.get("quiz_province") or random.choice(provinces)
    if province not in provinces: province = provinces[0]
    request.session["quiz_province"] = province
    row = table[table["Provinsi"] == province].iloc[0]
    last = years[-1]
    vals = [float(row[str(y)]) for y in years]
    trend = fz.slope(years, vals)
    result = None
    guess = request.POST.get("guess", "Sedang")
    if request.method == "POST" and "check" in request.POST:
        result = fz.infer(vals[-1], trend)
        score = request.session.get("quiz_score", {"correct": 0, "total": 0})
        score["total"] += 1
        if guess == result["level"]: score["correct"] += 1
        request.session["quiz_score"] = score
    if request.method == "POST" and "randomize" in request.POST:
        province = random.choice(provinces)
        request.session["quiz_province"] = province
        row = table[table["Provinsi"] == province].iloc[0]
        vals = [float(row[str(y)]) for y in years]
        trend = fz.slope(years, vals)
        result = None
    score = request.session.get("quiz_score", {"correct": 0, "total": 0})
    return render(request, "core/quiz.html", base_context("quiz", provinces=provinces,
        province=province, years=years, values=vals, prevalence=vals[-1], trend=trend,
        result=result, guess=guess, score=score, level_colors=LEVEL_COLOR,
        recommendations=REKOMENDASI, level_note=LEVEL_NOTE, fmt=fmt, rules=fz.RULES,
        prev_colors=PREV_COLOR, trend_colors=TREND_COLOR))

def dashboard(request):
    table, years = get_table()
    last = str(years[-1])
    counts = table["Prioritas"].value_counts().reindex(fz.LEVELS, fill_value=0).to_dict()
    avg = table[[str(y) for y in years]].mean()
    fig1 = go.Figure(go.Scatter(x=years, y=avg.values, mode="lines+markers+text",
        text=[fmt(v) for v in avg.values], textposition="top center", name="Rata-rata"))
    top = table.sort_values(last, ascending=False).head(10).iloc[::-1]
    fig2 = go.Figure(go.Bar(x=top[last], y=top["Provinsi"], orientation="h",
        marker_color=[LEVEL_COLOR[x] for x in top["Prioritas"]], text=[fmt(v) for v in top[last]], textposition="outside"))
    fig3 = go.Figure()
    for level in fz.LEVELS:
        subset = table[table["Prioritas"] == level]
        if not subset.empty:
            fig3.add_trace(go.Scatter(x=subset[last], y=subset["Tren"], mode="markers", name=level,
                text=subset["Provinsi"], marker=dict(size=11, color=LEVEL_COLOR[level])))
    ranked = table.sort_values("Skor", ascending=False)[["Provinsi", last, "Tren", "Skor", "Prioritas"]].to_dict("records")
    return render(request, "core/dashboard.html", base_context("dashboard", counts=counts,
        chart_average=chart_html(fig1), chart_top=chart_html(fig2), chart_scatter=chart_html(fig3),
        ranked=ranked, years=years, last=last, fmt=fmt))

def dataset(request):
    table, years = get_table()
    query = request.GET.get("q", "").strip()
    selected = request.GET.getlist("level")
    df = table.copy()
    if query: df = df[df["Provinsi"].str.contains(query, case=False, na=False)]
    if selected: df = df[df["Prioritas"].isin(selected)]
    df = df.sort_values("Provinsi")
    records = []
    for _, row in df.iterrows():
        records.append({"province": row["Provinsi"], "values": [fmt(row[str(y)]) for y in years],
            "trend": fmt(row["Tren"], 2), "score": fmt(row["Skor"]), "level": row["Prioritas"]})
    return render(request, "core/dataset.html", base_context("dataset", records=records,
        years=years, query=query, selected=selected, levels=fz.LEVELS, count=len(records)))

def download_csv(request):
    table, years = get_table()
    response = HttpResponse(table.drop(columns=["Riwayat"]).to_csv(index=False, sep=";", decimal=","),
                            content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="hasil_sistem_pakar_stunting.csv"'
    return response
