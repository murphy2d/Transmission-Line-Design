import streamlit as st
import pandas as pd
import numpy as np
import math
import cmath
from utils.conductorCalc import lineCurrent, conductor_selection, resistance_20_degree, resistance_75_degree, power_loss_calculation_MW, efficiency_calculation, gmr, GMRandGMDparameters, GMR_2, GMD_2, GMR_1, GMD_1, plot_efficiency_trend, inductance_L, capacitance_C, impedance_Z, susceptance_Y, abc_parameters, currentReceiving, to_polar

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

if "bundle_conductor_number" not in st.session_state:    
    st.session_state.bundle_conductor_number = 1 #default value for bundle_conductor_number

if "bundle_button" not in st.session_state:    
    st.session_state.bundle_button = False #default value for bundle_toggle

if "bundle_conductor_spacing" not in st.session_state:    
    st.session_state.bundle_conductor_spacing = 30 #default value for bundle_conductor_spacing


def sync_state():
    st.session_state.p_val = st.session_state._p
    st.session_state.l_val = st.session_state._l
    st.session_state.Nc = st.session_state._Nc
    # st.session_state.efficiency = st.session_state._efficiency
    st.session_state.pfTL = st.session_state._pfTL
    st.session_state.bundle_conductor_number = st.session_state.bundle_conductor_number
    st.session_state.bundle_button = st.session_state.bundle_toggle

    if "_bundle_conductor_spacing" in st.session_state:
        st.session_state.bundle_conductor_spacing = st.session_state._bundle_conductor_spacing

#Conductor selection
st.header(":orange[Conductor Selection] 🔌")

#import acsr conductor table
acsr_conductor_table = pd.read_csv("data/ACSRconductorTable.csv")

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
        
        #ask user if to use bundle conductor
        bundle_button = st.toggle("Use bundle conductor? (Nb)", key="bundle_toggle",value= st.session_state.bundle_button, on_change=sync_state)
        if bundle_button:
            
            bundle_conductor_number = st.number_input("Enter number of sub-conductor in a bundle (Max: 4)", value=st.session_state.bundle_conductor_number, key="bundle_conductor_number", on_change=sync_state, max_value=4)

        else:
            bundle_conductor_number = 1
        
    #line current calculation and conductor selection

    with col2:

        st.subheader("Line Current Calculation")
        line_current = lineCurrent(power, Nc, V, pfTL, bundle_conductor_number)
        st.latex(fr""" Line \, Current = \frac{{P}}{{ \sqrt{3} \cdot V \cdot cos(\phi) \cdot Nc \cdot Nb}} """)
        st.latex(fr""" Line \, Current = \frac{{{power} \cdot 10^6 }}{{ \sqrt{3} \cdot {V} \cdot 10^3 \cdot {pfTL} \cdot {Nc} \cdot {bundle_conductor_number}}} = {line_current:.2f} A""")

        st.space("small")

        #conductor selection

        conductor_selected, conductor_rating = conductor_selection(line_current, ambient_temp)
        
    if conductor_selected != None:

        with col2:
            st.write(f" *The conductor of rating greater than {line_current:.2f} A is of* {conductor_selected} *with rating of {conductor_rating} Ampere*")
            st.space("small")
            st.write(f"Selected Conductor = **{conductor_selected}**")

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

            power_loss_MW = power_loss_calculation_MW(line_current, resistance_75, Nc, bundle_conductor_number)
            st.latex(rf"Power \, loss = 3 \cdot line current^2 \cdot resistance\_75 \cdot Nc \cdot Nb \, \, Watt ")
            st.latex(rf"Power \, loss = 3 \cdot {line_current:.2f}^2 \cdot {resistance_75:.2f} \cdot {Nc} \cdot {bundle_conductor_number} \, Watt ")
            st.latex(rf"Power \, loss = {power_loss_MW:.2f} \, MW")

            efficiency = efficiency_calculation(power_loss_MW, power)
            st.latex(rf"Efficiency \, (η) = (1 + \frac{{{power_loss_MW:.2f}}}{{{power}}}) \cdot 100 \, \%")
            st.latex(rf"Efficiency \, (η) = {efficiency:.2f} \, \%")


        with col2:
            
            st.subheader("Efficiency Analysis")
            st.write("")

            efficiency_standard = st.number_input("Efficiency Standard (η_s)", value= st.session_state.efficiency_standard, key="_efficiency",on_change=sync_state)
            st.write("")

            st.latex(rf"Required \,\, Condition: \, Efficiency \, (η) > Efficiency \, standard \, (η_s)")

            st.write("")

            if efficiency > efficiency_standard:
                st.write(f"Since, {efficiency:.2f} % > {efficiency_standard} %")
                st.write(f"Selected Conductor = **{conductor_selected}**")
            
            else:
                st.write(f"Since, {efficiency:.2f} % < {efficiency_standard} %")
                st.write(" *Size of conductor is increased and process is repeated to calculate efficiency. The process is repeated till the required condition is fulfilled. The process is tabulated below.* ")

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
                    
                    for i in range(index + 1, rows_no):
                        conductor_selected = acsr_conductor_table.iloc[i]["Code_Name"]
                        
                        # 1. Determine rating
                        if ambient_temp == 40:
                            conductor_rating = acsr_conductor_table.iloc[i]["Current_40C_A"]
                        elif ambient_temp == 45:
                            conductor_rating = acsr_conductor_table.iloc[i]["Current_45C_A"]
                        else:
                            conductor_rating = None

                        #Skip if rating is None
                        if conductor_rating is None or pd.isna(conductor_rating) or conductor_selected == "Fox":
                            continue 

                        resistance_20_perLength = resistance_20_degree(ambient_temp, conductor_selected)
                        resistance_75_perLength, resistance_75 = resistance_75_degree(resistance_20_perLength, length)
                        power_loss_MW = power_loss_calculation_MW(line_current, resistance_75, Nc, bundle_conductor_number)
                        efficiency = efficiency_calculation(power_loss_MW, power)

                        #Prepare data
                        concat_efficiency_data = {
                            "Conductor": [conductor_selected],
                            "R_20 (Ω/Km)": [resistance_20_perLength],
                            "Current Carrying Capacity": [conductor_rating],
                            "R_75 (Ω)": [resistance_75],
                            "Power Loss(MW)": [power_loss_MW],
                            "Efficiency (η)": [efficiency]
                        }
                        
                        efficiency_table = pd.concat([efficiency_table, pd.DataFrame(concat_efficiency_data)])

                        #Stop the loop if we've reached the standard
                        if efficiency >= efficiency_standard:
                            break

                
                    st.dataframe(efficiency_table, hide_index=True)

                if not efficiency_table.empty:
                    st.write("📈 Efficiency vs. Loss Analysis")
                    fig = plot_efficiency_trend(efficiency_table)
                    st.pyplot(fig)


                if efficiency < efficiency_standard:
                    st.write("There is no avaible conductor to get efficiency greater than 94%. So, increase number of sub-conductor in the bundle.")
                else:
                    st.write(f"Selected Conductor = {conductor_selected}")


    else:
        st.write (f"No conductor is available. You need to opt to bundle conductor ")



    #VOLTAGE REGULATION
    st.space("medium")
    st.subheader("Voltage Regulation")


    ROW = st.session_state.ROW
    y = st.session_state.y
    
    diameter_of_conductor = acsr_conductor_table.loc[acsr_conductor_table["Code_Name"] == conductor_selected, "Conductor_Dia_mm"].iloc[0]
    radius_of_conductor = diameter_of_conductor/2

    gmr_conductor_L, gmr_conductor_C = gmr(radius_of_conductor)


    #GMR and GMD  parameter calculation
    GMRandGMD_parameters = GMRandGMDparameters(ROW, y)

    col1, col2 = st.columns(2, border=True)
    #Space between bundle in bundle conductor
    with col1:

        st.subheader("Parameters")
        st.write("")

        if bundle_conductor_number!= 1:
            bundle_conductor_spacing = st.number_input("Enter spacing between sub-conductor in a bundle (cm)", value= st.session_state.bundle_conductor_spacing, key="_bundle_conductor_spacing", on_change=sync_state)

        else:
            bundle_conductor_spacing = st.session_state.bundle_conductor_spacing
    #GMR and GMD CALCULATION

    if Nc == 1:
        GMR_L , GMR_C = GMR_1(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, bundle_conductor_spacing)
        GMD = GMD_1(y, ROW)

    elif Nc==2:
        
        GMR_L, GMR_C = GMR_2(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, GMRandGMD_parameters, bundle_conductor_spacing)
        GMD = GMD_2(GMRandGMD_parameters)
        

    with col1:

        if Nc == 2:
            
            df = pd.DataFrame(GMRandGMD_parameters.items(), columns=["Parameter", "Distance (cm)"])
            df["Distance (cm)"] = df["Distance (cm)"].round(2)

            sub_col_left, sub_col_mid, sub_col_right = st.columns([1, 3, 1])

            with sub_col_mid:
                st.image("data/ConductorConfigNc2.png", caption="Fig: Conductor Configuration for Nc = 2", width="content")
            st.dataframe(df, hide_index=True)

        if Nc == 1:

            GMRandGMD_parameter_Nc1 = {
                "Dab" : math.sqrt(pow(y/2,2) + pow(ROW,2)),
                "Dac" : y,
                "Dba" : math.sqrt(pow(y/2,2) + pow(ROW,2)),
                "Dbc" : math.sqrt(pow(y/2,2) + pow(ROW,2)),
                "Dca" : y,
                "Dcb" : math.sqrt(pow(y/2,2) + pow(ROW,2))
            }

            df = pd.DataFrame(GMRandGMD_parameter_Nc1.items(), columns=["Parameter", "Distance (cm)"])
            df["Distance (cm)"] = df["Distance (cm)"].round(2)

            sub_col_left, sub_col_mid, sub_col_right = st.columns([1, 3, 1])

            with sub_col_mid:
                st.image("data/conductorConfigNc1.png", caption="Fig: Conductor Configuration for Nc = 1", width="content")

            st.dataframe(df, hide_index=True)

            #GMD and GMR printing

        st.latex(rf"GMD = {GMD:.2f} \, cm ")
        st.latex(rf"GMR_L = {GMR_L:.2f} \, cm")
        st.latex(rf"GMR_C = {GMR_C:.2f} \, cm")

    
    with col2:

        st.subheader("Calculation")
        st.write("")

        

        #Inducatance and Capacitance calculation

        inductance = inductance_L(GMD, GMR_L, length)
        st.latex(rf"L = 2 \cdot 10^{{-7}} \cdot ln \frac{{GMD}}{{GMR_L}} = 2 \cdot 10^{{-7}} \cdot \ln \frac{{{GMD:.2f}}}{{{GMR_L:.2f}}} = {inductance:.2e} \, H/km")

        capacitance = capacitance_C(GMD, GMR_C, length)
        st.latex(rf"C = \frac{{2 \cdot \pi \cdot ϵ_o}}{{ln \frac{{GMD}}{{GMR_C}}}} = \frac{{2 \cdot \pi \cdot ϵ_o}}{{ln \frac{{{GMD:.2f}}}{{{GMR_C:.2f}}}}} = {capacitance:.2e} \, F/km")

        st.latex(rf"R_{{75}} = {resistance_75:.2f} \, ohm")
        
        #impedance of line
        impedance = impedance_Z(resistance_75, inductance)
        st.latex(rf"Z =R_{{75}} + 2 \pi f L ={resistance_75:.2f} + 2 \cdot \pi \cdot 50 \cdot ({inductance:.2e}) = {impedance:.2f} = {to_polar(impedance)} \, ohm")

        #susceptance of line
        susceptance = susceptance_Y(capacitance)
        st.latex(rf"Y =j \cdot 2 \pi f C =j \cdot 2 \cdot \pi \cdot 50 \cdot ({capacitance:.2e}) = j({susceptance.imag:.2e}) = {to_polar(susceptance)} \, siemens")

        #ABC parameters
        A,B,C = abc_parameters(impedance, susceptance)  

        st.latex(rf"A = 1 + \frac{{YZ}}{{2}} = {A:.6f} = {to_polar(A)}")
        st.latex(rf"B = Z = {B:.5f} = {to_polar(B)}")
        st.latex(rf"C = Y \cdot (1 + \frac{{YZ}}{{4}}) = {C:.6f} = {to_polar(C)}")


        #receiving current
        current_receiving = currentReceiving(line_current, pfTL)
        st.latex(rf"I_R = {current_receiving:.2f} = {to_polar(current_receiving)} \, A")

        #receiving end voltage per phase
        voltage_receiving = complex((V*1000)/math.sqrt(3), 0)
        st.latex(rf"V_R = {(voltage_receiving/1000):.2f} = {to_polar(voltage_receiving/1000)}\, kV")

        #sending end voltage
        voltage_sending = (A * voltage_receiving + B * current_receiving)/1000
        st.latex(rf"V_S = A \cdot V_R + B \cdot I_R = {voltage_sending:.2f} = {to_polar(voltage_sending)} \, kV")

        #Voltage regulation calulation
        VR_calc = (((abs(voltage_sending*1000))/abs(A) - abs(voltage_receiving))/abs(voltage_receiving)) * 100
        st.latex(fr"V.R =\frac{{\frac{{V_S}}{{A}} - V_R}}{{V_R}} = {VR_calc:.2f} \, \%")

    

    with st.container(border=True):
        
        st.subheader("Voltage Regulation Analysis")
        st.write("")

        st.latex(rf"Required \,\, Condition: \, V.R  < 10 \%")
        st.space("small")
        
        if VR_calc < 10:
            st.write(f"Since, V.R is less than 10 %. Conductor ({conductor_selected}) with current rating of {conductor_rating} A, satisfies the condition. ")
        
        else:
            st.write(f"Since, V.R is not less than 10%. We need to increase the conductor size and re-evaluate V.R again, till it satisfies the condition. The process is tabulated as below.")
            
            with st.expander("Voltage Regualtion Calculation Table"):

                VR_table = pd.DataFrame({
                    "Conductor" : [conductor_selected],
                    "Current Rating (A)" : [conductor_rating],
                    "Conductor Radius (mm)" : [radius_of_conductor],
                    "GMD (cm)" : [GMD],
                    "GMR_L (cm)" : [GMR_L],
                    "GMR_C (cm)" : [GMR_C],
                    "Inductance (H)" : [inductance],
                    "Capacitance (F)" : [capacitance],
                    "Resistance at 75 (ohm)" : [resistance_75],
                    "Impedance (Z)" : [impedance],
                    "Susceptance (Y)" : [susceptance],
                    "A" : [A],
                    "B" : [B],
                    "I_R" : [current_receiving],
                    "V_R" : [voltage_receiving/1000],
                    "V_S" : [voltage_sending],
                    "V.R %" : [VR_calc]
                })

                index = acsr_conductor_table.index[acsr_conductor_table["Code_Name"] == conductor_selected][0]
                rows_no = acsr_conductor_table.shape[0]
                    
                for i in range(index + 1, rows_no):
                    conductor_selected = acsr_conductor_table.iloc[i]["Code_Name"]
                        
                    # 1. Determine rating
                    if ambient_temp == 40:
                        conductor_rating = acsr_conductor_table.iloc[i]["Current_40C_A"]
                    elif ambient_temp == 45:
                        conductor_rating = acsr_conductor_table.iloc[i]["Current_45C_A"]
                    else:
                        conductor_rating = None

                    #Skip if rating is None
                    if conductor_rating is None or pd.isna(conductor_rating) or conductor_selected == "Fox":
                        continue 

                    resistance_20_perLength = resistance_20_degree(ambient_temp, conductor_selected)
                    resistance_75_perLength, resistance_75 = resistance_75_degree(resistance_20_perLength, length)

                    diameter_of_conductor = acsr_conductor_table.loc[acsr_conductor_table["Code_Name"] == conductor_selected, "Conductor_Dia_mm"].iloc[0]
                    radius_of_conductor = diameter_of_conductor/2

                    gmr_conductor_L, gmr_conductor_C = gmr(radius_of_conductor)

                    if Nc == 1:
                        GMR_L , GMR_C = GMR_1(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, bundle_conductor_spacing)
                        GMD = GMD_1(y, ROW)

                    elif Nc==2:
        
                        GMR_L, GMR_C = GMR_2(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, GMRandGMD_parameters, bundle_conductor_spacing)
                        GMD = GMD_2(GMRandGMD_parameters)

                    inductance = inductance_L(GMD, GMR_L, length)
                    capacitance = capacitance_C(GMD, GMR_C, length)
                    impedance = impedance_Z(resistance_75, inductance)
                    susceptance = susceptance_Y(capacitance)
                    A,B,C = abc_parameters(impedance, susceptance)
                    current_receiving = currentReceiving(line_current, pfTL)
                    voltage_receiving = complex((V*1000)/math.sqrt(3), 0)
                    voltage_sending = (A * voltage_receiving + B * current_receiving)/1000
                    VR_calc = (((abs(voltage_sending*1000))/abs(A) - abs(voltage_receiving))/abs(voltage_receiving)) * 100

                    #new data
                    concat_VR_table = pd.DataFrame({
                        "Conductor" : [conductor_selected],
                        "Current Rating (A)" : [conductor_rating],
                        "Conductor Radius (mm)" : [radius_of_conductor],
                        "GMD (cm)" : [GMD],
                        "GMR_L (cm)" : [GMR_L],
                        "GMR_C (cm)" : [GMR_C],
                        "Inductance (H)" : [inductance],
                        "Capacitance (F)" : [capacitance],
                        "Resistance at 75 (ohm)" : [resistance_75],
                        "Impedance (Z)" : [impedance],
                        "Susceptance (Y)" : [susceptance],
                        "A" : [A],
                        "B" : [B],
                        "I_R" : [current_receiving],
                        "V_R" : [voltage_receiving/1000],
                        "V_S" : [voltage_sending],
                        "V.R %" : [VR_calc]
                    })

                    VR_table = pd.concat([VR_table, pd.DataFrame(concat_VR_table)])

                    #Stop the loop if we've reached the standard
                    if VR_calc < 10:
                        break
                
                
                # Convert complex numbers to a clean string format: "real + imag j"
                complex_cols = ["Impedance (Z)", "Susceptance (Y)", "A", "B", "I_R", "V_R", "V_S"]
                for col in complex_cols:
                    VR_table[col] = VR_table[col].apply(lambda x: f"{x.real:.2f} + {x.imag:.2f}j" if isinstance(x, complex) else x)

                st.dataframe(VR_table.style.format({
                    "Current Rating (A)": "{:.1f}",
                    "Conductor Radius (mm)": "{:.2f}",
                    "GMD (cm)": "{:.2f}",
                    "GMR_L (cm)": "{:.4f}",
                    "GMR_C (cm)": "{:.4f}",
                    "Inductance (H)": "{:.4e}",
                    "Capacitance (F)": "{:.4e}",
                    "Resistance at 75 (ohm)": "{:.2f}",
                    "V.R %": "{:.2f}%"
                    }), hide_index=True, use_container_width=True)
                # st.dataframe(VR_table, hide_index=True)

            if VR_calc > 10:
                st.space("small")
                st.write("There is no avaible conductor to get V.R less than 10 %. So, increase number of sub-conductor in the bundle.")
            else:
                st.space("small")
                st.write(f"Selected Conductor = {conductor_selected}")




    #CORONA

    st.space("medium")
    st.subheader("Corona")
    st.space("small")

    





with tab2:

    st.header("Coming Soon!!!")

