# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 13:01:05 2015

@author: rob
"""

from bs4 import BeautifulSoup
import urllib2
import datetime
import calendar

class HeadlineGrabber:
    
    def __init__(self):
        return
        
    def get_headline(self, date):
        month = calendar.month_name[date.month]
        url = "http://en.wikipedia.org/wiki/Portal:Current_events/"+str(date.year) +"_"+ month + "_"+str(date.day)
        print url
        soup = BeautifulSoup(urllib2.urlopen(url))
        headline = soup.find("table", class_="vevent").find("li").text
        headline = headline.split("(")[0]
        return headline + " Market contagion results."