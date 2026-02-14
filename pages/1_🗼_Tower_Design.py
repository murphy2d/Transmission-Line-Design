import streamlit as st
import pandas as pd
from utils.towerCalc import economic_voltage_level, mflimit

#input design parameters

# --- INITIALIZATION (Add this here) ---
if "p_val" not in st.session_state:
    st.session_state.p_val = 0
if "l_val" not in st.session_state:
    st.session_state.l_val = 0

# --- PERSISTENCE LOGIC ---
def sync_state():
    st.session_state.p_val = st.session_state._p
    st.session_state.l_val = st.session_state._l

st.header("Transmission Line Parameters 🗼")

col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("Transmitted Power (MW)")
    power = st.number_input("Enter the power to be transmitted:", value=st.session_state.p_val, key="_p", on_change=sync_state)
    st.write(f"Power (P) = {power} MW")

with col2:
    st.subheader("Transmission Length (km)")
    length = st.number_input("Enter transmission line length:", value=st.session_state.l_val, key="_l", on_change=sync_state)
    st.write(f"Length (L) = {length} km")

#economic voltage level

st.subheader("Economic Voltage Level 💰")

#economic voltage formulae

st.latex(r'''V_{eco} = 5.5\cdot \sqrt{\frac{L}{1.6} + \frac{P \cdot 1000}{N_c \cdot cos(\phi) \cdot 150}} \space kV''')

#economic voltage level calculation

col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("For Nc = 1")
    st.latex(fr"""V_{{eco}} = 5.5 \cdot \sqrt{{\frac{{{length}}}{{1.6}} + \frac{{{power} \cdot 1000}}{{{1} \cdot {0.96} \cdot 150}}}}\; kV""")
    V_eco_1 = economic_voltage_level(power, length, 1)
    st.write(f"V_eco_1 = {V_eco_1:.2f} kV")
    
with col2:
    st.subheader("For Nc = 2")
    st.latex(fr"""V_{{eco}} = 5.5 \cdot \sqrt{{\frac{{{length}}}{{1.6}} + \frac{{{power} \cdot 1000}}{{{2} \cdot {0.96} \cdot 150}}}}\; kV""")
    V_eco_2 = economic_voltage_level(power, length, 2)
    st.write(f"V_eco_2 = {V_eco_2:.2f} kV")

#mf limit
col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("MF Limit Chart 📊")
    mf_limit = pd.read_csv("TnDProject\data\mfLimit.csv")
    mf_limit.plot(x="Length", y="mf_Limit", kind="line", title="MF Limit vs Length", xlabel="Length (km)", ylabel="MF Limit")
    st.line_chart(mf_limit, x="Length", y="mf_Limit", x_label="Length (km)", y_label="MF Limit", width="stretch")

with col2:
    st.subheader("MF Limit Data 📊")
    st.dataframe(mf_limit, width="stretch")
    mf_limit_value = mflimit(length)
    st.write(f"***Mf Limit ({length}) km  :*** {mf_limit_value:.3f}")