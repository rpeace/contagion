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

class Collector:

    def __init__(self):
        return

    def get_stock_data(self, symbol, start, end):
        s = dateparser.parse(start) - timedelta(weeks=1)
        e = dateparser.parse(end)
        f = web.DataReader(symbol, "yahoo", s, e)
        f['Return'] = pd.Series()
        f.Return = (f.Close-f.Close.shift(1))/f.Close
        return f[dateparser.parse(start):]
        
    def get_average_stock_data(self, symbols, start, end):
        stocks = {}
        s = dateparser.parse(start)
        print type(s)
        e = dateparser.parse(end)
        for symbol in symbols:
            stocks[symbol] = web.DataReader(symbol, "yahoo", s, e)
            stocks[symbol]['Return'] = pd.Series()
            stocks[symbol].Return = (stocks[symbol].Close-stocks[symbol].Open)/stocks[symbol].Open
        panel = pd.Panel(stocks)
        avg = panel.mean(axis=0)
        return avg