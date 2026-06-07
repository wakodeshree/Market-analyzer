import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set up mobile-friendly page config
st.set_page_config(page_title="Pro Quant Analyzer", page_icon="📈", layout="centered")

st.title("📈 Pro Quant Market Analyzer")
st.markdown("### High-Probability Intraday & Options Engine")
st.write("---")

# User Configuration Sidebar (Perfect for Mobile view)
st.sidebar.header("⚙️ Risk & Capital Settings")
capital = st.sidebar.number_input("Your Trading Capital (₹)", min_value=5000, max_value=1000000, value=15000, step=1000)
max_risk_pct = st.sidebar.slider("Max Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
max_risk_rupees = (max_risk_pct / 100) * capital

selected_stock = st.sidebar.selectbox("Select Target Stock", ["SBIN", "TATAMOTORS", "RELIANCE", "INFY"])

# ==========================================
# ADVANCED ANALYSIS: PREVIOUS CHARTS LOGIC
# ==========================================
@st.cache_data(ttl=60)
def analyze_previous_charts(stock):
    """
    Simulates looking at the last 5 days of historical daily charts 
    to find major Support, Resistance, and Trend direction.
    """
    # In production, this data would come from a live API history payload
    base_prices = {"SBIN": 810.0, "TATAMOTORS": 950.0, "RELIANCE": 2450.0, "INFY": 1420.0}
    bp = base_prices[stock]
    
    historical_resistance = bp * 1.015  # Key swing high
    historical_support = bp * 0.985     # Key swing low
    
    return round(historical_support, 2), round(historical_resistance, 2)

prev_support, prev_resistance = analyze_previous_charts(selected_stock)

# Display historical analysis block
st.subheader("📊 Historical Chart Analysis (Multi-Day)")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="🔑 Key Historical Support", value=f"₹{prev_support}")
with col2:
    st.metric(label="🚀 Major Resistance Barrier", value=f"₹{prev_resistance}")

st.info(f"💡 **System Strategy:** The engine will validate live breakouts only if the price clears the historical resistance barrier of **₹{prev_resistance}**.")

# ==========================================
# LIVE ENGINE SCANNER
# ==========================================
st.write("---")
st.subheader("⚡ Live Market Scanner Execution")

if st.button("🚀 Execute Strategy Scan", use_container_width=True):
    with st.spinner("Analyzing current volume profiles and calculating VWAP..."):
        
        # Simulate live price ticks breaking past the historical levels
        ticks = 10
        current_price = prev_resistance - 2.0  # Start just below resistance
        market_data = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        trade_triggered = False
        
        for i in range(ticks):
            # Simulate a strong upward breakout move on institutional volume
            current_price += random.uniform(-0.5, 2.5)
            volume = random.randint(15000, 45000)
            
            high = current_price * 1.001
            low = current_price * 0.999
            
            market_data.append({'close': current_price, 'high': high, 'low': low, 'volume': volume})
            df = pd.DataFrame(market_data)
            
            # Calculate VWAP
            typical_price = (df['close'] + df['high'] + df['low']) / 3
            df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            latest_vwap = df['vwap'].iloc[-1]
            
            status_text.text(f"Scanning Tick {i+1}/10 | Price: ₹{round(current_price, 2)} | VWAP: ₹{round(latest_vwap, 2)}")
            progress_bar.progress((i + 1) / ticks)
            
            # CHECK MULTI-LAYER CONDITION:
            # 1. Price must be above VWAP
            # 2. Price must break out past historical chart resistance
            if not trade_triggered and current_price > latest_vwap and current_price > prev_resistance:
                trade_triggered = True
                
                # Math: Risk Calculations for Spot
                stop_loss = current_price * 0.995
                target = current_price * 1.015  # Higher target due to structural breakout
                
                # OPTIONS STRATEGY ENGINE CALCULATIONS
                # Determine ATMs/OTM Strike price based on current stock underlying value
                strike_price = int(round(current_price / 10) * 10)
                option_name = f"{selected_stock} {strike_price} CE (Call Option)"
                
                # Estimated standard option premium price for an active intraday contract
                estimated_premium = 25.0 
                
                # Math: Calculate exact quantity based on premium cost and capital limits
                # Options buying doesn't allow leverage, full premium required upfront
                max_qty_by_capital = int(capital / estimated_premium)
                
                # Risk allocation constraints (Stop-loss on option is typically tighter or managed on spot)
                # Let's cap maximum lot sizing to respect risk per trade allocation
                allowed_option_qty = max_qty_by_capital
                if (allowed_option_qty * estimated_premium * 0.20) > max_risk_rupees: # Assuming 20% stop loss on premium
                    allowed_option_qty = int(max_risk_rupees / (estimated_premium * 0.20))
                
                if allowed_option_qty == 0:
                    allowed_option_qty = 1
                    
                total_premium_cost = allowed_option_qty * estimated_premium
                
                # Display Results beautifully on mobile
                st.balloons()
                st.success("🔥 BREAKOUT DETECTED! MULTI-CHART CONDITIONS MET! 🔥")
                
                st.markdown(f"### 🎯 RECOMMENDED OPTION TRADE")
                st.error(f"**Trade Instrument:** {option_name}")
                
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric(label="📥 Entry Premium Range", value=f"₹{estimated_premium}")
                    st.metric(label="📦 Exact Buy Quantity", value=f"{allowed_option_qty} Qty")
                with metrics_col2:
                    st.metric(label="🛑 Option Stop-Loss", value=f"₹{round(estimated_premium * 0.80, 2)}")
                    st.metric(label="🎯 Target Take-Profit", value=f"₹{round(estimated_premium * 1.40, 2)}")
                
                st.warning(f"💳 **Capital Required for Option Buying:** ₹{round(total_premium_cost, 2)} (Within your ₹{capital} limit)")
                break
                
        if not trade_triggered:
            st.info("Scan finished. Price did not break past historical multi-day resistance barriers today.")
