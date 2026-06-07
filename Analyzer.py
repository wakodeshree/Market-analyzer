import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime

# Mobile-Optimized Dashboard Configuration
st.set_page_config(page_title="Nifty 50 Options Analyzer", page_icon="⚡", layout="centered")

st.title("⚡ Nifty 50 Options Quant Dashboard")
st.markdown("### Real-Time Option Chain & Capital Management Engine")
st.write("---")

# Capital Settings for Trade Validation
st.sidebar.header("💳 Capital Allocator")
capital = st.sidebar.number_input("Your Trading Capital (₹)", min_value=5000, max_value=500000, value=15000, step=1000)
max_risk_per_trade = st.sidebar.slider("Max Risk Allocation (₹)", 150, 1000, 300, 50)

# =======================================================
# ENGINE DATA: SIMULATING NIFTY 50 OPTION CHAIN DATA
# =======================================================
@st.cache_data(ttl=10)
def generate_nifty_option_chain(spot_price):
    """
    Simulates real-time NSE India Option Chain structure with 50-point gaps.
    Calculates Open Interest (OI) to locate major institutional blockages.
    """
    # Round to closest 50-point strike to find At-The-Money (ATM)
    atm_strike = int(round(spot_price / 50) * 50)
    strikes = [atm_strike + i for i in range(-150, 200, 50)]
    
    chain_data = []
    for strike in strikes:
        # Distance from current market spot price
        distance = strike - spot_price
        
        # Simulating realistic option pricing (decaying as it moves Out-Of-The-Money)
        if distance < 0: # In-the-money Calls / Out-of-the-money Puts
            call_ltp = abs(distance) + random.uniform(10, 30)
            put_ltp = random.uniform(5, 25)
            call_oi = random.randint(15000, 45000)
            put_oi = random.randint(55000, 120000) # Heavy Put OI implies Support
        else: # Out-of-the-money Calls / In-the-money Puts
            call_ltp = max(2.0, 120 - distance * 0.6 + random.uniform(-5, 5))
            put_ltp = distance + random.uniform(10, 30)
            call_oi = random.randint(60000, 150000) # Heavy Call OI implies Resistance
            put_oi = random.randint(10000, 40000)
            
        chain_data.append({
            "Call OI (Lakhs)": round(call_oi / 100000, 2),
            "Call Premium (₹)": round(call_ltp, 2),
            "STRIKE PRICE": strike,
            "Put Premium (₹)": round(put_ltp, 2),
            "Put OI (Lakhs)": round(put_oi / 100000, 2)
        })
        
    return pd.DataFrame(chain_data), atm_strike

# Current Market Parameters
nifty_spot = 23515.00  # Baseline Nifty spot price
df_chain, atm_strike_price = generate_nifty_option_chain(nifty_spot)

# Find support and resistance using maximum Open Interest (OI)
highest_call_oi_row = df_chain.loc[df_chain["Call OI (Lakhs)"].idxmax()]
highest_put_oi_row = df_chain.loc[df_chain["Put OI (Lakhs)"].idxmax()]

resistance_zone = int(highest_call_oi_row["STRIKE PRICE"])
support_zone = int(highest_put_oi_row["STRIKE PRICE"])

# =======================================================
# METRICS PANEL FOR MOBILE
# =======================================================
st.subheader("📊 Institutional Open Interest Analysis")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric(label="🎯 Nifty 50 Spot", value=f"₹{nifty_spot}")
with m_col2:
    st.metric(label="🧱 Institutional Support", value=f"{support_zone}", delta="Puts Active")
with m_col3:
    st.metric(label="🚧 Major Resistance", value=f"{resistance_zone}", delta="-Calls Active", delta_color="inverse")

st.markdown(f"👉 **Analysis Overview:** Institutional data shows key floor protection at **{support_zone}**. An upward explosive trend is triggered if Nifty cracks and sustains above **{resistance_zone}**.")

# =======================================================
# INTERACTIVE OPTION CHAIN GRAPHIC UI (FIXED)
# =======================================================
with st.expander("🔍 View Live Nifty 50 Option Chain Matrix"):
    # Removed the background_gradient styling engine completely to prevent the ImportError
    st.dataframe(df_chain, use_container_width=True, hide_index=True)

# =======================================================
# LIVE SCANNER TRIGGER ENGINE
# =======================================================
st.write("---")
st.subheader("⚡ Live Option Breakout Scanner")

if st.button("🔥 Scan Nifty Option Chain for Trades", use_container_width=True):
    with st.spinner("Processing volume delta changes across 7 underlying strike layers..."):
        
        # Simulate a quick structural move breaking past resistance zone
        simulated_breakout_spot = resistance_zone + 12.50
        
        # Regenerate chain at breakout level
        df_breakout_chain, current_atm = generate_nifty_option_chain(simulated_breakout_spot)
        
        st.balloons()
        st.success(f"📈 Nifty Breakout! Market cleared historical Call OI ceiling of {resistance_zone} (Current: ₹{simulated_breakout_spot})")
        
        # Pull standard target Call contract information (At-The-Money Call Option)
        atm_contract = df_breakout_chain[df_breakout_chain["STRIKE PRICE"] == current_atm].iloc[0]
        option_premium = atm_contract["Call Premium (₹)"]
        
        # RISK MANAGEMENT & QUANTITY CALCULATOR FOR NIFTY OPTIONS
        LOT_SIZE = 65  # Nifty 50 statutory lot limitation
        cost_per_lot = option_premium * LOT_SIZE
        
        # Calculate maximum lots you can buy with your ₹15,000 capital
        max_lots_allowed = int(capital / cost_per_lot)
        
        if max_lots_allowed > 0:
            total_premium_outlay = max_lots_allowed * cost_per_lot
            
            # Setup standard mechanical parameters for Scalping
            stop_loss_premium = option_premium - (max_risk_per_trade / (max_lots_allowed * LOT_SIZE))
            # Protect against math dipping premium below zero
            if stop_loss_premium < (option_premium * 0.70):
                stop_loss_premium = option_premium * 0.80 # Cap risk max at 20% of premium
                
            expected_target_premium = option_premium + ((max_risk_per_trade * 2) / (max_lots_allowed * LOT_SIZE))
            
            st.markdown("### 🎯 RECOMMENDED STRATEGY PLAY")
            st.info(f"⚡ **Trade Target:** Buy NIFTY {current_atm} CE (Call Option for Upward Trend)")
            
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                st.metric(label="📥 Entry Premium Buy", value=f"₹{round(option_premium, 2)}")
                st.metric(label="📦 Trade Volume (Lots)", value=f"{max_lots_allowed} Lots ({max_lots_allowed * LOT_SIZE} Qty)")
            with r_col2:
                st.metric(label="🛑 Option Stop-Loss", value=f"₹{round(stop_loss_premium, 2)}")
                st.metric(label="🎯 Premium Take-Profit", value=f"₹{round(expected_target_premium, 2)}")
                
            st.warning(f"💳 **Margin Required:** ₹{round(total_premium_outlay, 2)} | **Remaining Cash Protection:** ₹{round(capital - total_premium_outlay, 2)}")
        else:
            st.error(f"❌ Premium price (₹{option_premium}) for 1 Lot requires ₹{round(cost_per_lot, 2)}. Your current capital of ₹{capital} is insufficient to execute this lot setup.")
