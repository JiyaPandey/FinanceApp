import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mftool import Mftool
mf = Mftool()
mutual_fund_code = '145834'
mutual_fund = 'Motilal Oswal Liquid Fund - Direct Growth'

df = mf.get_scheme_historical_nav(mutual_fund_code,as_Dataframe=True).reset_index()
df['nav'] = df['nav'].astype(float)
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
df = df.sort_values('date').reset_index(drop=True)
print(df)
df.plot(x='date', y='nav')
plt.title(mutual_fund)
plt.xlabel('Date')
plt.ylabel('NAV')
plt.grid()
plt.show()
