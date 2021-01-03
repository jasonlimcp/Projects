import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

df = pd.read_excel('ResidentialTransactions.xlsx')  

df = df.replace(',','', regex=True)
df = df.astype({'Transacted Price ($)': 'int64',
                 'Area (SQFT)': 'float64',
                 'Unit Price ($ PSF)': 'int64'
                })


#Cleaning: Remove columns not relevant. Save as df_main
df_main = df.drop(columns=['Area (SQM)', 
                           'Unit Price ($ PSM)',
                           'Number of Units',
                           'Completion Date',
                           'Purchaser Address Indicator',
                           'Postal Code',
                          'Postal Sector'])


#Create New Sale table
df_new = df_main.loc[df_main['Type of Sale'] == 'New Sale']
df_new = df_new.drop(columns=['Type of Sale'])
print(df_new.shape)


#Create Resale Table
df_resale = df_main.loc[df_main['Type of Sale'].isin(['Resale'])]
df_resale = df_resale[["Address","Transacted Price ($)", "Unit Price ($ PSF)", "Sale Date"]]
print(df_resale.shape)


df_combine = pd.merge(df_new, df_resale, how = "inner", on = 'Address')
print(df_combine.shape)
df_combine.rename(columns={'Transacted Price ($)_x': 'New Sale Price ($)', 
                           'Unit Price ($ PSF)_x': 'New Sale Price (PSF)',
                           'Sale Date_x': 'New Sale Date',
                           'Transacted Price ($)_y': 'Resale Price ($)',
                           'Unit Price ($ PSF)_y': 'Resale Price (PSF)',
                           'Sale Date_y': 'Resale Date'
                          }, inplace=True)


df_final = df_combine


CCR = [9,10,11,1,2,6]
RCR = [3,4,5,7,8,12,13,14,15,20]
OCR = [16,17,18,19,21,22,23,24,25,26,27,28]

def segment(x):
    if x in CCR:
        return 'CCR'
    elif x in RCR:
        return 'RCR'
    elif x in OCR:
        return 'OCR'
    else:
        return 'Null'

df_final['Market Segment'] = df_final.apply(lambda row:
                                                    segment(row['Postal District'])
                                                    , axis = 1)


df_final['New Sale Datetime'] = df_final['New Sale Date'].apply(lambda x: datetime.strptime(x,'%d %b %Y'))
df_final['Resale Datetime'] = df_final['Resale Date'].apply(lambda x: datetime.strptime(x,'%d %b %Y'))
df_final = df_final.drop(columns=['New Sale Date','Resale Date'])


def year_convertor(x):
    y = round(int((x.split()[0]))/365,1)
    return y

df_final['Property Age (Years)'] = df_final.apply(lambda row:
                                                    year_convertor(str(row['Resale Datetime'] - row['New Sale Datetime']))
                                                    , axis = 1)


df_final['Price Differential (%)'] = df_final.apply(lambda row:
                                                    (row['Resale Price (PSF)'] - row['New Sale Price (PSF)'])/row['New Sale Price (PSF)']
                                                    , axis = 1)


df_final['Annualized Growth'] = df_final.apply(lambda row:
                                                    ((1+row['Price Differential (%)'])**(1/row['Property Age (Years)']))-1
                                                    , axis = 1)


df_visual = df_final[["Project Name", "Area (SQFT)","Postal District","Market Segment","Property Age (Years)","Price Differential (%)","Annualized Growth"]]
df_visual.head()


df_visual.groupby('Market Segment')['Price Differential (%)'].describe()
df_visual.groupby('Market Segment')['Annualized Growth'].describe()


district_rank = df_visual.groupby('Postal District')['Annualized Growth'].mean()
district_rank.sort_values(ascending=False)


plt.hist(df_visual['Price Differential (%)'], color = '#1f77b4', edgecolor = 'black',
         bins = int(1/0.01))

plt.title('Range of Capital Gains/Losses')
plt.xlabel('Price Differential')
plt.ylabel('Number of Transactions')


plt.hist(df_visual['Annualized Growth'], color = '#1f77b4', edgecolor = 'black',
         bins = int(0.5/0.005))

plt.title('Range of Annualized Growth')
plt.xlabel('Annualized Growth')
plt.ylabel('Number of Transactions')