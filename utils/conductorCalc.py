import math
import pandas as pd
import cmath

#import table
conductor_table = pd.read_csv("TnDProject/data/ACSRconductorTable.csv")

#line current calculation
def lineCurrent(power, Nc, V, pfTL, bundle_conductor_number):

    try:
        line_current = (power*pow(10,6))/(math.sqrt(3)*V*pfTL*Nc*pow(10,3)*bundle_conductor_number)
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

def power_loss_calculation_MW(line_current, resistance_75, Nc, bundle_conductor_number):

    power_loss = (3*pow(line_current,2)*resistance_75*Nc*bundle_conductor_number)/(pow(10,6))
    return power_loss

#efficiency calculation

def efficiency_calculation(power_loss, power):

    efficiency = (1-(power_loss/power))*100
    return efficiency

#gmr of conductor calculation for inductance and capacitance (mm --> cm)

def gmr(radius_of_conductor):

    return (0.7788*radius_of_conductor)/10, radius_of_conductor/10


#GMR and GMD parameters 

def GMRandGMDparameters(ROW, y):

    GMRandDMD_Parameters = {"Dac'" : ROW,
                            "Dca'" : ROW,
                            "Dab'" : math.sqrt(pow(y,2)+pow(ROW,2)),
                            "Dba'" : math.sqrt(pow(y,2)+pow(ROW,2)),
                            "Dbc'" : math.sqrt(pow(y,2)+pow(ROW,2)),
                            "Dcb'" : math.sqrt(pow(y,2)+pow(ROW,2)),
                            "Dab" : y,
                            "Dac" : 2*y,
                            "Dba" : y,
                            "Dbc" : y,
                            "Dca" : 2*y,
                            "Dcb" : y,
                            "Daa'" : math.sqrt(pow(2*y,2)+pow(ROW,2)),
                            "Dbb'" : ROW,
                            "Dcc'" : math.sqrt(pow(2*y,2)+pow(ROW,2))
                            }
    
    return GMRandDMD_Parameters



#GMR (self GMD calculation) for Nc=2

def GMR_2(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, GMRandGMD_parameters, bundle_conductor_spacing):

    if bundle_conductor_number==1:

        GMR_a_L = math.sqrt(gmr_conductor_L*GMRandGMD_parameters["Daa'"])
        GMR_b_L = math.sqrt(gmr_conductor_L*GMRandGMD_parameters["Dbb'"])     
        GMR_c_L = math.sqrt(gmr_conductor_L*GMRandGMD_parameters["Dcc'"])     
        GMR_L = pow(GMR_a_L*GMR_b_L*GMR_c_L, 1/3)

        GMR_a_C = math.sqrt(gmr_conductor_C*GMRandGMD_parameters["Daa'"])
        GMR_b_C = math.sqrt(gmr_conductor_C*GMRandGMD_parameters["Dbb'"])     
        GMR_c_C = math.sqrt(gmr_conductor_C*GMRandGMD_parameters["Dcc'"])
        GMR_C = pow(GMR_a_C*GMR_b_C*GMR_c_C, 1/3)

        return GMR_L, GMR_C
    
    elif bundle_conductor_number !=2 :

        r_eq_L = pow(gmr_conductor_L*pow(bundle_conductor_spacing, bundle_conductor_number-1), 1/bundle_conductor_number)
        GMR_a_L = math.sqrt(r_eq_L*GMRandGMD_parameters["Daa'"])
        GMR_b_L = math.sqrt(r_eq_L*GMRandGMD_parameters["Dbb'"])     
        GMR_c_L = math.sqrt(r_eq_L*GMRandGMD_parameters["Dcc'"])     
        GMR_L = pow(GMR_a_L*GMR_b_L*GMR_c_L, 1/3)

        r_eq_C = pow(gmr_conductor_C*pow(bundle_conductor_spacing, bundle_conductor_number-1), 1/bundle_conductor_number)
        GMR_a_C = math.sqrt(r_eq_C*GMRandGMD_parameters["Daa'"])
        GMR_b_C = math.sqrt(r_eq_C*GMRandGMD_parameters["Dbb'"])     
        GMR_c_C = math.sqrt(r_eq_C*GMRandGMD_parameters["Dcc'"])
        GMR_C = pow(GMR_a_C*GMR_b_C*GMR_c_C, 1/3)

        return GMR_L, GMR_C



#GMD for NC=2
def GMD_2(GMRandGMD_parameters):

    GMD2 = pow(GMRandGMD_parameters["Dab"]*GMRandGMD_parameters["Dac"]*GMRandGMD_parameters["Dab'"]*GMRandGMD_parameters["Dac'"]*GMRandGMD_parameters["Dba"]*GMRandGMD_parameters["Dbc"]*GMRandGMD_parameters["Dba'"]*GMRandGMD_parameters["Dbc'"]*GMRandGMD_parameters["Dca"]*GMRandGMD_parameters["Dcb"]*GMRandGMD_parameters["Dca'"]*GMRandGMD_parameters["Dcb'"], 1/12)

    return GMD2


#GMR for Nc = 1

def GMR_1(bundle_conductor_number, gmr_conductor_L, gmr_conductor_C, bundle_conductor_spacing):
    
    if bundle_conductor_number == 1:

        return gmr_conductor_L, gmr_conductor_C
    
    elif bundle_conductor_number != 1:

        r_eq_L = pow(gmr_conductor_L*pow(bundle_conductor_spacing, bundle_conductor_number-1), 1/bundle_conductor_number)
        r_eq_C = pow(gmr_conductor_C*pow(bundle_conductor_spacing, bundle_conductor_number-1), 1/bundle_conductor_number)

        return r_eq_L, r_eq_C
    

#GMD of Nc = 1 

def GMD_1(GMRandGMD_parameters):

    D = GMRandGMD_parameters["Dab"]/2 * GMRandGMD_parameters["Dac"]/2 * GMRandGMD_parameters["Dba"]/2 * GMRandGMD_parameters["Dbc"]/2 * GMRandGMD_parameters["Dca"]/2 *GMRandGMD_parameters["Dcb"]/2
    GMD1 = pow(D, 1/6)

    return GMD1


import matplotlib.pyplot as plt

def plot_efficiency_trend(efficiency_table):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # Plotting Efficiency
    ax1.set_xlabel('Conductor Code Name')
    ax1.set_ylabel('Efficiency (%)', color='tab:blue')
    ax1.plot(efficiency_table['Conductor'], efficiency_table['Efficiency (η)'], marker='o', color='tab:blue', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    
    # Create a second y-axis for Power Loss
    ax2 = ax1.twinx()
    ax2.set_ylabel('Power Loss (MW)', color='tab:red')
    ax2.bar(efficiency_table['Conductor'], efficiency_table['Power Loss(MW)'], alpha=0.3, color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    
    plt.title("Efficiency vs. Power Loss")
    return fig


#inductance

def inductance_L(GMD, GMR_L, length):
    
    L = 2*pow(10, -7)*math.log(GMD/GMR_L)*1000*length
    return L


#capacitance

def capacitance_C(GMD, GMR_C, length):
    
    C = ((2*math.pi*8.89*pow(10, -12))/(math.log(GMD/GMR_C)))*1000*length
    return C

#impedance Z

def impedance_Z(resistance_75, inductance):
    
    Z = complex(resistance_75, 2*math.pi*50*inductance)
    return Z


#Susceptance Y

def susceptance_Y(capacitance):
    
    Y = complex(0, 2*math.pi*50*capacitance)
    return Y


#abc parameters

def abc_parameters(Z, Y):

    return 1+((Z*Y)/2), Z, Y*(1+((Y*Z)/4))

#receiving current

def currentReceiving(line_current, pf):

    angle_rad = math.acos(pf)
    R = line_current*math.cos(-angle_rad)
    X = line_current*math.sin(-angle_rad)

    return complex(R, X)


#to polar

def to_polar(complex_number):

    mag = abs(complex_number)
    angle_deg = math.degrees(cmath.phase(complex_number))

    return f"{mag:.2f} \\angle {angle_deg:.2f}^\\circ "