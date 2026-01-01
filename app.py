
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MF Core Scoring Engine", layout="centered")

st.title("Mutual Fund Core Scoring Engine")
st.caption("Strict 3-Year Rule | Decision-Focused | Stable Build")

# -----------------------------
# PRE-CURATED FUND UNIVERSE (STABLE DATA)
# -----------------------------
FUNDS = {
    "Parag Parikh Flexi Cap Fund": {
        "category": "Flexi Cap",
        "score": 78
    },
    "HDFC Mid-Cap Opportunities Fund": {
        "category": "Mid Cap",
        "score": 76
    },
    "Motilal Oswal Midcap Fund": {
        "category": "Mid Cap",
        "score": 75
    },
    "WhiteOak Flexi Cap Fund": {
        "category": "Flexi Cap",
        "score": 74
    },
    "SBI Small Cap Fund": {
        "category": "Small Cap",
        "score": 73
    },
    "Kotak Emerging Equity Fund": {
        "category": "Mid Cap",
        "score": 74
    },
    "Canara Robeco Flexi Cap Fund": {
        "category": "Flexi Cap",
        "score": 73
    },
    "Axis Small Cap Fund": {
        "category": "Small Cap",
        "score": 70
    },
    "Nippon India Growth Fund": {
        "category": "Mid Cap",
        "score": 72
    },
    "ICICI Prudential Bluechip Fund": {
        "category": "Large Cap",
        "score": 70
    }
}

# -----------------------------
# DECISION LOGIC
# -----------------------------
def decision(score):
    if score >= 85:
        return "CORE – ACCUMULATE"
    elif score >= 70:
        return "HOLD"
    elif score >= 55:
        return "MONITOR"
    else:
        return "EXIT / AVOID"

# -----------------------------
# SESSION STORAGE FOR PORTFOLIO
# -----------------------------
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["Single Fund", "Portfolio Mode"])

# -----------------------------
# SINGLE FUND VIEW
# -----------------------------
with tab1:
    fund = st.selectbox("Select Mutual Fund (≥ 3Y history)", list(FUNDS.keys()))

    f = FUNDS[fund]
    score = f["score"]

    st.subheader(fund)
    st.write(f"Category: {f['category']}")
    st.metric("Score", f"{score} / 100")
    st.success(decision(score))

    if st.button("Add to Portfolio"):
        st.session_state.portfolio[fund] = score
        st.success("Added to portfolio")

# -----------------------------
# PORTFOLIO MODE
# -----------------------------
with tab2:
    if st.session_state.portfolio:
        weights = {}
        total_weight = 0

        for fund, score in st.session_state.portfolio.items():
            w = st.number_input(f"Weight for {fund} (%)", 0.0, 100.0, 10.0)
            weights[fund] = w
            total_weight += w

        if total_weight > 0:
            portfolio_score = 0
            rows = []

            for fund, score in st.session_state.portfolio.items():
                portfolio_score += score * (weights[fund] / total_weight)
                rows.append([fund, score, weights[fund]])

            st.metric("Portfolio Score", f"{portfolio_score:.1f} / 100")
            st.table(pd.DataFrame(rows, columns=["Fund", "Score", "Weight (%)"]))
    else:
        st.info("No funds added yet.")
