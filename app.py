
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="MF Scoring Engine", page_icon="📊", layout="centered")
st.title("Mutual Fund Scoring Engine")
st.caption("100-Point Model | Aggressive Compounding Bias | On-Demand Any MF")

# -----------------------------
# LOAD AMFI SCHEME MASTER (SAFE)
# -----------------------------
@st.cache_data(show_spinner=False)
def load_amfi_master():
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    df = pd.read_csv(
        url,
        sep=";",
        engine="python",
        on_bad_lines="skip"
    )
    df = df[["Scheme Code", "Scheme Name"]].dropna()
    return df

# -----------------------------
# FETCH NAV HISTORY (SAFE)
# -----------------------------
@st.cache_data(show_spinner=False)
def fetch_nav_history(scheme_code):
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    df = pd.read_csv(
        url,
        sep=";",
        engine="python",
        on_bad_lines="skip"
    )

    df = df[df["Scheme Code"] == scheme_code]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["Net Asset Value"] = pd.to_numeric(df["Net Asset Value"], errors="coerce")
    df = df.dropna().sort_values("Date")
    return df

# -----------------------------
# METRIC ENGINE
# -----------------------------
def compute_metrics(df):
    if df.shape[0] < 750:
        return None

    df = df.copy()
    df["ret"] = df["Net Asset Value"].pct_change()

    years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
    cagr = (df["Net Asset Value"].iloc[-1] / df["Net Asset Value"].iloc[0]) ** (1/years) - 1

    vol = df["ret"].std() * np.sqrt(252)
    drawdown = (df["Net Asset Value"] / df["Net Asset Value"].cummax() - 1).min()

    rolling = df["Net Asset Value"].pct_change(756).dropna()
    rolling_win = (rolling > 0).mean() * 100

    return {
        "CAGR (%)": round(cagr * 100, 2),
        "Volatility (%)": round(vol * 100, 2),
        "Max Drawdown (%)": round(drawdown * 100, 2),
        "Rolling Win %": round(rolling_win, 2)
    }

# -----------------------------
# SCORING ENGINE (AGGRESSIVE)
# -----------------------------
def score(metrics):
    score = 0
    score += 12 if metrics["CAGR (%)"] > 15 else 10 if metrics["CAGR (%)"] > 12 else 8
    score += 12 if metrics["Rolling Win %"] > 65 else 10 if metrics["Rolling Win %"] > 55 else 8
    score += 8 if metrics["Volatility (%)"] < 18 else 6 if metrics["Volatility (%)"] < 22 else 4
    score += 8 if metrics["Max Drawdown (%)"] > -25 else 6 if metrics["Max Drawdown (%)"] > -35 else 4
    score += 10  # Manager/process proxy
    score += 10  # Portfolio quality proxy
    score += 6   # Expense proxy
    score += 6   # AUM proxy
    score += 10  # Cycle proxy
    return score

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "saved_funds" not in st.session_state:
    st.session_state.saved_funds = {}

# -----------------------------
# UI
# -----------------------------
try:
    amfi_master = load_amfi_master()
except Exception as e:
    st.error("Unable to load AMFI data. Please refresh in a few seconds.")
    st.stop()

tab1, tab2 = st.tabs(["Single Fund (Any MF)", "Portfolio Mode"])

# -------- SINGLE FUND --------
with tab1:
    query = st.text_input("Search any Mutual Fund (type name)")

    if query:
        matches = amfi_master[
            amfi_master["Scheme Name"].str.contains(query, case=False, na=False)
        ].head(10)

        if not matches.empty:
            choice = st.selectbox("Select Scheme", matches["Scheme Name"].tolist())
            scheme_code = matches[matches["Scheme Name"] == choice]["Scheme Code"].iloc[0]

            with st.spinner("Fetching & evaluating fund..."):
                nav = fetch_nav_history(scheme_code)
                metrics = compute_metrics(nav)

            if metrics is None:
                st.warning("Fund has insufficient history (< 3 years).")
            else:
                total = score(metrics)
                decision = (
                    "CORE – ACCUMULATE" if total >= 85 else
                    "HOLD" if total >= 70 else
                    "MONITOR" if total >= 55 else
                    "EXIT / AVOID"
                )

                st.metric("Total Score", f"{total} / 100")
                st.success(decision)
                st.table(pd.DataFrame(metrics.items(), columns=["Metric", "Value"]))

                st.session_state.saved_funds[choice] = total
        else:
            st.info("No matching schemes found.")

# -------- PORTFOLIO MODE --------
with tab2:
    if st.session_state.saved_funds:
        selected = st.multiselect(
            "Select evaluated funds",
            list(st.session_state.saved_funds.keys())
        )

        weights = {}
        total_w = 0
        for f in selected:
            w = st.number_input(f"Weight for {f} (%)", 0.0, 100.0, 10.0)
            weights[f] = w
            total_w += w

        if selected and total_w > 0:
            pscore = 0
            rows = []
            for f in selected:
                s = st.session_state.saved_funds[f]
                pscore += s * (weights[f] / total_w)
                rows.append([f, s, weights[f]])

            st.metric("Portfolio Score", f"{pscore:.1f} / 100")
            st.table(pd.DataFrame(rows, columns=["Fund", "Score", "Weight (%)"]))
    else:
        st.info("Evaluate at least one fund to build a portfolio.")
