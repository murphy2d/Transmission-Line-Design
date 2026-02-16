import math
import pandas as pd
import numpy

#import table
conductor_table = pd.read_csv("data/ACSRconductorTable.csv")

#line current calculation
def lineCurrent(power, Nc, V, pfTL):

    try:
        line_current = (power*pow(10,6))/(math.sqrt(3)*V*pfTL*Nc*pow(10,3))
        return line_current
    except ZeroDivisionError:
        return 0
    
#conductor selection
def conductor_selection(line_current, ambient_temp):
    

    if ambient_temp == 40:

        match = conductor_table.loc[conductor_table["Current_40C_A"] >= line_current]
        
        if not match.empty:
            return match.iloc[0]["Code_Name"], match.iloc[0]["Current_40C_A"]
        
        else:
            return None, None
        
    elif ambient_temp == 45:

        match = conductor_table.loc[conductor_table["Current_45C_A"] >= line_current]
        
        if not match.empty:
            return match.iloc[0]["Code_Name"], match.iloc[0]["Current_45C_A"]
        
        else:
            return None, None
        

#resistance value at 20 degree celcius

def resistance_20_degree(ambient_temp, conductor_selected):
    
    if ambient_temp == 40:

        match = conductor_table.loc[conductor_table["Code_Name"] == conductor_selected]
        
        if not match.empty:
            return match.iloc[0]["Resistance_20C_Ohm_per_km"]
        
        else:
            return None
        
    elif ambient_temp == 45:

        match = conductor_table.loc[conductor_table["Code_Name"] == conductor_selected]
        
        if not match.empty:
            return match.iloc[0]["Resistance_20C_Ohm_per_km"]
        
        else:
            return None
        

#resistance at 75 degree celcius

def resistance_75_degree(resistance_20_degree, length):

    resistance_75 = resistance_20_degree*(1+ 0.004 * (75-20))
    return resistance_75, resistance_75*length

#power loss

def power_loss_calculation_MW(line_current, resistance_75, Nc):

    power_loss = (3*pow(line_current,2)*resistance_75*Nc)/(pow(10,6))
    return power_loss

#efficiency calculation

def efficiency_calculation(power_loss, power):

    efficiency = (1-(power_loss/power))*100

    return efficiency
