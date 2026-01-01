
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="MF Scoring Engine",
    page_icon="📊",
    layout="centered"
)

st.title("Mutual Fund Scoring Engine")
st.caption("100-Point Model | Aggressive Compounding Bias")

# ---------------- FUND DATABASE ----------------
funds = {
    "Parag Parikh Flexi Cap Fund": {
        "category": "Flexi Cap", "benchmark": "NIFTY 500 TRI",
        "alpha": 1.6, "rolling": 72, "sortino": 1.8, "volatility": 16,
        "downside": 88, "manager": 10, "expense": 0.75,
        "aum": 60000, "portfolio": 9, "cycle": 8
    },
    "WhiteOak Flexi Cap Fund": {
        "category": "Flexi Cap", "benchmark": "NIFTY 500 TRI",
        "alpha": 1.9, "rolling": 68, "sortino": 1.6, "volatility": 17,
        "downside": 92, "manager": 6, "expense": 0.78,
        "aum": 18000, "portfolio": 8, "cycle": 7
    },
    "HDFC Mid-Cap Opportunities Fund": {
        "category": "Mid Cap", "benchmark": "NIFTY Midcap 150 TRI",
        "alpha": 2.2, "rolling": 65, "sortino": 1.5, "volatility": 21,
        "downside": 105, "manager": 9, "expense": 0.85,
        "aum": 52000, "portfolio": 8, "cycle": 7
    },
    "SBI Small Cap Fund": {
        "category": "Small Cap", "benchmark": "NIFTY Smallcap 250 TRI",
        "alpha": 3.1, "rolling": 60, "sortino": 1.4, "volatility": 26,
        "downside": 118, "manager": 8, "expense": 0.9,
        "aum": 26000, "portfolio": 7, "cycle": 6
    },
    "Bandhan Small Cap Fund": {
        "category": "Small Cap", "benchmark": "NIFTY Smallcap 250 TRI",
        "alpha": 2.5, "rolling": 55, "sortino": 1.2, "volatility": 27,
        "downside": 120, "manager": 5, "expense": 0.92,
        "aum": 9000, "portfolio": 6, "cycle": 5
    },
    "ABSL Consumption Fund": {
        "category": "Thematic", "benchmark": "NIFTY India Consumption",
        "alpha": 1.1, "rolling": 48, "sortino": 1.0, "volatility": 24,
        "downside": 122, "manager": 6, "expense": 0.88,
        "aum": 4500, "portfolio": 6, "cycle": 4
    }
}

# ---------------- SCORING FUNCTIONS ----------------
def score_alpha(x): return 12 if x > 2 else 10 if x > 1.5 else 8 if x > 1 else 6
def score_rolling(x): return 12 if x > 70 else 10 if x > 60 else 8 if x > 50 else 6
def score_sortino(x): return 10 if x > 1.8 else 8 if x > 1.5 else 6 if x > 1.2 else 4
def score_volatility(x): return 8 if x < 16 else 6 if x < 20 else 4
def score_downside(x): return 8 if x < 90 else 6 if x < 100 else 4
def score_manager(x): return 8 if x >= 10 else 6 if x >= 7 else 4
def score_expense(x): return 6 if x < 0.8 else 4
def score_aum(x): return 6 if 5000 < x < 50000 else 4

def calculate_score(f):
    scores = {
        "Benchmark Alpha": score_alpha(f["alpha"]),
        "Rolling Return Consistency": score_rolling(f["rolling"]),
        "Risk Adjusted Return": score_sortino(f["sortino"]),
        "Volatility Control": score_volatility(f["volatility"]),
        "Downside Protection": score_downside(f["downside"]),
        "Fund Manager Stability": score_manager(f["manager"]),
        "Portfolio Quality": f["portfolio"],
        "Expense Ratio Efficiency": score_expense(f["expense"]),
        "AUM Suitability": score_aum(f["aum"]),
        "Market Cycle Performance": f["cycle"]
    }
    return scores, sum(scores.values())

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["Single Fund", "Portfolio Mode"])

# -------- Single Fund --------
with tab1:
    fund_name = st.selectbox("Select Mutual Fund", [""] + sorted(funds.keys()))
    if fund_name:
        f = funds[fund_name]
        scores, total = calculate_score(f)

        decision = (
            "CORE – ACCUMULATE" if total >= 85 else
            "HOLD" if total >= 70 else
            "MONITOR" if total >= 55 else
            "EXIT / AVOID"
        )

        st.subheader(fund_name)
        st.write(f"Category: {f['category']}")
        st.write(f"Benchmark: {f['benchmark']}")
        st.metric("Total Score", f"{total} / 100")
        st.success(decision)
        st.table(pd.DataFrame(scores.items(), columns=["Criteria", "Score"]))

# -------- Portfolio Mode --------
with tab2:
    st.subheader("Build Your Portfolio")

    selected_funds = st.multiselect(
        "Select Funds",
        options=sorted(funds.keys())
    )

    weights = {}
    total_weight = 0

    for fund in selected_funds:
        w = st.number_input(
            f"Weight for {fund} (%)",
            min_value=0.0, max_value=100.0, step=5.0
        )
        weights[fund] = w
        total_weight += w

    if selected_funds and total_weight > 0:
        portfolio_score = 0
        details = []

        for fund in selected_funds:
            scores, total = calculate_score(funds[fund])
            weighted = total * (weights[fund] / total_weight)
            portfolio_score += weighted
            details.append([fund, total, weights[fund]])

        decision = (
            "STRONG PORTFOLIO" if portfolio_score >= 75 else
            "AVERAGE – NEEDS IMPROVEMENT" if portfolio_score >= 65 else
            "HIGH RISK / WEAK"
        )

        st.metric("Portfolio Score", f"{portfolio_score:.1f} / 100")
        st.success(decision)
        st.table(pd.DataFrame(details, columns=["Fund", "Score", "Weight (%)"]))
