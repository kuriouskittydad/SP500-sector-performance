# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 14:06:02 2022

@author: abhay
"""


#!/usr/bin/python3 
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pytz import timezone
import json
import robin_stocks.robinhood as R
import pyotp
from Rconfig import totp
from Rconfig import config


login = config


# add time stuff
nyc = timezone('America/New_York')
today = datetime.today().astimezone(nyc)
# input any time delta below -- 2400 hours would be 100 days
delta = timedelta(hours = 8800 )
From = today - delta
todayy = today.strftime('%Y-%m-%dT%H:%M:%S-04:00')
Fromm = From.strftime('%Y-%m-%dT%H:%M:%S-04:00')
today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
From_str = From.strftime('%Y-%m-%d')


# Pull a recent list of SP500 stocks

with open('C:/Users/abhay/Downloads/SPY500.json') as f:
  data = json.load(f)
SP = list(data.values())

# additional stuff
SP.remove('N/A*')
SP.remove('COG')
SP.remove('WLTW')
SP = SP + ['CTRA']
SP = SP + ['WTW']



# robinhoodapi takes a max of 100 tickers string at a time to process without error

    
TK = [SP[x:x+100] for x in range(0, len(SP), 100)]

F2 = pd.DataFrame()

F1 = pd.DataFrame()


for i in range(len(TK)):
    
    data = R.stocks.get_fundamentals(TK[i])
    
    D = pd.DataFrame(data)

    F1 = F1.append(D, ignore_index = False)
    
for i in range(len(TK)):
    
    data2 = R.stocks.get_latest_price(TK[i],includeExtendedHours= False)
    D2 = pd.DataFrame(data2,columns = ['Price'])
    D2['symbol'] = pd.DataFrame(TK[i])
    F2 = F2.append(D2, ignore_index = False)


T = 'day'
columns = ['DoC']
dtype = ['datetime64[ns]']
         
DF = pd.concat([pd.Series(name=col, dtype=dt) for col, dt in zip(columns, dtype)], axis=1)
DF = DF.append({'DoC' : today_str}, ignore_index=True)

DT  = pd.DataFrame(pd.date_range(start= From_str  , end= today_str), columns = ['D'])
DT['date'] = [d.date() for d in DT['D']]

    
F3 = pd.DataFrame()    

for i in range(len(SP)):    
        

    try:
            
    
        data = R.stocks.get_stock_historicals(SP[i], interval='day', span='year', bounds='regular', info=None)
        df = pd.DataFrame(data)
        df['dat'] =   [datetime.strptime(d[0:10], '%Y-%m-%d') for d in df['begins_at']]  
        df['date'] = [d.date() for d in df['dat']]
        c= df.merge(DT,on = 'date', how = 'outer', sort = True)
        c = c.fillna(method='ffill')
        c = c.fillna(method ='bfill')
        LYD = c.iloc[-366:-365]
        L7d = c.iloc[-8:-7]
        L30d = c.iloc[-31:-30]
        Ldclose = c.iloc[-2:-1]
        c['LYD'] = LYD['close_price']
        c['L7d'] = L7d['close_price']
        c['L30d'] = L30d['close_price']
        c['Ldclose'] = Ldclose['close_price']
        c = c.fillna(method='ffill')
        c = c.iloc[-1:]
        # F1 = F1.append(c)
                    
    except:
        
        c = pd.DataFrame(columns = F1.columns)
        
    F3 = F3.append(c)
    

    
F1 = F1[['pb_ratio','pe_ratio', 'shares_outstanding','sector', 'industry', 'symbol']]
F = F1.merge(F2, on = 'symbol',how = "inner")
F = F.merge(F3, on ='symbol', how = 'inner')

F['MKTCAP_now'] = F['Price'].astype(float) *F['shares_outstanding'].astype(float)

F['MKTCAP_lastclose'] = F['close_price'].astype(float) *F['shares_outstanding'].astype(float)

F['MKTCAP_lastweek'] = F['L7d'].astype(float) *F['shares_outstanding'].astype(float)


F['MKTCAP_lastmonth'] = F['L30d'].astype(float) *F['shares_outstanding'].astype(float)

F['MKTCAP_lastyear'] = F['LYD'].astype(float) *F['shares_outstanding'].astype(float)


Report = F[['sector','MKTCAP_now','MKTCAP_lastclose','MKTCAP_lastweek','MKTCAP_lastmonth','MKTCAP_lastyear']]
R = pd.pivot_table(Report, values=['MKTCAP_now','MKTCAP_lastclose','MKTCAP_lastweek','MKTCAP_lastmonth','MKTCAP_lastyear'], index= 'sector' , aggfunc=np.sum)

ALLMARKET = R['MKTCAP_now'].sum()
R['Return_LD_%'] = (R['MKTCAP_now'] - R['MKTCAP_lastclose'])*100 / R['MKTCAP_now']
R['Return_LD_%'] = R['Return_LD_%'].map('{:,.2f}'.format)
R['Return_LW_%'] = (R['MKTCAP_now'] - R['MKTCAP_lastweek'])*100 / R['MKTCAP_now']
R['Return_LW_%'] = R['Return_LW_%'].map('{:,.2f}'.format)
R['Return_LM_%'] = (R['MKTCAP_now'] - R['MKTCAP_lastmonth'])*100 / R['MKTCAP_now']
R['Return_LM_%'] = R['Return_LM_%'].map('{:,.2f}'.format)
R['Return_LY_%'] = (R['MKTCAP_now'] - R['MKTCAP_lastyear'])*100 / R['MKTCAP_now']
R['Return_LY_%'] = R['Return_LY_%'].map('{:,.2f}'.format)
R['Sector_weight'] = R['MKTCAP_now']*100/ALLMARKET
R['Sector_weight'] = R['Sector_weight'].map('{:,.2f}'.format)


RPT = R[['Return_LD_%','Return_LW_%', 'Return_LM_%', 'Return_LY_%', 'Sector_weight']]
RPT = RPT.sort_values(by='Return_LD_%', ascending = False)
RPT = RPT.reset_index(drop = False)

print(RPT)