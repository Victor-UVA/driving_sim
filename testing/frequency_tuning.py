import pandas as pd
import numpy as np

data = pd.read_csv('time_calc.csv')

print("Max = ", np.max(data['Time']))
print("Min = ", np.min(data['Time']))
print("Med = ", np.median(data['Time']))
print("Avg = ", np.mean(data['Time']))
