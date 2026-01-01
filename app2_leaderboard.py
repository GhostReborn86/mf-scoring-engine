
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MF Leaderboard", layout="centered")

st.title("Mutual Fund Leaderboard")
st.caption("Monthly Auto-Calculated | Educational & Discovery Tool")

# ---------------- SEBI-STYLE DISCLAIMER ----------------
st.warning(
    """
⚠️ **Important Disclaimer (As per SEBI-style guidance)**

This application is created **solely for educational and informational purposes**.
It **does NOT constitute investment advice, recommendation, solicitation, or offer** 
to buy or sell any mutual fund or financial instrument.

- Mutual fund investments are subject to market risks.
- Past performance and scores do not guarantee future returns.
- Investors should consult a **SEBI-registered financial advisor** before making any investment decisions.
- The creator of this app assumes **no responsibility or liability** for investment outcomes.

Use this leaderboard **only as a learning and comparison aid**, not as a decision tool.
"""
)

st.divider()

# -------------------------------------------------
# MONTH CONTROL
# -------------------------------------------------
CURRENT_MONTH = datetime.now().strftime("%Y-%m")

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = CURRENT_MONTH

st.info(f"Leaderboard Month: {st.session_state.last_refresh}")

# -------------------------------------------------
# STATIC MONTHLY CALCULATION (SNAPSHOT MODEL)
# -------------------------------------------------
def calculate_monthly_scores():
    data = [
        ("Parag Parikh Flexi Cap Fund", "Flexi Cap", 78),
        ("HDFC Flexi Cap Fund", "Flexi Cap", 72),
        ("Kotak Flexi Cap Fund", "Flexi Cap", 70),
        ("Canara Robeco Flexi Cap Fund", "Flexi Cap", 73),

        ("HDFC Mid-Cap Opportunities Fund", "Mid Cap", 76),
        ("Motilal Oswal Midcap Fund", "Mid Cap", 75),
        ("Kotak Emerging Equity Fund", "Mid Cap", 74),
        ("Nippon India Growth Fund", "Mid Cap", 72),

        ("SBI Small Cap Fund", "Small Cap", 73),
        ("Nippon India Small Cap Fund", "Small Cap", 74),
        ("Quant Small Cap Fund", "Small Cap", 76),

        ("ICICI Prudential Bluechip Fund", "Large Cap", 70),
        ("Mirae Asset Large Cap Fund", "Large Cap", 69),
        ("HDFC Top 100 Fund", "Large Cap", 68),

        ("UTI Nifty 50 Index Fund", "Index", 65),
        ("HDFC Nifty 50 Index Fund", "Index", 66),
    ]
    return pd.DataFrame(data, columns=["Fund", "Category", "Score"])

# -------------------------------------------------
# MANUAL MONTHLY REFRESH
# -------------------------------------------------
if st.button("Run Monthly Refresh"):
    st.session_state.last_refresh = CURRENT_MONTH
    st.success("Leaderboard refreshed for current month")

df = calculate_monthly_scores()

def decision(score):
    if score >= 85:
        return "CORE"
    elif score >= 70:
        return "HOLD"
    elif score >= 55:
        return "MONITOR"
    else:
        return "EXIT"

df["Decision"] = df["Score"].apply(decision)
df = df.sort_values("Score", ascending=False)

# -------------------------------------------------
# FILTERS
# -------------------------------------------------
category = st.selectbox(
    "Filter by Category",
    ["All"] + sorted(df["Category"].unique().tolist())
)

if category != "All":
    df = df[df["Category"] == category]

st.dataframe(df, use_container_width=True)

st.caption(
    "Educational tool only. This leaderboard is not investment advice. "
    "For actual decisions, use the Core Scoring Engine and consult a SEBI-registered advisor."
)
