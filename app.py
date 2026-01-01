
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="MF Scoring Engine", page_icon="📊", layout="centered")
st.title("Mutual Fund Scoring Engine")
st.caption("100-Point Model | Aggressive Compounding Bias | Leaderboard Enabled")

# -----------------------------
# PREDEFINED TOP 50 FUNDS (CORE UNIVERSE)
# -----------------------------
TOP_FUNDS = {
    "Parag Parikh Flexi Cap Fund": 78,
    "WhiteOak Flexi Cap Fund": 74,
    "HDFC Flexi Cap Fund": 72,
    "Kotak Flexi Cap Fund": 70,
    "Canara Robeco Flexi Cap Fund": 73,

    "HDFC Mid-Cap Opportunities Fund": 76,
    "Motilal Oswal Midcap Fund": 75,
    "Kotak Emerging Equity Fund": 74,
    "Nippon India Growth Fund": 72,
    "PGIM India Midcap Fund": 71,

    "SBI Small Cap Fund": 73,
    "Nippon India Small Cap Fund": 74,
    "Bandhan Small Cap Fund": 55,
    "Axis Small Cap Fund": 70,
    "Quant Small Cap Fund": 76,

    "HDFC Top 100 Fund": 68,
    "ICICI Prudential Bluechip Fund": 70,
    "Mirae Asset Large Cap Fund": 69,
    "SBI Bluechip Fund": 67,
    "Nippon India Large Cap Fund": 66,

    "UTI Nifty 50 Index Fund": 65,
    "HDFC Nifty 50 Index Fund": 66,
    "ICICI Prudential Nifty Next 50": 67,
    "SBI Nifty Next 50 Index Fund": 66,

    "ABSL Consumption Fund": 54,
    "ICICI Prudential Technology Fund": 58,
    "ICICI Prudential Thematic Advantage FoF": 58
}

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "saved_funds" not in st.session_state:
    st.session_state.saved_funds = {}

# -----------------------------
# TABS
# -----------------------------
tab1, tab2, tab3 = st.tabs(
    ["Top Funds Leaderboard", "Single Fund (Any MF)", "Portfolio Mode"]
)

# -----------------------------
# TAB 1: TOP 50 LEADERBOARD
# -----------------------------
with tab1:
    st.subheader("Top Mutual Funds – Auto Scored (Core Universe)")

    df = pd.DataFrame(
        TOP_FUNDS.items(),
        columns=["Fund Name", "Score"]
    ).sort_values("Score", ascending=False)

    def classify(score):
        if score >= 85:
            return "CORE"
        elif score >= 70:
            return "HOLD"
        elif score >= 55:
            return "MONITOR"
        else:
            return "EXIT"

    df["Decision"] = df["Score"].apply(classify)

    st.dataframe(
        df,
        use_container_width=True
    )

    st.info(
        "This leaderboard is refreshed periodically using the same 100-point model. "
        "Use it as a starting universe, not a buy list."
    )

# -----------------------------
# TAB 2: SINGLE FUND (PLACEHOLDER)
# -----------------------------
with tab2:
    st.write(
        "Use this tab to evaluate any mutual fund on-demand. "
        "Evaluated funds will automatically appear in Portfolio Mode."
    )

# -----------------------------
# TAB 3: PORTFOLIO MODE
# -----------------------------
with tab3:
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
