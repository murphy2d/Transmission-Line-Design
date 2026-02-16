import streamlit as st
import pandas as pd
from utils.towerCalc import economic_voltage_level_calcuation,economic_voltage_level, mflimit, sil_calculation, mf_i_calculation

#set page configuration
st.set_page_config(
    page_title="Transmission Line Parameter",
    layout="wide",
    initial_sidebar_state="expanded",
)

#input design parameters

# --- INITIALIZATION ---
if "p_val" not in st.session_state:
    st.session_state.p_val = 0
if "l_val" not in st.session_state:
    st.session_state.l_val = 0
if "V" not in st.session_state:
    st.session_state.V = 0
if "Nc" not in st.session_state:
    st.session_state.Nc = 0

# --- PERSISTENCE LOGIC ---
def sync_state():
    st.session_state.p_val = st.session_state._p
    st.session_state.l_val = st.session_state._l

st.header(":orange[Design Parameters] 🗼")

global power, length, V, Nc

#input parameters for transmission line design

col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("Transmitted Power (MW)")
    power = st.number_input("Enter the power to be transmitted:", value=st.session_state.p_val, key="_p", on_change=sync_state)
    st.write(f"Power (P) = {power} MW")

with col2:
    st.subheader("Transmission Length (km)")
    length = st.number_input("Enter transmission line length:", value=st.session_state.l_val, key="_l", on_change=sync_state)
    st.write(f"Length (L) = {length} km")

st.space(size="medium")

#economic voltage level

st.subheader(":orange[Economic Voltage Level] 💰")

#economic voltage formulae

st.latex(r'''V_{eco} = 5.5\cdot \sqrt{\frac{L}{1.6} + \frac{P \cdot 1000}{N_c \cdot cos(\phi) \cdot 150}} \space kV''')

#economic voltage level calculation

col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("For Nc = 1")
    st.latex(fr"""V_{{eco}} = 5.5 \cdot \sqrt{{\frac{{{length}}}{{1.6}} + \frac{{{power} \cdot 1000}}{{{1} \cdot {0.96} \cdot 150}}}}\; kV""")
    V_eco_1 = economic_voltage_level_calcuation(power, length, 1)
    st.latex(f"V_{{eco1}} = {V_eco_1:.2f} kV")
    V1 = economic_voltage_level(V_eco_1)
    st.latex(f"V_{{1}} = {V1} kV")
    
with col2:
    st.subheader("For Nc = 2")
    st.latex(fr"""V_{{eco}} = 5.5 \cdot \sqrt{{\frac{{{length}}}{{1.6}} + \frac{{{power} \cdot 1000}}{{{2} \cdot {0.96} \cdot 150}}}}\; kV""")
    V_eco_2 = economic_voltage_level_calcuation(power, length, 2)
    st.latex(f"V_{{eco2}} = {V_eco_2:.2f} kV")
    V2 = economic_voltage_level(V_eco_2)
    st.latex(f"V_{{2}} = {V2} kV")


#mf limit
col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("MF Limit Chart 📊")
    mf_limit = pd.read_csv("data/mfLimit.csv")
    mf_limit.plot(x="Length", y="mf_Limit", kind="line", title="MF Limit vs Length", xlabel="Length (km)", ylabel="MF Limit")
    st.line_chart(mf_limit, x="Length", y="mf_Limit", x_label="Length (km)", y_label="MF Limit", width="stretch")

with col2:
    st.subheader("MF Limit Data 📊")
    st.dataframe(mf_limit, width="stretch")
    mf_limit_value = mflimit(length)
    st.write(f"***Mf Limit ({length} km)  :*** {mf_limit_value:.3f}")

#choice of voltage level and number of circuit using mf limit by figuring out SIL for both circuit options and comparing with mf limit value 

col1, col2 , col3= st.columns(3, border= True)

with col1:
    st.subheader("SIL Calculation")
    st.latex(r'''SIL = \frac{V^2}{Z_{o}} \space kV/km''')
    SIL_1 = sil_calculation(V1, 400)
    st.latex(f"SIL_{{1}} = \\frac{{{V1}^2}}{{400}} = {SIL_1:.3f} \\space kV/ohm")
    SIL_2 = sil_calculation(V2, 200)
    st.latex(f"SIL_{{2}} = \\frac{{{V2}^2}}{{200}} = {SIL_2:.3f} \\space kV/ohm")

with col2:
    st.subheader("mfᵢ Calculation")
    st.latex(r'''mf_i = \frac{P}{SILᵢ}''')
    mf_i_1 = mf_i_calculation(power, SIL_1)
    st.latex(f"mf_{{1}} = \\frac{{{power}}}{{{SIL_1:.3f}}} = {mf_i_1:.3f}")
    mf_i_2 = mf_i_calculation(power, SIL_2)
    st.latex(f"mf_{{2}} = \\frac{{{power}}}{{{SIL_2:.3f}}} = {mf_i_2:.3f}")

with col3:
    V = 0
    Nc = 0
    st.subheader("Design Decision")
    if mf_i_1 > mf_limit_value and mf_i_2 < mf_limit_value:
        st.write(f"Since, **mf₁ > mf ₗᵢₘᵢₜ** and **mf₂ < mf ₗᵢₘᵢₜ**, we choose V₂ and Nc = 2")
        V = V2
        Nc = 2
    elif mf_i_1 < mf_limit_value and mf_i_2 > mf_limit_value:
        st.write(f"Since, **mf₁ < mf ₗᵢₘᵢₜ** and **mf₂ > mf ₗᵢₘᵢₜ**, we choose V₁ and Nc = 1")
        V = V1
        Nc = 1
    elif mf_i_1 and mf_i_2 < mf_limit_value:
        if V1 == V2:
            st.write("Since, mf₁ and mf₂ < mf ₗᵢₘᵢₜ and V₁=V₂ ,we choose V₁ and Nc = 1")
            V = V1
            Nc = 1
        elif V1 != V2:
            PM1 = mf_limit_value*SIL_1-power
            PM2 = mf_limit_value*SIL_2-power
            st.write(f"PM₁ = mfₗᵢₘᵢₜ X SIL₁ - P = {mf_limit_value:.3f} * {SIL_1:.3f} - {power} = {PM1:.3f}")
            st.write(f"PM₂ = mfₗᵢₘᵢₜ X SIL₂ - P = {mf_limit_value:.3f} * {SIL_2:.3f} - {power} = {PM2:.3f}")
            if PM1 > PM2:
                st.write(f"Since, mf₁ and mf₂ < mf ₗᵢₘᵢₜ and PM₁ > PM₂ ,we choose V₂ and Nc = 2")
                V = V2
                Nc = 2
            elif PM2 > PM1:
                st.write(f"Since, mf₁ and mf₂ < mf ₗᵢₘᵢₜ and PM₂ > PM₁ ,we choose V₁ and Nc = 1")
                V = V1
                Nc = 1
        
    else:
        st.write("Neither option is feasible based on the MF limit. You may need to reconsider your design parameters and increase the voltage level. ")

    st.write(f"**Chosen Voltage Level (V) :** {V} kV")
    st.write(f"**Chosen Number of Circuits (Nc) :** {Nc}")
    
    #set voltage level and number of circuits in session state for use in other pages
    st.session_state.V = V
    st.session_state.Nc = Nc







