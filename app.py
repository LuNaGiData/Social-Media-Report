import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------- Layout ----------
st.set_page_config(page_title="Social Media Campaign Report", layout="wide")
st.markdown(
    "<div style='position:fixed;top:10px;right:40px;color:gray;font-size:16px;z-index:1000;'>&copy; Luca Napolitano Gil</div>",
    unsafe_allow_html=True
)
st.title("📊 Social Media Campaign Report")

# ---------- Daten einlesen ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data_export.csv", sep=";")
    df["Datum"] = pd.to_datetime(df["Datum"], errors="coerce")
    if "Videoaufrufe" not in df.columns:
        df["Videoaufrufe"] = 0
    if "Klicks" not in df.columns:
        df["Klicks"] = 0
    if "Plattform" not in df.columns:
        df["Plattform"] = df["Platform"] if "Platform" in df.columns else "Unbekannt"
    return df.dropna(subset=["Datum"])

@st.cache_data
def load_benchmarks():
    df = pd.read_csv("benchmarks.csv", sep=",")
    return df.set_index("Plattform")

df = load_data()
benchmark_df = load_benchmarks()

# ---------- Sidebar: Filter ----------
st.sidebar.header("🔍 Filter")

min_date = df["Datum"].min().date()
max_date = df["Datum"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Zeitraum wählen", [min_date, max_date],
    min_value=min_date, max_value=max_date
)

plattformen = df["Plattform"].dropna().unique()
selected_platforms = st.sidebar.multiselect(
    "Plattformen", plattformen, default=list(plattformen)
)

# ---------- Daten filtern ----------
mask = (
    (df["Datum"].dt.date >= start_date) &
    (df["Datum"].dt.date <= end_date) &
    (df["Plattform"].isin(selected_platforms))
)
filtered_df = df[mask]

st.markdown(f"### Gefilterte Ergebnisse: {len(filtered_df)} Beiträge")

if filtered_df.empty:
    st.info("Keine Daten für die ausgewählte Filterung.")
    st.stop()

# ---------- Engagement Rate berechnen ----------
filtered_df["Engagement Rate"] = (
    filtered_df["Interaktionen"] / filtered_df["Impressionen"]
).replace([float("inf"), -float("inf")], 0).fillna(0) * 100  # Prozent

# ---------- Summary + Benchmarks + Performance ----------
sum_posts = filtered_df.shape[0]
sum_impressions = filtered_df["Impressionen"].sum()
sum_interactions = filtered_df["Interaktionen"].sum()
sum_clicks = filtered_df["Klicks"].sum()
sum_video = filtered_df["Videoaufrufe"].sum()

# Engagement Rate gesamt (Summe!)
if sum_impressions > 0:
    er_total = (sum_interactions / sum_impressions) * 100
else:
    er_total = 0

# Benchmark-Werte aggregieren (nur die ausgewählten Plattformen):
bench = benchmark_df.loc[selected_platforms].mean()

def perf_html(value, bench):
    if pd.isna(bench) or bench == 0:
        return "-"
    percent = ((value - bench) / bench) * 100
    color = "#14ae5c" if percent > 10 else "#f8b500" if percent > -10 else "#db4848"
    sign = "+" if percent >= 0 else ""
    return f"<span style='color:{color}; font-weight:bold'>{sign}{percent:.1f}%</span>"

# ---------- Summary/Overview ----------
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Beiträge", f"{sum_posts:,}", f"{((sum_posts-bench['Posts'])/bench['Posts'])*100:+.1f}%" if bench['Posts'] else "-")
col2.metric("Impressionen", f"{sum_impressions:,}", f"{((sum_impressions-bench['Impressionen'])/bench['Impressionen'])*100:+.1f}%" if bench['Impressionen'] else "-")
col3.metric("Interaktionen", f"{sum_interactions:,}", f"{((sum_interactions-bench['Interaktionen'])/bench['Interaktionen'])*100:+.1f}%" if bench['Interaktionen'] else "-")
col4.metric("Klicks", f"{sum_clicks:,}", f"{((sum_clicks-bench['Klicks'])/bench['Klicks'])*100:+.1f}%" if bench['Klicks'] else "-")
col5.metric("Videoaufrufe", f"{sum_video:,}", f"{((sum_video-bench['Videoaufrufe'])/bench['Videoaufrufe'])*100:+.1f}%" if bench['Videoaufrufe'] else "-")
col6.metric("Engagement Rate", f"{er_total:.2f} %", "")  # Kein Benchmark für ER

st.markdown("---")

# ---------- Kuchendiagramm: Posts pro Plattform ----------
posts_per_platform = filtered_df["Plattform"].value_counts().reset_index()
posts_per_platform.columns = ["Plattform", "Posts"]
fig_pie = px.pie(
    posts_per_platform, names="Plattform", values="Posts",
    title="Posts pro Plattform",
    hole=0.4
)
st.plotly_chart(fig_pie, use_container_width=True)

# ---------- Balkendiagramm: Impressionen pro Plattform ----------
imp_per_platform = filtered_df.groupby("Plattform")["Impressionen"].sum().reset_index()
fig_bar = px.bar(
    imp_per_platform, x="Plattform", y="Impressionen",
    color="Plattform", text_auto=".2s",
    title="Impressionen pro Plattform"
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ---------- Zeitverlauf: Impressionen pro Plattform ----------
time_df = filtered_df.copy()
time_df["Datum"] = pd.to_datetime(time_df["Datum"]).dt.date
time_group = time_df.groupby(["Datum", "Plattform"])["Impressionen"].sum().reset_index()
fig_time = px.line(
    time_group, x="Datum", y="Impressionen", color="Plattform",
    markers=True, title="Zeitverlauf der Impressionen pro Plattform"
)
st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

# ---------- Hilfsfunktion für HTML-Tabellen ----------
def make_html_table(df, perf_cols):
    # Formatiert alle Performance-Spalten farbig und als HTML
    df_disp = df.copy()
    for col in perf_cols:
        df_disp[col] = df_disp[col].apply(lambda x: x if isinstance(x, str) and x.startswith("<span") else x)
    html = df_disp.to_html(escape=False, index=False)
    return html

# ---------- TOP/FLOP & Alle Beiträge mit Performance-Emojis/Zahlen (farbig) ----------
def color_perf(val, bench):
    if pd.isna(bench) or bench == 0:
        return "-"
    percent = ((val - bench) / bench) * 100
    color = "#14ae5c" if percent > 10 else "#f8b500" if percent > -10 else "#db4848"
    sign = "+" if percent >= 0 else ""
    return f"<span style='color:{color}; font-weight:bold'>{sign}{percent:.1f}%</span>"

for plattform in selected_platforms:
    st.subheader(f"📱 Plattform: {plattform}")

    sub_df = filtered_df[filtered_df["Plattform"] == plattform].copy()
    bm = benchmark_df.loc[plattform]

    # Engagement Rate berechnen (pro Post)
    sub_df["Engagement Rate"] = (sub_df["Interaktionen"] / sub_df["Impressionen"]).replace([float("inf"), -float("inf")], 0).fillna(0) * 100

    # ---------- Top 3 ----------
    st.markdown("**Top 3 Beiträge nach Engagement Rate**")
    top3 = sub_df.sort_values("Engagement Rate", ascending=False).head(3)
    if not top3.empty:
        top3_disp = top3[[
            "Titel", "Impressionen", "Interaktionen", "Klicks", "Videoaufrufe", "Engagement Rate"
        ]].copy()
        top3_disp["Imp Perf."] = [color_perf(row["Impressionen"], bm["Impressionen"]) for _, row in top3.iterrows()]
        top3_disp["Int Perf."] = [color_perf(row["Interaktionen"], bm["Interaktionen"]) for _, row in top3.iterrows()]
        top3_disp["Klick Perf."] = [color_perf(row["Klicks"], bm["Klicks"]) for _, row in top3.iterrows()]
        top3_disp["ER (%)"] = top3_disp["Engagement Rate"].map(lambda x: f"{x:.2f} %")
        st.markdown(
            make_html_table(
                top3_disp[["Titel", "Impressionen", "Imp Perf.", "Interaktionen", "Int Perf.", "Klicks", "Klick Perf.", "Videoaufrufe", "ER (%)"]],
                ["Imp Perf.", "Int Perf.", "Klick Perf."]
            ), unsafe_allow_html=True
        )
    else:
        st.info("Keine Top-Beiträge verfügbar.")

    # ---------- Flop 3 ----------
    st.markdown("**Flop 3 Beiträge nach Engagement Rate**")
    flop3 = sub_df.sort_values("Engagement Rate", ascending=True).head(3)
    if not flop3.empty:
        flop3_disp = flop3[[
            "Titel", "Impressionen", "Interaktionen", "Klicks", "Videoaufrufe", "Engagement Rate"
        ]].copy()
        flop3_disp["Imp Perf."] = [color_perf(row["Impressionen"], bm["Impressionen"]) for _, row in flop3.iterrows()]
        flop3_disp["Int Perf."] = [color_perf(row["Interaktionen"], bm["Interaktionen"]) for _, row in flop3.iterrows()]
        flop3_disp["Klick Perf."] = [color_perf(row["Klicks"], bm["Klicks"]) for _, row in flop3.iterrows()]
        flop3_disp["ER (%)"] = flop3_disp["Engagement Rate"].map(lambda x: f"{x:.2f} %")
        st.markdown(
            make_html_table(
                flop3_disp[["Titel", "Impressionen", "Imp Perf.", "Interaktionen", "Int Perf.", "Klicks", "Klick Perf.", "Videoaufrufe", "ER (%)"]],
                ["Imp Perf.", "Int Perf.", "Klick Perf."]
            ), unsafe_allow_html=True
        )
    else:
        st.info("Keine Flop-Beiträge verfügbar.")

    # ---------- Alle Beiträge mit Performance (Übersicht) ----------
    st.markdown("**Alle Beiträge dieser Plattform**")
    all_disp = sub_df[[
        "Titel", "Impressionen", "Interaktionen", "Klicks", "Videoaufrufe", "Engagement Rate"
    ]].copy()
    all_disp["Imp Perf."] = [color_perf(row["Impressionen"], bm["Impressionen"]) for _, row in all_disp.iterrows()]
    all_disp["Int Perf."] = [color_perf(row["Interaktionen"], bm["Interaktionen"]) for _, row in all_disp.iterrows()]
    all_disp["Klick Perf."] = [color_perf(row["Klicks"], bm["Klicks"]) for _, row in all_disp.iterrows()]
    all_disp["ER (%)"] = all_disp["Engagement Rate"].map(lambda x: f"{x:.2f} %")
    st.markdown(
        make_html_table(
            all_disp[["Titel", "Impressionen", "Imp Perf.", "Interaktionen", "Int Perf.", "Klicks", "Klick Perf.", "Videoaufrufe", "ER (%)"]],
            ["Imp Perf.", "Int Perf.", "Klick Perf."]
        ), unsafe_allow_html=True
    )
    st.markdown("---")
