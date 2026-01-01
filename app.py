
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="MF Scoring Engine", page_icon="📊", layout="centered")
st.title("Mutual Fund Scoring Engine")
st.caption("Stable Build | Aggressive Compounding Bias")

# =====================================================
# TAB SETUP
# =====================================================
tab1, tab2, tab3 = st.tabs(
    ["Top 50 Leaderboard", "Single Fund (Any MF)", "Portfolio Mode"]
)

# =====================================================
# TAB 1: STATIC LEADERBOARD (NO AMFI CALLS)
# =====================================================
TOP_50 = [
    ("Parag Parikh Flexi Cap Fund", 78),
    ("Quant Small Cap Fund", 76),
    ("HDFC Mid-Cap Opportunities Fund", 76),
    ("Motilal Oswal Midcap Fund", 75),
    ("WhiteOak Flexi Cap Fund", 74),
    ("Nippon India Small Cap Fund", 74),
    ("Kotak Emerging Equity Fund", 74),
    ("Canara Robeco Flexi Cap Fund", 73),
    ("SBI Small Cap Fund", 73),
    ("HDFC Flexi Cap Fund", 72),
    ("Nippon India Growth Fund", 72),
    ("PGIM India Midcap Fund", 71),
    ("Kotak Flexi Cap Fund", 70),
    ("Axis Small Cap Fund", 70),
    ("ICICI Prudential Bluechip Fund", 70),
    ("Mirae Asset Large Cap Fund", 69),
    ("UTI Nifty 50 Index Fund", 65),
    ("HDFC Nifty 50 Index Fund", 66),
]

with tab1:
    st.subheader("Top Mutual Funds – Core Universe")
    df = pd.DataFrame(TOP_50, columns=["Fund", "Score"]).sort_values("Score", ascending=False)

    def label(s):
        if s >= 85: return "CORE"
        if s >= 70: return "HOLD"
        if s >= 55: return "MONITOR"
        return "EXIT"

    df["Decision"] = df["Score"].apply(label)
    st.dataframe(df, use_container_width=True)
    st.info("Static leaderboard for stability. Not a buy list.")

# =====================================================
# TAB 2: ANY MF – AMFI ON-DEMAND ONLY
# =====================================================
@st.cache_data(show_spinner=False)
def load_amfi_master():
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    df = pd.read_csv(url, sep=";", engine="python", on_bad_lines="skip")
    return df[["Scheme Code", "Scheme Name"]].dropna()

@st.cache_data(show_spinner=False)
def fetch_nav(code):
    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    df = pd.read_csv(url, sep=";", engine="python", on_bad_lines="skip")
    df = df[df["Scheme Code"] == code]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df["NAV"] = pd.to_numeric(df["Net Asset Value"], errors="coerce")
    return df.dropna().sort_values("Date")

def compute_score(nav):
    years = (nav["Date"].iloc[-1] - nav["Date"].iloc[0]).days / 365.25
    nav["ret"] = nav["NAV"].pct_change()
    cagr = (nav["NAV"].iloc[-1] / nav["NAV"].iloc[0]) ** (1/years) - 1
    vol = nav["ret"].std() * np.sqrt(252)
    dd = (nav["NAV"] / nav["NAV"].cummax() - 1).min()

    score = 0
    score += 12 if cagr*100 > 15 else 10 if cagr*100 > 12 else 8
    score += 8 if vol*100 < 18 else 6 if vol*100 < 22 else 4
    score += 8 if dd*100 > -25 else 6 if dd*100 > -35 else 4
    score += 36  # qualitative proxies

    if years < 3:
        score = min(score, 60)

    return round(score), round(years,2), round(cagr*100,2), round(vol*100,2), round(dd*100,2)

if "saved_funds" not in st.session_state:
    st.session_state.saved_funds = {}

with tab2:
    st.subheader("Evaluate Any Mutual Fund (On-Demand)")
    q = st.text_input("Search fund name")

    if q:
        amfi = load_amfi_master()
        matches = amfi[amfi["Scheme Name"].str.contains(q, case=False)].head(10)

        if not matches.empty:
            name = st.selectbox("Select fund", matches["Scheme Name"])
            code = matches[matches["Scheme Name"] == name]["Scheme Code"].iloc[0]

            with st.spinner("Evaluating fund..."):
                nav = fetch_nav(code)
                score, yrs, cagr, vol, dd = compute_score(nav)

            if yrs < 3:
                st.warning("Early-stage fund (<3 years). Score capped at 60.")

            st.metric("Score", f"{score} / 100")
            st.table(pd.DataFrame({
                "Metric": ["Years", "CAGR %", "Volatility %", "Max Drawdown %"],
                "Value": [yrs, cagr, vol, dd]
            }))

            st.session_state.saved_funds[name] = score

# =====================================================
# TAB 3: PORTFOLIO MODE (NO AMFI)
# =====================================================
with tab3:
    if st.session_state.saved_funds:
        sel = st.multiselect("Select evaluated funds", list(st.session_state.saved_funds.keys()))
        weights = {}
        total = 0

        for f in sel:
            w = st.number_input(f"Weight for {f} (%)", 0.0, 100.0, 10.0)
            weights[f] = w
            total += w

        if sel and total > 0:
            pscore = 0
            rows = []
            for f in sel:
                s = st.session_state.saved_funds[f]
                pscore += s * (weights[f] / total)
                rows.append([f, s, weights[f]])

            st.metric("Portfolio Score", f"{pscore:.1f} / 100")
            st.table(pd.DataFrame(rows, columns=["Fund", "Score", "Weight (%)"]))
    else:
        st.info("Evaluate at least one fund first.")
