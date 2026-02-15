import streamlit as st
import pandas as pd
import math
from utils.insulationCalc import maximum_system_voltage_calculation, dry_1min_withstand_voltage_calculation, wet_1min_withstand_voltage_calculation, impulse_withstand_voltage_calculation

#set page configuration
st.set_page_config(
    page_title="⚡ Transmission Tower Calculation",
    layout="wide",
    initial_sidebar_state="expanded",
)

#initialization of global variables for Flashover Withstand Ratio (FWR), Atmospheric Correction Factor (ACF), and Safety Factor (FS)
if "FWR" not in st.session_state:
    st.session_state.FWR = 1.15 #default value for Flashover Withstand Ratio (FWR)
if "ACF" not in st.session_state:
    st.session_state.ACF = 1.15 #default value for Atmospheric Correction Factor (ACF)
if "FS" not in st.session_state:
    st.session_state.FS = 1.2 #default value for Safety Factor (FS)
if "V" not in st.session_state:    
    st.session_state.V = 0 #default value for System Voltage (V)

#persistence logic for Flashover Withstand Ratio (FWR), Atmospheric Correction Factor (ACF), and Safety Factor (FS)
def sync_state():
    st.session_state.FWR = st.session_state.FWR_input
    st.session_state.ACF = st.session_state.ACF_input
    st.session_state.FS = st.session_state.FS_input


#insulation design
st.header(":orange[Insulation Design] 🛡️")

#design considerations

st.subheader("Design Considerations for Insulation")
col1, col2 = st.columns(2, border=True)

#table for flashover voltage for 254 x 154 mm disc insulator
with col1:
    st.subheader("Flashover Voltage for 254 x 154 mm Disc Insulator")
    flashover_voltage_data = pd.read_csv("TnDProject/data/FlashoverVoltageInsulator.csv")
    st.dataframe(flashover_voltage_data)

#table for withstand voltage capability
with col2:
    st.subheader("Withstand Voltage Capability of Insulators")
    withstand_voltage_data = pd.read_csv("TnDProject/data/withstandVoltageCapability.csv")
    st.dataframe(withstand_voltage_data)

    #factors consideration
    st.write("**Factors for Insulation Design:**")

    FWR = st.number_input("Flashover Withstand Ratio (FWR)", value=st.session_state.FWR, help="The ratio of the flashover voltage to the system withstand voltage.")
    ACF = st.number_input("Atmospheric Correction Factor (ACF)", value=st.session_state.ACF, help="A factor that accounts for the effects of atmospheric conditions on insulation performance.")
    FS = st.number_input("Safety Factor (FS)", value=st.session_state.FS, help="A factor that provides a margin of safety in the design of the insulation system.")

    st.session_state.FWR = FWR
    st.session_state.ACF = ACF
    st.session_state.FS = FS    

st.space(size="medium")

col1, col2 = st.columns(2, border=False)

#system voltage and withstand voltage calculation
with col1:
    st.subheader("System and Withstand Voltage Calculation")

    with st.expander("System Voltage and Withstand Voltage Calculation Details"):

        V = st.session_state.V
        FWR = st.session_state.FWR
        ACF = st.session_state.ACF
        FS = st.session_state.FS

        #calculate the maximum system voltage nearest to withstand voltage capability
        Vmax = maximum_system_voltage_calculation(V)
        st.write(f"**Maximum System Voltage Calculated =** 1.1 × {V} kV = {1.1*V:.2f} kV")
        st.write(f"**Maximum System Voltage From table withstand voltage capability (Vmax) =** {Vmax} kV")

        #dry 1 min withstand voltage calculation
        dry_1min_withstand_voltage = dry_1min_withstand_voltage_calculation(Vmax)
        st.write(f"**Dry 1 min Withstand Voltage (Vdry) =** {dry_1min_withstand_voltage} kV")

        #wet 1 min withstand voltage calculation
        wet_1min_withstand_voltage = wet_1min_withstand_voltage_calculation(Vmax)
        st.write(f"**Wet 1 min Withstand Voltage (Vwet) =** {wet_1min_withstand_voltage} kV")

        #temp overvoltage calculation
        temp_overvoltage = 0.8*(V * 1.1) * math.sqrt(2)
        st.write(f"**Temporary Overvoltage (Vtemp) =** 0.8 × {V} × 1.1 × √2 = {temp_overvoltage:.2f} kV")

        #impulse withstand voltage calculation
        impulse_withstand_voltage = impulse_withstand_voltage_calculation(Vmax)
        st.write(f"**Impulse Withstand Voltage (Vimp) =** {impulse_withstand_voltage} kV")

        #switching surge ratio
        SSR = 2.8
        st.write(f"**Switching Surge Ratio (SSR) =** {SSR}")

        #system phase peak voltage calculation
        Vppeak = 1.1 * V * math.sqrt(2)/math.sqrt(3)
        st.write(f"**System Phase Peak Voltage (Vph-p) =** 1.1 × {V} × √2/√3 = {Vppeak:.2f} kV")

        #switching withstand voltage calculation
        switching_withstand_voltage = SSR * Vppeak
        st.write(f"**Switching Withstand Voltage (Vswitch) =** {SSR} × {Vppeak:.2f} kV = {switching_withstand_voltage:.2f} kV") 

        #switching to impulse ratio
        SIR = 1.2
        st.write(f"**Switching to Impulse Ratio (SIR) =** {SIR}")

#flashover voltage calculation
with col2:

    st.subheader("Flashover Voltage Calculation")

    with st.expander("Flashover Voltage Calculation Details"):

        st.markdown("**1. Continuous Maximum System Over Voltage**")
        
        #1 min dry flashover voltage calculation
        flashover_voltage_dry = FWR * ACF * FS * dry_1min_withstand_voltage
        st.write(f"*1 min Dry Flashover Voltage =* {dry_1min_withstand_voltage} × {FWR} × {ACF} × {FS} = {flashover_voltage_dry:.2f} kV")

        #1 min wet flashover voltage calculation
        flashover_voltage_wet = FWR * ACF * FS * wet_1min_withstand_voltage
        st.write(f"*1 min Wet Flashover Voltage =* {wet_1min_withstand_voltage} × {FWR} × {ACF} × {FS} = {flashover_voltage_wet:.2f} kV")

        st.markdown("**2. Temporary Overvoltage**")
        temporary_flashover_voltage = temp_overvoltage * FWR * ACF * FS
        st.write(f"*Temporary FOV =* {temp_overvoltage:.2f} × {FWR} × {ACF} × {FS} = {temporary_flashover_voltage:.2f} kV")

        st.markdown("**3. Lightning Overvoltage**")
        lightning_flash_overvoltage = impulse_withstand_voltage * FWR * ACF * FS
        st.write(f"*Lightning FOV =* {impulse_withstand_voltage} × {FWR} × {ACF} × {FS} = {lightning_flash_overvoltage:.2f} kV")

        st.markdown("**4. Switching Overvoltage**")
        switching_flash_overvoltage = switching_withstand_voltage * FWR * ACF * FS
        st.write(f"*Switching FOV =* {switching_withstand_voltage:.2f} × {FWR} × {ACF} × {FS} = {switching_flash_overvoltage:.2f} kV")

        st.caption("[ *As Switching FOV is in kHz range and there is no switching withstand voltage for disc insulator in above table, we need to convert it in terms to impulse FOV.* ]")
        impulse_flash_overvoltage = switching_flash_overvoltage * 1.2
        st.write(f"*Impulse FOV = Switching FOV × SIR =* {switching_flash_overvoltage:.2f} × 1.2 = {impulse_flash_overvoltage:.2f} kV")

st.space(size="medium")

#insulator disc calculation
st.subheader("Number of Insulator Discs Calculation")

#choose number of insulator discs based on the flashover voltage calculated above and the flashover voltage for 254 x 154 mm disc insulator from the table and represent them in tabular format

for index, row in flashover_voltage_data.iterrows():
    if flashover_voltage_dry <= row["1 minute dry FOV (kV)"]:
        num_discs_dry = row["No. of discs"]
        break
    
for index, row in flashover_voltage_data.iterrows():
    if flashover_voltage_wet <= row["1 minute wet FOV (kV)"]:
        num_discs_wet = row["No. of discs"]
        break

for index, row in flashover_voltage_data.iterrows():
    if temporary_flashover_voltage <= row["1 minute wet FOV (kV)"]:
        num_discs_temp = row["No. of discs"]
        break

for index, row in flashover_voltage_data.iterrows():
    if lightning_flash_overvoltage <= row["Impulse withstand (kV)"]:
        num_discs_lightning = row["No. of discs"]
        break

for index, row in flashover_voltage_data.iterrows():
    if impulse_flash_overvoltage <= row["Impulse withstand (kV)"]:
        num_discs_switching = row["No. of discs"]
        break

insulator_disc_data = pd.DataFrame({
    "Condition": ["1 min Dry FOV", "1 min Wet FOV", "Temporary FOV", "Lightning FOV", "Switching FOV"],
    "Number of Discs": [num_discs_dry, num_discs_wet, num_discs_temp, num_discs_lightning, num_discs_switching]
})

# Create 3 columns, place table in the middle
left_spacer, center, right_spacer = st.columns([1, 2, 1])
with center:
    Disc_insulator_number = st.dataframe(insulator_disc_data, hide_index=True, column_config={"Condition": {"alignment": "left"}, "Number of Discs": {"alignment": "left"}})

Final_disc_insulator_number = max(num_discs_dry, num_discs_wet, num_discs_temp, num_discs_lightning, num_discs_switching)
st.write(f"Selected Number of Discs Insulator = {Final_disc_insulator_number} discs")