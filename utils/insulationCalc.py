import math
import pandas as pd
import numpy as np

Vmax = pd.read_csv("data/withstandVoltageCapability.csv")

def maximum_system_voltage_calculation(V):
    max_sys_V = 1.1 * V
    
    #return the maximum system voltage nearest to withstand voltage capability. Take system voltage = max_sys_V if tolerance is 5kV else take higher system voltage
    for index, row in Vmax.iterrows():
        if abs(max_sys_V - row["maximum system voltage (kV)"]) <= 5:
            return row["maximum system voltage (kV)"]
        elif max_sys_V < row["maximum system voltage (kV)"]:
            #return the next higher system voltage, row+1
            if index + 1 < len(Vmax):
                return Vmax.iloc[index + 1]["maximum system voltage (kV)"]
            else:
                return row["maximum system voltage (kV)"]

#dry 1 min withstand voltage calculation    
def dry_1min_withstand_voltage_calculation(V):   
    # return the dry 1 min withstand voltage from the table withstand voltage capability (Vmax). We know first column maximum system voltage (kV) and return the corresponding dry 1 min withstand voltage (kV) from the second column
    for index, row in Vmax.iterrows():
        if row["maximum system voltage (kV)"] == V:
            return row["1 min dry withstand voltage (kV)"]
        else:
            continue

#wet 1 min withstand voltage calculation
def wet_1min_withstand_voltage_calculation(V):
    # return the wet 1 min withstand voltage from the table withstand voltage capability (Vmax). We know first column maximum system voltage (kV) and return the corresponding wet 1 min withstand voltage (kV) from the third column
    for index, row in Vmax.iterrows():
        if row["maximum system voltage (kV)"] == V:
            return row["1 min wet withstand voltage (kV)"]
        else:
            continue

#impulse withstand voltage calculation
def impulse_withstand_voltage_calculation(V):
    # return the impulse withstand voltage from the table withstand voltage capability (Vmax). We know first column maximum system voltage (kV) and return the corresponding impulse withstand voltage (kV) from the fourth column
    for index, row in Vmax.iterrows():
        if row["maximum system voltage (kV)"] == V:
            return row["Impulse withstand voltage (kV)"]
        else:

            continue
