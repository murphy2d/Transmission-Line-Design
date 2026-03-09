import streamlit as st
import pandas as pd
import numpy as np
import math
import cmath
from utils.conductorCalc import lineCurrent, conductor_selection, resistance_20_degree, resistance_75_degree, power_loss_calculation_MW, efficiency_calculation, gmr, GMRandGMDparameters, GMR_2, GMD_2, GMR_1, GMD_1, plot_efficiency_trend, inductance_L, capacitance_C, impedance_Z, susceptance_Y, abc_parameters, currentReceiving, to_polar, coronaInceptionVoltage
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

if "air_density_factor" not in st.session_state:    
    st.session_state.air_density_factor = 0.95 #default value for air density factor

if "surface_irregularity_factor" not in st.session_state:    
    st.session_state.surface_irregularity_factor = 0.95 #default value for surface_irregularity_factor

def sync_state():
    st.session_state.p_val = st.session_state._p
    st.session_state.l_val = st.session_state._l
    st.session_state.Nc = st.session_state._Nc
    # st.session_state.efficiency = st.session_state._efficiency
    st.session_state.pfTL = st.session_state._pfTL
    st.session_state.bundle_conductor_number = st.session_state.bundle_conductor_number
    st.session_state.bundle_button = st.session_state.bundle_toggle
    st.session_state.air_density_factor = st.session_state._air_density_factor
    st.session_state.surface_irregularity_factor = st.session_state._surface_irregularity_factor

    if "_bundle_conductor_spacing" in st.session_state:
        st.session_state.bundle_conductor_spacing = st.session_state._bundle_conductor_spacing

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
                    st.info('No conductor is available. You need to opt to bundle conductor ', icon="ℹ️")
                    st.markdown("[Go to bundle conductor selection](#current-carrying-capacity)")
                else:
                    st.write(f"Selected Conductor = {conductor_selected}")


    else:
        st.info('No conductor is available. You need to opt to bundle conductor ', icon="ℹ️")
        st.markdown("[Go to bundle conductor selection](#current-carrying-capacity)")



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
                st.image("TnDProject/data/ConductorConfigNc2.png", caption="Fig: Conductor Configuration for Nc = 2", width="content")
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
                st.image("TnDProject/data/conductorConfigNc1.png", caption="Fig: Conductor Configuration for Nc = 1", width="content")

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
                st.info('No conductor is available. You need to opt to bundle conductor ', icon="ℹ️")
                st.markdown("[Go to bundle conductor selection](#current-carrying-capacity)")
            else:
                st.space("small")
                st.write(f"Selected Conductor = {conductor_selected}")




    #CORONA

    st.space("medium")
    st.subheader("Corona")
    st.space("small")

    col1, col2 = st.columns(2, border=True)

    with col1:

        st.subheader("Parameters")
        st.write("")

        st.write(f"System Voltage (Vsys) = {V} kV")
        st.write(f"GMD = {GMD:.2f} cm")
        st.write(f"GMRc = {GMR_C:.2f} cm")

        air_density_factor = st.number_input("Enter air density factor (ρ)", value = st.session_state.air_density_factor, key="_air_density_factor", on_change=sync_state)
        surface_irregularity_factor = st.number_input("Enter surface irregularity factor (m)", value = st.session_state.surface_irregularity_factor, key="_surface_irregularity_factor", on_change=sync_state)

    with col2:

        st.subheader("Calculation and Analysis")
        st.write("")

        st.write(" *Corona Inception Voltage (Vci) :* ")
        corona_inception_voltage = coronaInceptionVoltage(GMD, GMR_C, air_density_factor, surface_irregularity_factor)

        st.latex(rf"V_{{ci}} = \sqrt{3} \cdot 21.21 \cdot \ln(\frac{{GMD}}{{GMR_C}}) \cdot GMR_C \cdot ρ \cdot m = {corona_inception_voltage:.2f} \, kV")

        st.write("")
        st.write("Required Condition: Vsys < Vci")

        if corona_inception_voltage > V:
            st.write(f"Since, {V} kV is less than {corona_inception_voltage:.2f} kV, the conductor satisfies the condition.")

        else:

            index = acsr_conductor_table.index[acsr_conductor_table["Code_Name"] == conductor_selected][0]
            rows_no = acsr_conductor_table.shape[0]


            corona_table = pd.DataFrame({
                "Conductor" : [conductor_selected],
                "Current Rating (A)" : [conductor_rating],
                "GMD (cm)" : [GMD],
                "GMR_L (cm)" : [GMR_L],
                "GMR_C (cm)" : [GMR_C],
            })

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


                if Nc == 1:
                        GMR_L , GMR_C = GMR_1(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, bundle_conductor_spacing)
                        GMD = GMD_1(y, ROW)

                elif Nc==2:
    
                    GMR_L, GMR_C = GMR_2(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, GMRandGMD_parameters, bundle_conductor_spacing)
                    GMD = GMD_2(GMRandGMD_parameters)

                #new data
                concat_corona_table = pd.DataFrame({
                    "Conductor" : [conductor_selected],
                    "Current Rating (A)" : [conductor_rating],
                    "GMD (cm)" : [GMD],
                    "GMR_L (cm)" : [GMR_L],
                    "GMR_C (cm)" : [GMR_C],
                })

                corona_table = pd.concat([corona_table, pd.DataFrame(concat_corona_table)])

                #Stop the loop if we've reached the standard
                if corona_inception_voltage > V:
                    break

        if corona_inception_voltage < V:
            st.space("small")
            st.info('No conductor is available. You need to opt to bundle conductor ', icon="ℹ️")
            st.markdown("[Go to bundle conductor selection](#current-carrying-capacity)")
        else:
            st.space("small")
            st.write(f"Selected Conductor = {conductor_selected}")

with tab2:
    st.header("Mechanical & Economic Requirements")
    st.space("medium")

  
    # 1. CONDUCTOR FETCHING & VALIDATION
   
    index_sel = acsr_conductor_table.index[acsr_conductor_table["Code_Name"] == conductor_selected].tolist()[0]
    sel_area = acsr_conductor_table.loc[index_sel, "Conductor_Area_mm2"]
    
    valid_conductors = [acsr_conductor_table.iloc[index_sel]]
    
    # Iterate to find the next 4 larger conductors
    for i in range(index_sel + 1, len(acsr_conductor_table)):
        row = acsr_conductor_table.iloc[i]
        
        # Ensure values exist and area is strictly increasing
        if (pd.notna(row['Conductor_Area_mm2']) and row['Conductor_Area_mm2'] > sel_area and
            pd.notna(row['Weight_Total_kg_per_km']) and pd.notna(row['Ultimate_Strength_kg'])):
            
            valid_conductors.append(row)
            sel_area = row['Conductor_Area_mm2']
            
        if len(valid_conductors) == 5:
            break
            
    if len(valid_conductors) < 5:
        st.error(f"⚠️ Only {len(valid_conductors)} valid conductors found after {conductor_selected}.")
        st.info("Please go back and opt to use a **Bundle Conductor (Nb > 1)**. This decreases the required current per conductor, allowing you to select a smaller base wire so you have enough standard sizes left in the table to compare 5 conductors.")
        st.stop()

    st.success(f"**Conductors Selected for Analysis:** {', '.join([r['Code_Name'] for r in valid_conductors])}")
    st.divider()

    
    # 2. GLOBAL INPUTS
    
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.subheader("Mechanical Variables")
        wind_pressure = st.number_input("Wind Pressure (Wp) [kg/m²]", value=100.0)
        weight_ice_perkm = st.number_input("Ice Weight (W_ice) [kg/km]", value=0.0)
        factor_of_safety = st.number_input("Factor of Safety (FS)", value=2.0)
        
    with col2:
        st.subheader("Economic & Temp Variables")
        theta_1 = st.number_input("Toughest Temp (θ1) [°C]", value=0.0)
        theta_2 = st.number_input("Stringing Temp (θ2) [°C]", value=25.0)
        theta_3 = st.number_input("Easiest Temp (θ3) [°C]", value=75.0)
        
        cost_al_per_tonne = st.number_input("Cost of Aluminum/tonne (Rs)", value=20150.0)
        cost_steel_per_tonne = st.number_input("Cost of Steel/tonne (Rs)", value=150000.0)
        cost_per_unit_energy = st.number_input("Energy Cost/unit (Rs)", value=7.50)

    st.divider()

    
    # 3. MASTER CALCULATION ENGINE
   
    span_lengths_m = [250, 275, 300, 325, 350]
    master_data = {} 

    v_smax = st.session_state.get('V', 132) * 1.1
    
    # Retrieving lengths from session state and converting cm to m safely
    y_raw = st.session_state.get('y', 411.0)
    y_dist = y_raw / 100.0 if y_raw > 10 else y_raw 
    
    d_prime_raw = st.session_state.get('d_prime', 549.84)
    d_prime = d_prime_raw / 100.0 if d_prime_raw > 10 else d_prime_raw

    total_length_km = st.session_state.get('l_val', 120.0)
    Nc = st.session_state.get('Nc', 2)
    bundle_conductor_number = st.session_state.get('bundle_conductor_number', 1)
    
    if 'line_current' in st.session_state:
        I_L = st.session_state.line_current
    else:
        I_L = (st.session_state.p_val * 1e6) / (math.sqrt(3) * st.session_state.V * 1000 * st.session_state.pfTL * Nc * bundle_conductor_number)
    
    Ne = 2 if Nc == 2 else 1
    d_e = 14.6 * 1e-3  
    T1e = 6664 / factor_of_safety  

    for cond in valid_conductors:
        c_name = cond['Code_Name']
        c_area = cond['Conductor_Area_mm2']
        
        w_c = cond['Weight_Total_kg_per_km'] / 1000.0
        w_ice = weight_ice_perkm / 1000.0
        d_m = cond['Conductor_Dia_mm'] * 1e-3
        UTS = cond['Ultimate_Strength_kg']
        
        E_modulus = cond['Elastic_Modulus_x10^6_kg_per_cm2'] * 1e6
        alpha = cond['Linear_Coefficient_x10^-6_per_C'] * 1e-6
        R_20 = cond['Resistance_20C_Ohm_per_km']
        w_al = cond['Weight_Al_kg_per_km']
        w_st = cond['Weight_Steel_kg_per_km']

        w_w = wind_pressure * d_m * (2/3)
        w_1 = math.sqrt((w_c + w_ice)**2 + w_w**2)
        w_2 = w_c
        w_3 = w_c
        T1 = UTS / factor_of_safety
        
        A_cm2 = c_area / 100.0
        Ae = A_cm2 * E_modulus

        cond_spans = []
        for l_sp in span_lengths_m:
            
            k1_T2 = -T1 + alpha * (theta_2 - theta_1) * Ae + ((w_1**2 * l_sp**2) / (24 * T1**2)) * Ae
            k2_T2 = ((w_2**2 * l_sp**2) / 24) * Ae
            roots_T2 = np.roots([1, k1_T2, 0, -k2_T2])
            T2 = np.real(roots_T2[(np.isreal(roots_T2)) & (np.real(roots_T2) > 0)][0])
            
            k1_T3 = -T1 + alpha * (theta_3 - theta_1) * Ae + ((w_1**2 * l_sp**2) / (24 * T1**2)) * Ae
            k2_T3 = ((w_3**2 * l_sp**2) / 24) * Ae
            roots_T3 = np.roots([1, k1_T3, 0, -k2_T3])
            T3 = np.real(roots_T3[(np.isreal(roots_T3)) & (np.real(roots_T3) > 0)][0])
            
            D_max = (w_3 * l_sp**2) / (8 * T3)
            h_g = (((v_smax - 33) / 33) + 17) * 0.3048 
            
            if Nc == 2:
                h1 = h_g + D_max
                h2 = h1 + y_dist
                h3 = h2 + y_dist
            else:
                h1 = h_g + D_max
                h2 = h1 + (y_dist / 2)
                h3 = h2 + (y_dist / 2)
                
            h_t = h3 + d_prime
            
            F_wp = wind_pressure * d_m * l_sp * (2/3)
            F_we = wind_pressure * d_e * l_sp * (2/3)
            
            BMP_w = (h1 + h2 + h3) * Nc * F_wp
            BME_w = h_t * Ne * F_we
            
            turn_factor = (0.8*math.sin(math.radians(1)) + 0.15*math.sin(math.radians(7.5)) + 0.05*math.sin(math.radians(15)))
            BMP_T = 2 * T1 * turn_factor * (h1 + h2 + h3) * Nc
            BME_T = 2 * T1e * turn_factor * h_t * Ne
            
            TBM = BMP_w + BME_w + BMP_T + BME_T
            
            TW = 0.000631 * h_t * math.sqrt(TBM * factor_of_safety)
            N_t = math.ceil((total_length_km * 1000) / l_sp) + 1
            cost_per_tower = cost_steel_per_tonne * TW
            tower_cost_per_km = cost_per_tower * (N_t / total_length_km)
            
            Y_annuity = 0.1 * (1 + 0.1)**25 / ((1 + 0.1)**25 - 1)
            total_conductors = 3 * Nc * bundle_conductor_number
            cond_cost_per_km = total_conductors * ((w_al * cost_al_per_tonne / 1000) + (w_st * cost_steel_per_tonne / 1000))
            capital_cost_per_km = tower_cost_per_km + cond_cost_per_km
            annual_capital_cost = Y_annuity * capital_cost_per_km
            
            LF = 0.6
            LLF = (0.7 * LF) + (0.3 * LF**2)
            R_75 = R_20 * (1 + 0.004 * (75 - 20))
            P_L_kw = (I_L**2 * R_75 * total_conductors) / 1000
            annual_loss_cost = P_L_kw * LLF * (365 * 24) * cost_per_unit_energy
            total_annual_cost = annual_capital_cost + annual_loss_cost
            
            cond_spans.append({
                "span": l_sp, "k1_T2": k1_T2, "k2_T2": k2_T2, "k1_T3": k1_T3, "T1": T1, "T2": T2, "T3": T3,
                "D_max": D_max, "h_g": h_g, "h1": h1, "h2": h2, "h3": h3, "h_t": h_t,
                "BMP_w": BMP_w, "BME_w": BME_w, "BMP_T": BMP_T, "BME_T": BME_T, "TBM": TBM, 
                "TW": TW, "N_t": N_t, "tower_cost_per_km": tower_cost_per_km, 
                "cond_cost_per_km": cond_cost_per_km, "annual_capital_cost": annual_capital_cost, 
                "annual_loss_cost": annual_loss_cost, "total_annual_cost": total_annual_cost, 
                "R_75": R_75, "P_L_kw": P_L_kw, "total_cond": total_conductors
            })
            
        master_data[c_name] = {
            "cond": cond, "w_w": w_w, "w_1": w_1, "w_2": w_2, "w_3": w_3, "T1": T1, "Ae": Ae, "spans": cond_spans
        }

    samp_name = valid_conductors[0]['Code_Name']
    samp = master_data[samp_name]
    s_c = samp['cond']
    s_span = samp['spans'][0]


    st.write("### Iterative Design Tables")
    design_tabs = st.tabs([
        "A. Tension Variations", 
        "B. Sag & Tower Heights", 
        "C. Moments & Weights", 
        "D. Tower Costs", 
        "E. Economic Selection"
    ])

  
    # TAB A: TENSION CALCULATION
   
    with design_tabs[0]:
        st.subheader("A. Tension Variations")
        with st.expander(f"📖 Sample Calculation for {samp_name} (Span = 250m)", expanded=False):
            st.markdown(f"""
            **Acronyms & Details:**
            * $w_c$: Weight of conductor = {s_c['Weight_Total_kg_per_km']} kg/km = {samp['w_3']:.4f} kg/m
            * $w_w$: Weight due to wind [kg/m]
            * $w_1, w_2, w_3$: Weights at Toughest, Normal, and Easiest conditions [kg/m]
            * $UTS$: Ultimate Tensile Strength = {s_c['Ultimate_Strength_kg']} kg
            * $A$: Area of conductor = {s_c['Conductor_Area_mm2']} mm² = {s_c['Conductor_Area_mm2']/100} cm²
            * $\epsilon$: Modulus of Elasticity = {s_c['Elastic_Modulus_x10^6_kg_per_cm2']*1e6:.2e} kg/cm²
            * $\alpha$: Linear expansion coeff. = {s_c['Linear_Coefficient_x10^-6_per_C']*1e-6:.2e} /°C
            """)
            
            st.latex(fr"w_w = W_p \cdot (d \cdot \frac{{2}}{{3}}) = {wind_pressure} \cdot ({s_c['Conductor_Dia_mm']*1e-3:.4f} \cdot \frac{{2}}{{3}}) = {samp['w_w']:.4f} \text{{ kg/m}}")
            st.latex(fr"w_1 = \sqrt{{(w_c + w_{{ice}})^2 + w_w^2}} = \sqrt{{({samp['w_3']:.4f} + {weight_ice_perkm/1000:.4f})^2 + {samp['w_w']:.4f}^2}} = {samp['w_1']:.4f} \text{{ kg/m}}")
            st.latex(fr"T_1 = \frac{{UTS}}{{FS}} = \frac{{{s_c['Ultimate_Strength_kg']}}}{{{factor_of_safety}}} = {samp['T1']:.2f} \text{{ kg}}")
            
            st.write("**Stringing Equation (Normal Condition $T_2$ at $\\theta_2$):**")
            st.latex(r"T_2^2(T_2 + k_1) - k_2 = 0")
            st.latex(fr"k_1 = -T_1 + \alpha(\theta_2 - \theta_1)A\epsilon + \frac{{w_1^2 \cdot l_{{sp}}^2}}{{24 \cdot T_1^2}}A\epsilon = {s_span['k1_T2']:.3f}")
            st.latex(fr"k_2 = \frac{{w_2^2 \cdot l_{{sp}}^2}}{{24}}A\epsilon = {s_span['k2_T2']:.2e}")
            st.latex(fr"T_2 = {s_span['T2']:.2f} \text{{ kg}}")

            st.write("**Stringing Equation (Easiest Condition $T_3$ at $\\theta_3$):**")
            st.latex(r"T_3^2(T_3 + k_1') - k_2' = 0")
            st.latex(fr"k_1' = -T_1 + \alpha(\theta_3 - \theta_1)A\epsilon + \frac{{w_1^2 \cdot l_{{sp}}^2}}{{24 \cdot T_1^2}}A\epsilon = {s_span['k1_T3']:.3f}")
            st.latex(fr"T_3 = {s_span['T3']:.2f} \text{{ kg}}")

        for i, c_name in enumerate(master_data.keys(), 1):
            df_t = pd.DataFrame(master_data[c_name]['spans'])[['span', 'k1_T2', 'k2_T2', 'k1_T3', 'T2', 'T3']]
            df_t.insert(0, 'w1 (kg/m)', master_data[c_name]['w_1'])
            df_t.insert(0, 'T1 (kg)', master_data[c_name]['T1'])
            st.write(f"**Table 1.{i}: {c_name} Tensions**")
            st.dataframe(df_t.style.format("{:.2f}"), use_container_width=True)


    # ---------------------------------------------------------
    # TAB B: SAG & TOWER HEIGHT
    # ---------------------------------------------------------
    with design_tabs[1]:
        st.subheader("B. Sag and Tower Height Calculation")
        with st.expander(f"📖 Sample Calculation for {samp_name} (Span = 250m)"):
            st.markdown(f"""
            **Acronyms & Details:**
            * $D_{{max}}$: Maximum Sag [m]
            * $h_g$: Minimum Ground Clearance [m]
            * $h_1, h_2, h_3$: Heights of power conductors [m]. 
              * For Nc=1: $h_2 = h_1 + y/2$ , $h_3 = h_2 + y/2$
              * For Nc=2: $h_2 = h_1 + y$ , $h_3 = h_2 + y$
            * $h_t$: Total Tower Height [m]
            * $N_c$: Number of circuits = {Nc}
            """)
            st.latex(fr"D_{{max}} = \frac{{w_3 \cdot l_{{sp}}^2}}{{8 \cdot T_3}} = \frac{{{samp['w_3']:.4f} \cdot 250^2}}{{8 \cdot {s_span['T3']:.2f}}} = {s_span['D_max']:.3f} \text{{ m}}")
            st.latex(fr"h_g = \left( \frac{{V_{{smax}} - 33}}{{33}} + 17 \right) \text{{ feet}} = {s_span['h_g']:.3f} \text{{ m}}")
            st.latex(fr"h_1 = h_g + D_{{max}} = {s_span['h_g']:.3f} + {s_span['D_max']:.3f} = {s_span['h1']:.3f} \text{{ m}}")
            
            if Nc == 2:
                st.latex(fr"h_2 = h_1 + y = {s_span['h1']:.3f} + {y_dist:.3f} = {s_span['h2']:.3f} \text{{ m}}")
                st.latex(fr"h_3 = h_2 + y = {s_span['h2']:.3f} + {y_dist:.3f} = {s_span['h3']:.3f} \text{{ m}}")
            else:
                st.latex(fr"h_2 = h_1 + y/2 = {s_span['h1']:.3f} + {y_dist/2:.3f} = {s_span['h2']:.3f} \text{{ m}}")
                st.latex(fr"h_3 = h_2 + y/2 = {s_span['h2']:.3f} + {y_dist/2:.3f} = {s_span['h3']:.3f} \text{{ m}}")
                
            st.latex(fr"h_t = h_3 + d' = {s_span['h3']:.3f} + {d_prime:.3f} = {s_span['h_t']:.3f} \text{{ m}}")

        for i, c_name in enumerate(master_data.keys(), 1):
            df_h = pd.DataFrame(master_data[c_name]['spans'])[['span', 'h_g', 'T3', 'D_max', 'h1', 'h2', 'h3', 'h_t']]
            df_h.insert(0, 'w3 (kg/m)', master_data[c_name]['w_3'])
            st.write(f"**Table 2.{i}: {c_name} Sag & Heights**")
            st.dataframe(df_h.style.format("{:.3f}"), use_container_width=True)


    # ---------------------------------------------------------
    # TAB C: BENDING MOMENT & WEIGHT
    # ---------------------------------------------------------
    with design_tabs[2]:
        st.subheader("C. Bending Moment & Tower Weight Calculation")
        with st.expander(f"📖 Sample Calculation for {samp_name} (Span = 250m)"):
            st.markdown(f"""
            **Acronyms & Details:**
            * $BMP_w, BME_w$: Wind Bending moments on Power Conductor & Earth Wire [kg-m]
            * $BMP_T, BME_T$: Turning Bending moments on Power Conductor & Earth Wire [kg-m]
            * $N_e$: Number of Earth wires = {Ne}
            * $T_{{1e}}$: Earth wire Tension = {T1e:.2f} kg (GUINEA UTS / FS)
            * $TBM$: Total Bending Moment [kg-m]
            * $TW$: Tower Weight [tonnes]
            """)
            st.latex(fr"BMP_w = (h_1 + h_2 + h_3) \cdot N_c \cdot (W_p \cdot d_p \cdot l_{{sp}} \cdot \frac{{2}}{{3}}) = {s_span['BMP_w']:.2f} \text{{ kg-m}}")
            st.latex(fr"BME_w = h_t \cdot N_e \cdot (W_p \cdot d_e \cdot l_{{sp}} \cdot \frac{{2}}{{3}}) = {s_span['BME_w']:.2f} \text{{ kg-m}}")
            
            st.latex(r"\text{Turn Factor } (TF) = 0.8\sin1^\circ + 0.15\sin7.5^\circ + 0.05\sin15^\circ")
            st.latex(fr"BMP_T = 2 \cdot T_1 \cdot TF \cdot (h_1+h_2+h_3) \cdot N_c = {s_span['BMP_T']:.2f} \text{{ kg-m}}")
            st.latex(fr"BME_T = 2 \cdot T_{{1e}} \cdot TF \cdot h_t \cdot N_e = {s_span['BME_T']:.2f} \text{{ kg-m}}")
            
            st.latex(fr"TBM = BMP_w + BME_w + BMP_T + BME_T = {s_span['TBM']:.2f} \text{{ kg-m}}")
            st.latex(fr"TW = 0.000631 \cdot h_t \cdot \sqrt{{TBM \cdot FS}} = 0.000631 \cdot {s_span['h_t']:.3f} \cdot \sqrt{{{s_span['TBM']:.2f} \cdot {factor_of_safety}}} = {s_span['TW']:.4f} \text{{ tonnes}}")

        for i, c_name in enumerate(master_data.keys(), 1):
            df_m = pd.DataFrame(master_data[c_name]['spans'])[['span', 'h_t', 'h1', 'h2', 'h3', 'BMP_w', 'BME_w', 'BMP_T', 'BME_T', 'TBM', 'TW']]
            st.write(f"**Table 3.{i}: {c_name} Moments & Weights**")
            st.dataframe(df_m.style.format("{:.2f}"), use_container_width=True)


    # ---------------------------------------------------------
    # TAB D: TOWER COST
    # ---------------------------------------------------------
    with design_tabs[3]:
        st.subheader("D. Tower Cost per Unit Length")
        with st.expander(f"📖 Sample Calculation for {samp_name} (Span = 250m)"):
            st.markdown(f"""
            **Acronyms & Details:**
            * $N_t$: Number of towers
            * $L_t$: Total transmission length = {total_length_km} km
            """)
            st.latex(fr"N_t = \frac{{L_t}}{{l_{{sp}}}} + 1 = \frac{{{total_length_km} \cdot 1000}}{{250}} + 1 = {s_span['N_t']}")
            st.latex(fr"\text{{Cost per Tower}} = \text{{Cost of steel/tonne}} \cdot TW = {cost_steel_per_tonne} \cdot {s_span['TW']:.4f} = \text{{Rs. }} {150000 * s_span['TW']:,.2f}")
            st.latex(fr"\text{{Cost of tower / km}} = \text{{Cost per tower}} \cdot \frac{{N_t}}{{L_t}} = \text{{Rs. }} {s_span['tower_cost_per_km']:,.2f}")

        for i, c_name in enumerate(master_data.keys(), 1):
            df_c = pd.DataFrame(master_data[c_name]['spans'])[['span', 'TW', 'N_t', 'tower_cost_per_km']]
            df_c['Cost/Tower (Rs)'] = df_c['TW'] * cost_steel_per_tonne
            df_c.rename(columns={'tower_cost_per_km': 'Cost/length (Rs)', 'TW': 'TW (t)'}, inplace=True)
            st.write(f"**Table 4.{i}: {c_name} Tower Costs**")
            st.dataframe(df_c.style.format({"TW (t)": "{:.4f}", "Cost/Tower (Rs)": "{:,.2f}", "Cost/length (Rs)": "{:,.2f}"}), use_container_width=True)


    # ---------------------------------------------------------
    # TAB E: ECONOMIC SELECTION
    # ---------------------------------------------------------
    with design_tabs[4]:
        st.subheader("E. Most Economical Span & Conductor Selection")
        with st.expander(f"📖 Sample Economic Calculation for {samp_name} (Span = 250m)"):
            st.markdown(f"""
            **Acronyms & Constants:**
            * $LF$: Load Factor = 0.6
            * $LLF$: Loss of Load Factor = 0.7(LF) + 0.3(LF)² = 0.528
            * $Y$: Annuity Factor (10% over 25 years) = 0.11017
            * $N_{{cond}}$: Total Conductors = 3 × {Nc} (Nc) × {bundle_conductor_number} (Nb) = {s_span['total_cond']}
            """)
            st.latex(fr"\text{{Cond. Cost/km}} = N_{{cond}} \cdot (W_{{Al}} \cdot C_{{Al}} + W_{{St}} \cdot C_{{St}}) = \text{{Rs. }} {s_span['cond_cost_per_km']:,.2f}")
            st.latex(fr"\text{{Capital Cost/km}} = \text{{Tower Cost/km}} + \text{{Cond. Cost/km}}")
            st.latex(fr"\text{{Annual Capital Cost}} = Y \cdot \text{{Capital Cost/km}} = 0.11017 \cdot {(s_span['tower_cost_per_km']+s_span['cond_cost_per_km']):,.2f} = \text{{Rs. }} {s_span['annual_capital_cost']:,.2f}")
            st.latex(fr"P_L \text{{ per km}} = \frac{{I_L^2 \cdot R_{{75}} \cdot N_{{cond}}}}{{1000}} = \frac{{{I_L:.2f}^2 \cdot {s_span['R_75']:.5f} \cdot {s_span['total_cond']}}}{{1000}} = {s_span['P_L_kw']:.2f} \text{{ kW/km}}")
            st.latex(fr"\text{{Energy Loss Cost}} = P_L \cdot LLF \cdot (365 \cdot 24) \cdot \text{{Rate}} = {s_span['P_L_kw']:.2f} \cdot 0.528 \cdot 8760 \cdot {cost_per_unit_energy} = \text{{Rs. }} {s_span['annual_loss_cost']:,.2f}")
            st.latex(fr"\text{{Total Annual Cost/km}} = \text{{Rs. }} {s_span['total_annual_cost']:,.2f}")

        final_rows = []
        for c_name, data in master_data.items():
            best_span_data = min(data['spans'], key=lambda x: x['total_annual_cost'])
            
            final_rows.append({
                "Conductor": c_name,
                "Economic Span (m)": best_span_data['span'],
                "Tower C/km": best_span_data['tower_cost_per_km'],
                "Cond. cost/km": best_span_data['cond_cost_per_km'],
                "Capital cost/km": best_span_data['tower_cost_per_km'] + best_span_data['cond_cost_per_km'],
                "Annual capital cost/km": best_span_data['annual_capital_cost'],
                "R_75": best_span_data['R_75'],
                "PL/km": best_span_data['P_L_kw'],
                "Energy loss cost/km": best_span_data['annual_loss_cost'],
                "Total Annual cost/km": best_span_data['total_annual_cost']
            })

        df_final = pd.DataFrame(final_rows)
        st.write("#### Final Table: Most Economical Span and Conductor Selection")
        st.dataframe(df_final.style.format({
            "Economic Span (m)": "{:.0f}",
            "Tower C/km": "{:,.2f}",
            "Cond. cost/km": "{:,.2f}",
            "Capital cost/km": "{:,.2f}",
            "Annual capital cost/km": "{:,.2f}",
            "R_75": "{:.5f}",
            "PL/km": "{:.2f}",
            "Energy loss cost/km": "{:,.2f}",
            "Total Annual cost/km": "{:,.2f}"
        }), hide_index=True, use_container_width=True)

        overall_best = df_final.loc[df_final["Total Annual cost/km"].idxmin()]
        st.success(f"🏆 **Absolute Most Economical Design:** Conductor **{overall_best['Conductor']}** at Span **{overall_best['Economic Span (m)']} m** (Minimum Cost: Rs. {overall_best['Total Annual cost/km']:,.2f}/km)")