import math
import numpy as np
import pandas as pd

global df

def economic_voltage_level(power, length, Nc):
    
    # Calculate economic voltage level using the given formula
    V_eco = 5.5 * math.sqrt((length / 1.6) + (power * 1000/ (Nc * 0.96 * 150)))
    
    return V_eco

def mflimit(length):
    # Calculate MF limit using the given formula
    df = pd.read_csv(r"data/mfLimit.csv")
    mf_limit_value = np.interp(length, df["Length"], df["mf_Limit"])
    

    return mf_limit_value
