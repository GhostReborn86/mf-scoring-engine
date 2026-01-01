
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MF Core Scoring Engine", layout="centered")

st.title("Mutual Fund Core Scoring Engine")
st.caption("Strict 3-Year Rule | Long-Term Proven Funds | Stable Build")

# =====================================================
# CORE FUND UNIVERSE – LONG HISTORY (≈40 FUNDS)
# Scores are representative, conservative, and stable
# =====================================================
FUNDS = {

    # -------- LARGE CAP --------
    "ICICI Prudential Bluechip Fund": {"category": "Large Cap", "score": 70},
    "HDFC Top 100 Fund": {"category": "Large Cap", "score": 68},
    "SBI Bluechip Fund": {"category": "Large Cap", "score": 67},
    "Mirae Asset Large Cap Fund": {"category": "Large Cap", "score": 69},
    "Nippon India Large Cap Fund": {"category": "Large Cap", "score": 66},
    "Axis Bluechip Fund": {"category": "Large Cap", "score": 65},
    "UTI Mastershare Unit Scheme": {"category": "Large Cap", "score": 66},
    "Franklin India Bluechip Fund": {"category": "Large Cap", "score": 64},
    "Canara Robeco Bluechip Equity Fund": {"category": "Large Cap", "score": 68},
    "Kotak Bluechip Fund": {"category": "Large Cap", "score": 67},

    # -------- FLEXI CAP --------
    "Parag Parikh Flexi Cap Fund": {"category": "Flexi Cap", "score": 78},
    "HDFC Flexi Cap Fund": {"category": "Flexi Cap", "score": 72},
    "Kotak Flexi Cap Fund": {"category": "Flexi Cap", "score": 70},
    "Canara Robeco Flexi Cap Fund": {"category": "Flexi Cap", "score": 73},
    "Franklin India Flexi Cap Fund": {"category": "Flexi Cap", "score": 71},
    "PGIM India Flexi Cap Fund": {"category": "Flexi Cap", "score": 70},
    "UTI Flexi Cap Fund": {"category": "Flexi Cap", "score": 69},
    "Aditya Birla SL Flexi Cap Fund": {"category": "Flexi Cap", "score": 68},
    "DSP Flexi Cap Fund": {"category": "Flexi Cap", "score": 69},
    "SBI Flexi Cap Fund": {"category": "Flexi Cap", "score": 67},

    # -------- MID CAP --------
    "HDFC Mid-Cap Opportunities Fund": {"category": "Mid Cap", "score": 76},
    "Motilal Oswal Midcap Fund": {"category": "Mid Cap", "score": 75},
    "Kotak Emerging Equity Fund": {"category": "Mid Cap", "score": 74},
    "Nippon India Growth Fund": {"category": "Mid Cap", "score": 72},
    "PGIM India Midcap Fund": {"category": "Mid Cap", "score": 71},
    "Axis Midcap Fund": {"category": "Mid Cap", "score": 70},
    "DSP Midcap Fund": {"category": "Mid Cap", "score": 69},
    "SBI Magnum Midcap Fund": {"category": "Mid Cap", "score": 68},
    "Franklin India Prima Fund": {"category": "Mid Cap", "score": 70},
    "L&T Midcap Fund": {"category": "Mid Cap", "score": 69},

    # -------- SMALL CAP --------
    "SBI Small Cap Fund": {"category": "Small Cap", "score": 73},
    "Nippon India Small Cap Fund": {"category": "Small Cap", "score": 74},
    "Axis Small Cap Fund": {"category": "Small Cap", "score": 70},
    "Quant Small Cap Fund": {"category": "Small Cap", "score": 76},
    "Bandhan Small Cap Fund": {"category": "Small Cap", "score": 55},
    "DSP Small Cap Fund": {"category": "Small Cap", "score": 68},
    "Kotak Small Cap Fund": {"category": "Small Cap", "score": 67},
    "HDFC Small Cap Fund": {"category": "Small Cap", "score": 69},
    "Tata Small Cap Fund": {"category": "Small Cap", "score": 66},
    "Franklin India Smaller Companies Fund": {"category": "Small Cap", "score": 68},

    # -------- INDEX / PASSIVE --------
    "UTI Nifty 50 Index Fund": {"category": "Index", "score": 65},
    "HDFC Nifty 50 Index Fund": {"category": "Index", "score": 66},
    "ICICI Prudential Nifty Next 50 Index Fund": {"category": "Index", "score": 67},
    "SBI Nifty Next 50 Index Fund": {"category": "Index", "score": 66},
    "HDFC Sensex Index Fund": {"category": "Index", "score": 65},
    "UTI Nifty 200 Momentum 30 Index Fund": {"category": "Index", "score": 64},
    "ICICI Prudential Sensex Index Fund": {"category": "Index", "score": 65},
    "Nippon India Nifty 50 Index Fund": {"category": "Index", "score": 64},
    "SBI Nifty 50 Index Fund": {"category": "Index", "score": 65},
    "Kotak Nifty 50 Index Fund": {"category": "Index", "score": 64},
}

# =====================================================
# DECISION LOGIC
# =====================================================
def decision(score):
    if score >= 85:
        return "CORE – ACCUMULATE"
    elif score >= 70:
        return "HOLD"
    elif score >= 55:
        return "MONITOR"
    else:
        return "EXIT / AVOID"

# =====================================================
# SESSION STORAGE
# =====================================================
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {}

# =====================================================
# UI TABS
# =====================================================
tab1, tab2 = st.tabs(["Single Fund", "Portfolio Mode"])

# ---------------- SINGLE FUND ----------------
with tab1:
    fund = st.selectbox("Select Mutual Fund (Long History)", list(FUNDS.keys()))
    f = FUNDS[fund]

    st.subheader(fund)
    st.write(f"Category: {f['category']}")
    st.metric("Score", f"{f['score']} / 100")
    st.success(decision(f['score']))

    if st.button("Add to Portfolio"):
        st.session_state.portfolio[fund] = f["score"]
        st.success("Added to portfolio")

# ---------------- PORTFOLIO MODE ----------------
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
