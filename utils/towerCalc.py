import math
import numpy as np
import pandas as pd


df = pd.read_csv("data/mfLimit.csv")

# Calculate economic voltage level using the given formula

def economic_voltage_level_calcuation(power, length, Nc):
    
    V_eco = 5.5 * math.sqrt((length / 1.6) + (power * 1000/ (Nc * 0.96 * 150)))
    return V_eco

# Calculate economic voltage level nearest to standard voltage level 66,132, 220, 400, 765, 1000 kV
def economic_voltage_level(Veco):
    standard_voltage_levels = [66, 132, 220, 400, 765, 1000]
    nearest_voltage_level = min(standard_voltage_levels, key=lambda x: abs(x - Veco))
    return nearest_voltage_level

# Calculate MF limit using the given formula

def mflimit(length):

    mf_limit_value = np.interp(length, df["Length"], df["mf_Limit"])
    return mf_limit_value

#sil calculation
def sil_calculation(V, z):
    SIL = V**2 / z
    return SIL

#mfᵢ calculation
def mf_i_calculation(power, SIL):
    mf_i = power / SIL
    return mf_i

#air clearance calculation
def air_clearance_calculation(V):
    a = 1*V*1.1*(math.sqrt(2)/math.sqrt(3))+30
    return a

#crossarm length calculation
def crossarm_length_calculation(swing_angle, air_clearance):
    cl  = air_clearance*(1+math.tan(math.radians(swing_angle)))
    return cl

#insulated string length calculation
def insulated_string_length_calculation(swing_angle, air_clearance):
    isl = air_clearance / math.cos(math.radians(swing_angle))
    return isl

#distance between two conductors calculation
def distance_between_conductors_calculation(insulated_string_length, crossarm_length, air_clearance):
    y = (insulated_string_length+air_clearance)/(math.sqrt(1-(0.3 * ((insulated_string_length+air_clearance)/crossarm_length))**2))
    return y

#distance between earth wire and top most conductor calculation
def distance_between_earth_wire_and_top_conductor_calculation(crossarm_length, tower_width, Nc):
    if Nc == 1:
        d = math.sqrt(3)*(crossarm_length - tower_width/2)
    elif Nc == 2:
        d = math.sqrt(3)*(crossarm_length)
    return d

#distance of earth wire from top most cross arm calculation
def distance_of_earth_wire_from_top_most_cross_arm_calculation(d_dash, insulated_string_length):
    d_earth_wire = d_dash - insulated_string_length

    return d_earth_wire
