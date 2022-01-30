# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 17:44:36 2022

@author: abhay
"""

import urllib.request
  
# for parsing all the tables present
# on the website
from html_table_parser.parser import HTMLTableParser
 
import pandas as pd
 
def url_get_contents(url):
 
    # Opens a website and read its
    # binary contents (HTTP Response Body)
 
    req = urllib.request.Request(url=url)
    f = urllib.request.urlopen(req)
 
    #reading contents of the website
    return f.read()
 
# defining the html contents of a URL.
global X    
X = pd.DataFrame() 



ALLURL = ['https://topforeignstocks.com/indices/components-of-the-sp-500-index/']
    

xhtml = url_get_contents(ALLURL[0]).decode('utf-8')    

p = HTMLTableParser()
 
p.feed(xhtml)
 

 
DF = pd.DataFrame(p.tables[0])

X = X.append(DF)

X.columns = ['S.no','Name','Ticker','Sector'] 
X = X.iloc[1:]

TKR = X['Ticker']  



TKR.to_json(r"C:/Users/abhay/Downloads/SPY500.json",index=True)
# TKR.to_csv(r"/home/abhaya_nsit/SPY500.csv",index=True)