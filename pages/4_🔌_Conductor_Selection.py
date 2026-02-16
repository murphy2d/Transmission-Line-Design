import streamlit as st
import pandas as pd
import numpy as np
import math
from utils.conductorCalc import lineCurrent, conductor_selection, resistance_20_degree, resistance_75_degree, power_loss_calculation_MW, efficiency_calculation

#set page configuration
st.set_page_config(
    page_title="Conductor Selection",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "V" not in st.session_state:    
    st.session_state.V = 0 #default value for System Voltage (V)

if "Nc" not in st.session_state:    
    st.session_state.Nc = 0 #default value for Number of circuit(Nc)

if "efficiency_standard" not in st.session_state:    
    st.session_state.efficiency_standard = 94 #default value for efficiency

if "p_val" not in st.session_state:    
    st.session_state.p_val = 0 #default value for Power(P)

if "l_val" not in st.session_state:    
    st.session_state.l_val = 0 #default value for length(l)

if "pfTL" not in st.session_state:    
    st.session_state.pfTL = 0.96 #default value for TL power factor(cos phi)

if "ambient_temp" not in st.session_state:    
    st.session_state.ambient_temp = 40 #default value for ambient temperature


def sync_state():
    st.session_state.p_val = st.session_state._p
    st.session_state.l_val = st.session_state._l
    st.session_state.Nc = st.session_state._Nc
    st.session_state.efficiency = st.session_state._efficiency
    st.session_state.pfTL = st.session_state._pfTL

#Conductor selection
st.header(":orange[Conductor Selection] 🔌")

#import acsr conductor table
acsr_conductor_table = pd.read_csv("TnDProject/data/ACSRconductorTable.csv")

#create expander for conductor table
with st.expander("ACSR Conductor Table IS:398-1976"):
    st.dataframe(acsr_conductor_table, hide_index=True)

st.space("small")

#The conductor should fullfill both electrical and mechanical+economic requirement
st.caption(" *The conductor should meet following requirements:* ")

tab1, tab2 = st.tabs(["**Electrical Requirement**", "**Economic and Mechanical Requirement**"], width="stretch")

with tab1:

    #CURRENT CARRYING CAPACITY
    st.subheader("Current Carrying Capacity")

    col1, col2 = st.columns(2, border=True)

    with col1:

        st.subheader("Parameters")
        power = st.number_input("Transmitted Power (MW)", value=st.session_state.p_val, key="_p", on_change=sync_state)
        length = st.number_input("Line Length (km)", value=st.session_state.l_val, key="_l", on_change=sync_state)
        Nc = st.number_input("Number of Circuit (Nc)", value= st.session_state.Nc, key="_Nc",on_change=sync_state)
        V= st.number_input("Enter Voltage Level (kV))", value= st.session_state.V)
        pfTL = st.number_input("Enter Transmission line Power factor (cos Ø)", value= st.session_state.pfTL, key="_pfTL", on_change=sync_state)
        
        options = (40, 45)

        ambient_temp = st.selectbox("Choose Ambient Temperature (θc)", options, index=options.index(st.session_state.ambient_temp), format_func=lambda x: f"{x} °C", accept_new_options=False, key="ambient_temp")
        # st.write(ambient_temp)

        
    #line current calculation and conductor selection

    with col2:

        st.subheader("Line Current Calculation")
        line_current = lineCurrent(power, Nc, V, pfTL)
        st.latex(fr""" Line \, Current = \frac{{P}}{{ \sqrt{3} \cdot V \cdot cos(\phi) \cdot Nc }} """)
        st.latex(fr""" Line \, Current = \frac{{{power} \cdot 10^6 }}{{ \sqrt{3} \cdot {V} \cdot 10^3 \cdot {pfTL} \cdot {Nc} }} = {line_current:.2f} A""")

        st.space("small")

        #conductor selection

        conductor_selected, conductor_rating = conductor_selection(line_current, ambient_temp)
        
        if conductor_selected != None:
            st.write(f" *The conductor of rating greater than {line_current:.2f} A is of* {conductor_selected} *with rating of {conductor_rating} Ampere*")
            st.space("small")
            st.write(f"Selected Conductor = **{conductor_selected}**")
        else:
            st.write (f" No conductor is available. You need to opt to bundle conductor ")



    st.space("medium")
    #EFFICIENCY

    st.subheader("Efficiency")

    col1, col2 = st.columns(2, border=True)

    with col1:

        st.subheader("Efficiency Parameters")
        st.write("")

        st.write(f"For {conductor_selected} Conductor, ")

        resistance_20_perLength = resistance_20_degree(ambient_temp, conductor_selected)
        st.latex(rf"Resistance \, at \, 20 °C \, per \, km  = {resistance_20_perLength} \, Ω/km")

        resistance_75_perLength, resistance_75 = resistance_75_degree(resistance_20_perLength, length)
        st.latex(rf"Resistance \, at \, 75 °C \, per \, km = {resistance_20_perLength} \cdot [1 + 0.004 \cdot (75-20)] =  {resistance_75_perLength:.3f} \, Ω/km")
        st.latex(rf"Resistance \, at \, 75 °C = {resistance_75:.3f} \, Ω")

        power_loss_MW = power_loss_calculation_MW(line_current, resistance_75, Nc)
        st.latex(rf"Power \, loss = 3 \cdot {line_current:.2f}^2 \cdot {resistance_75:.2f} \cdot {Nc} \, Watt ")
        st.latex(rf"Power \, loss = {power_loss_MW:.2f} \, MW")

        efficiency = efficiency_calculation(power_loss_MW, power)
        st.latex(rf"Efficiency \, (η) = (1 + \frac{{{power_loss_MW:.2f}}}{{{power}}}) \cdot 100 \, \%")
        st.latex(rf"Efficiency \, (η) = {efficiency:.2f} \, \%")


    with col2:
        
        st.subheader("Efficiency Analysis")
        st.write("")

        efficiency_standard = st.number_input("Efficiency Standard (η_s)", value= st.session_state.efficiency_standard, key="_efficiency",on_change=sync_state)
        st.write("")

        st.latex(rf"Condition: \, Efficiency \, (η) > Efficiency \, standard \, (η_s)")

        st.write("")

        if efficiency > efficiency_standard:
            st.write(f"Since, {efficiency:.2f} % > {efficiency_standard} %")
            st.write(f"Selected Conductor = **{conductor_selected}**")
        
        else:
            st.write(f"Since, {efficiency:.2f} % < {efficiency_standard} %")
            st.write(f"Size of conductor is increased and efficiency is calculated again. Efficiency is tabulated below to find appropriate conductor.")

            #expander for efficiency calculation table
            with st.expander("Efficiency Calculation Table"):
                
                efficiency_table_data = {
                    "Conductor": [conductor_selected],
                    "R_20 (Ω/Km)": [resistance_20_perLength],
                    "Current Carrying Capacity": [conductor_rating],
                    "R_75 (Ω)": [resistance_75],
                    "Power Loss(MW)": [power_loss_MW],
                    "Efficiency (η)": [efficiency]
                }

                efficiency_table = pd.DataFrame(efficiency_table_data)

                index = acsr_conductor_table.index[acsr_conductor_table["Code_Name"] == conductor_selected][0]
                rows_no = acsr_conductor_table.shape[0]
                
                for i in range(index+1, rows_no):

                    conductor_selected = acsr_conductor_table.iloc[i]["Code_Name"]
                    resistance_20_perLength = resistance_20_degree(ambient_temp, conductor_selected)

                    if ambient_temp == 40:
                        conductor_rating = acsr_conductor_table.iloc[i]["Current_40C_A"]
                    elif ambient_temp == 45:
                        conductor_rating = acsr_conductor_table.iloc[i]["Current_45C_A"]
                    
                    resistance_75_perLength, resistance_75 = resistance_75_degree(resistance_20_perLength, length)
                    power_loss_MW = power_loss_calculation_MW(line_current, resistance_75, Nc)
                    efficiency = efficiency_calculation(power_loss_MW, power)

                    if efficiency < efficiency_standard:
                        
                        concat_efficiency_data = {
                        "Conductor": [conductor_selected],
                        "R_20 (Ω/Km)": [resistance_20_perLength],
                        "Current Carrying Capacity": [conductor_rating],
                        "R_75 (Ω)": [resistance_75],
                        "Power Loss(MW)": [power_loss_MW],
                        "Efficiency (η)": [efficiency]
                        }

                        concat_efficiency_table = pd.DataFrame(concat_efficiency_data)

                        efficiency_table = pd.concat([efficiency_table, concat_efficiency_table])
                        
                        

                    else:
                        concat_efficiency_data = {
                        "Conductor": [conductor_selected],
                        "R_20 (Ω/Km)": [resistance_20_perLength],
                        "Current Carrying Capacity": [conductor_rating],
                        "R_75 (Ω)": [resistance_75],
                        "Power Loss(MW)": [power_loss_MW],
                        "Efficiency (η)": [efficiency]
                        }

                        concat_efficiency_table = pd.DataFrame(concat_efficiency_data)

                        efficiency_table = pd.concat([efficiency_table, concat_efficiency_table])
                        break
                
                st.dataframe(efficiency_table, hide_index=True)

            st.write(f"Selected Conductor = {conductor_selected}")




with tab2:

    st.header("Coming Soon!!!")