import sqlite3
import streamlit as st
from analysis import (
    get_frequencies,
    get_baseline_samples,
    get_miraclib_pbmc_cohort,
    compare_responders,
)
import os
import subprocess

if not os.path.exists("teiko.db"):
    subprocess.run(["python", "load_data.py"], check=True)

st.title("Immune Cell Population Analysis")

conn = sqlite3.connect("teiko.db")

freq = get_frequencies(conn)
baseline = get_baseline_samples(conn)
cohort = get_miraclib_pbmc_cohort(conn)
merged = freq.merge(cohort, on="sample")
stats_table = compare_responders(merged)

st.header("Part 2: Relative Frequencies")
st.dataframe(freq.head(100))

st.header("Part 3: Responders vs Non-Responders")
st.write("Melanoma patients treated with miraclib, PBMC samples only.")
st.image("response_boxplot.png")
st.dataframe(stats_table)

st.header("Part 4: Baseline Subset")
st.write("Melanoma PBMC samples at baseline from miraclib-treated patients.")
st.dataframe(baseline)

st.header("Explore by Population")

population = st.selectbox(
    "Choose a cell population:",
    sorted(merged["population"].unique()),
)

subset = merged[merged["population"] == population]

st.write(f"Showing {len(subset)} samples for {population}")
st.dataframe(subset.head(100))