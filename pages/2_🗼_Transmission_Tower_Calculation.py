import streamlit as st
import pandas as pd
from utils.towerCalc import air_clearance_calculation, crossarm_length_calculation, insulated_string_length_calculation, distance_between_conductors_calculation, distance_between_earth_wire_and_top_conductor_calculation, distance_of_earth_wire_from_top_most_cross_arm_calculation


#global variables for voltage level and number of circuits
V = st.session_state.V
Nc = st.session_state.Nc

#earth wire design

st.header(":orange[Earth Wire Selection] 🌩️")

col1, col2 = st.columns(2, border= True)

with col1:
    st.subheader("Earth Wire Selection based on Voltage Level")
    earth_wire_options = pd.DataFrame({
        "Voltage Level (kV)": ["Low Voltage (upto 66 kV)", "Medium Voltage (132 - 220 kV)", "High Voltage (> 220 kV)"],
        "Recommended Earth Wire": ["Single Earth Wire", "Single Earth Wire for Nc =1 and Double Earth Wire for Nc = 2", "Double Earth Wire"]})
    st.dataframe(earth_wire_options)

with col2:
    st.subheader("Recommended Earth Wire")
    if V <= 66:
        st.write("Based on the chosen voltage level, a \n\n**Single Earth Wire** is recommended.")
    elif 132 <= V <= 220:
        if Nc == 1:
            st.write("Based on the chosen voltage level and number of circuits, a \n\n**Single Earth Wire** is recommended.")
        elif Nc == 2:
            st.write("Based on the chosen voltage level and number of circuits, \n\n**Double Earth Wire** is recommended.")
    elif V > 220:
        st.write("Based on the chosen voltage level, \n\n**Double Earth Wire** is recommended.")

st.space(size="medium")

#transmission tower design

# --- INITIALIZATION ---
if "swing_angle" not in st.session_state:
    st.session_state.swing_angle = 0

# --- PERSISTENCE LOGIC ---
def sync_state():
    st.session_state.swing_angle = st.session_state.swing

st.header(":orange[Transmission Tower Design] 🏗️")

col1, col2 = st.columns(2, border= True)

with col1:
    if Nc == 1:
        st.image("data/TransmissionLineNc1.png", caption="Transmission Tower for Single Circuit", width="stretch")
    elif Nc == 2:
        st.image("data/TransmissionLineNc2.png", caption="Transmission Tower for Double Circuit", width="stretch")
    else:
        st.image("data/TransmissionLineNc2.png", caption="Transmission Tower for Double Circuit", width="stretch")

with col2:
    st.subheader("Tower Parameter Calculation")
    swing_angle = st.number_input("Enter the swing angle (degrees):", value=st.session_state.swing_angle, key="swing", on_change=sync_state)
    st.write(f"Swing Angle (θ) = {swing_angle} degrees")

    air_clearance = air_clearance_calculation(V)
    st.latex(fr"""Air \, Clearance \, (a) = 1 \cdot {V} \cdot 1.1 \cdot \left( \frac{{\sqrt{2}}}{{\sqrt{3}}} \right) + 30 = {air_clearance:.2f} \; cm""")
    
    crossarm_length = crossarm_length_calculation(swing_angle, air_clearance)
    st.latex(fr"""Crossarm \, Length \, (cl) = {air_clearance:.2f} \cdot \left( 1 + \tan\left( {swing_angle}^o \right) \right) = {crossarm_length:.2f} \; cm""")
    
    insulated_string_length = insulated_string_length_calculation(swing_angle, air_clearance)
    st.latex(fr"""Insulated \, String \, Length \, (l) = \frac{{{air_clearance:.2f}}}{{\cos\left( {swing_angle}^o \right)}} = {insulated_string_length:.2f} \; cm""")
    
    distance_between_conductors = distance_between_conductors_calculation(insulated_string_length, crossarm_length, air_clearance)
    st.latex(fr"""Distance \, between \, Conductors \, (y) = \frac{{{insulated_string_length:.2f} + {air_clearance:.2f}}}{{\sqrt{{1 - 0.3^2 \cdot \left( \frac{{{insulated_string_length:.2f} + {air_clearance:.2f}}}{{{crossarm_length:.2f}}} \right)^2}}}} = {distance_between_conductors:.2f} \; cm""")

    tower_width = 1.5 * air_clearance
    st.latex(fr"""Tower \, Width \, (b) = 1.5 \cdot {air_clearance:.2f} = {tower_width:.2f} \; cm""")

    ROW = 2*crossarm_length + tower_width
    st.latex(fr"""Right \, of \, Way \, (ROW) = 2 \cdot {crossarm_length:.2f} + {tower_width:.2f} = {ROW:.2f} \; cm""")

    d_dash = distance_between_earth_wire_and_top_conductor_calculation(crossarm_length, tower_width, Nc)  
    if Nc == 1:
        st.latex(fr"""Distance \, between \, Earth \, Wire \, and \, Top \, Conductor \, (d') = \sqrt{3} \cdot \left( {crossarm_length:.2f} - \frac{{{tower_width:.2f}}}{2} \right) = {d_dash:.2f} \; cm""") 
    elif Nc == 2:
        st.latex(fr"""Distance \, between \, Earth \, Wire \, and \, Top \, Conductor \, (d') = \sqrt{3} \cdot {crossarm_length:.2f} = {d_dash:.2f} \; cm """)

    d = distance_of_earth_wire_from_top_most_cross_arm_calculation(d_dash, insulated_string_length)

    st.latex(fr"""d = d' - l = {d_dash:.2f} - {insulated_string_length:.2f} = {d:.2f} \; cm""")

