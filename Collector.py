# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:15:44 2015

@author: rob
"""

import pandas.io.data as web
import pandas as pd
import datetime
from datetime import timedelta
from dateutil import parser as dateparser
import connection

class Collector:

    def __init__(self):
        return

    def get_stock_data(self, exchange, symbol, start, end, region, country, sector):
        if region == "(All)":
            region = ""
        if country == "(All)":
            country = ""
        if sector == "(All)":
            sector = ""
        if exchange == "(All)":
            exchange = ""
        s = dateparser.parse(start) - timedelta(weeks=1)
        e = dateparser.parse(end)
        cdata = connection.get_stocks(exchange, symbol, s, e, region, country, sector)
     
        IDs = list(set([line[0] for line in cdata]))      
        
        dates = []
        for line in cdata:
            dates.append(datetime.datetime(int(line[3]), int(line[4]), int(line[5])))
        dates = sorted(list(set(dates)))
        
        returns = pd.Series(0.0, dates[1:])
        
        dataDict = {}
        for ID in IDs:
            dataDict[ID] = []
            for line in cdata:
                if line[0] == ID:
                    dataDict[ID].append(line)
            for idx, line in enumerate(dataDict[ID]):
                if idx > 0:
                    returns[datetime.datetime(int(line[3]), int(line[4]), int(line[5]))] += (float(dataDict[ID][idx][6]) - float(dataDict[ID][idx-1][6])) / float(dataDict[ID][idx][6])                 
            
        returns = returns.div(len(IDs))
        return returns
#        f['Return'] = pd.Series()
#        f.Return = (f.Close-f.Close.shift(1))/f.Close
#        return f[dateparser.parse(start):]
        
    def get_nyse_stock_data(self, start, end):
        symbols = ["AAPL", "XOM", "MSFT", "JNJ", "GE", "WFC", "PG", "JPM", "PFE"]
        return self.get_average_stock_data(symbols, start, end)
    
    def get_sehk_stock_data(self, start, end):
        symbols = ["0001.HK", "0002.HK", "0003.HK", "0004.HK", "0005.HK", "0006.HK", "0007.HK", "0008.HK", "0009.HK", "0010.HK"]
        return self.get_average_stock_data(symbols, start, end)
        
    def get_lse_stock_data(self, start, end):
        symbols = ["III.L", "ABF.L", "ADN.L", "ADM.L", "AGK.L", "AAL.L", "ANTO.L", "ARM.L", "AHT.L", "BAB.L"]
        return self.get_average_stock_data(symbols, start, end)
        
    def get_average_stock_data(self, symbols, start, end):
        stocks = {}
        s = dateparser.parse(start)  - timedelta(weeks=1)
        e = dateparser.parse(end)
        for symbol in symbols:
            stocks[symbol] = web.DataReader(symbol, "yahoo", s, e)
            stocks[symbol]['Return'] = pd.Series()
            stocks[symbol].Return = (stocks[symbol].Close-stocks[symbol].Close.shift(1))/stocks[symbol].Close
            stocks[symbol] = stocks[symbol][dateparser.parse(start):]
        panel = pd.Panel(stocks)
        avg = panel.mean(axis=0)
        return avg
        
c = Collector()

c.get_stock_data("", "", "2003-01-01", "2003-12-31", "", "United States", "Technology")