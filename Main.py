# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:43:18 2015

@author: rob
"""

from Collector import *
from HeadlineGrabber import *
import pandas as pd

import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from arch import arch_model
import statsmodels.api as sm

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)
        
        self.models = QtGui.QButtonGroup(self)
        self.noModel = QtGui.QCheckBox('No modelling')
        self.models.addButton(self.noModel)
        self.useArma = QtGui.QCheckBox('Use ARMA')
        self.models.addButton(self.useArma)
        self.useArch = QtGui.QCheckBox('Use ARCH')
        self.models.addButton(self.useArch)
        self.useGarch = QtGui.QCheckBox('Use GARCH')
        self.models.addButton(self.useGarch)
        
        
        self.symbol1 = QtGui.QLineEdit(self)
        self.symbol1.setText("AAPL")
        self.symbol2 = QtGui.QLineEdit(self)
        self.symbol2.setText("GNW")
        self.startdate = QtGui.QLineEdit(self)
        self.startdate.setText("2010-01-01")
        self.enddate = QtGui.QLineEdit(self)
        self.enddate.setText("2012-01-01")
        self.s = QtGui.QLineEdit(self)
        self.s.setText("2")
        self.samples = QtGui.QLineEdit(self)
        self.samples.setText("5")
        
        self.average = QtGui.QLabel("   Average: ")
        self.std = QtGui.QLabel("   Std: ")
        self.zscore = QtGui.QLabel(" ")
        self.conclusion = QtGui.QLabel(" ")
        

        # set the layoutcovariance
        
        menuLayout = QtGui.QVBoxLayout()
        menuLayout.addWidget(QtGui.QLabel("Symbol or market 1"))
        menuLayout.addWidget(self.symbol1)
        menuLayout.addWidget(QtGui.QLabel("Symbol or market 2"))
        menuLayout.addWidget(self.symbol2)
        menuLayout.addWidget(QtGui.QLabel("Start date"))
        menuLayout.addWidget(self.startdate)
        menuLayout.addWidget(QtGui.QLabel("End date"))
        menuLayout.addWidget(self.enddate)
        menuLayout.addWidget(QtGui.QLabel("Smoothing level (# of samples)"))
        menuLayout.addWidget(self.s)
        menuLayout.addWidget(QtGui.QLabel("Rolling correlation samples"))
        menuLayout.addWidget(self.samples)
        menuLayout.addWidget(self.noModel)
        #menuLayout.addWidget(self.useArma)
        #menuLayout.addWidget(self.useArch)
        menuLayout.addWidget(self.useGarch)
        menuLayout.addWidget(self.button)
        
        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(self.toolbar)
        plotLayout.addWidget(self.canvas)
        plotLayout.addWidget(self.average)
        plotLayout.addWidget(self.std)
        plotLayout.addWidget(self.zscore)
        plotLayout.addWidget(self.conclusion)
        
        layout = QtGui.QGridLayout()
        layout.addLayout(menuLayout,1,0)
        layout.addLayout(plotLayout,1,1)
        self.setLayout(layout)
        
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)
        
    def find_high_region(self, corrData):
        
        topAvg = -1.0
        topStd = -1.0
        startDates = []
        for date in corrData.axes[0]:
            if date < corrData.axes[0][-1]-timedelta(days=30):
                startDates.append(date)

        
        for date in startDates:
            avg = corrData[date:date+timedelta(days=30)].mean()
            std = corrData[date:date+timedelta(days=30)].std()
            if avg-std > topAvg-topStd:
                topAvg = avg
                topStd = std
                topDate = date

        return (topDate, topAvg, topStd)
        
    def find_low_region(self, corrData):
        
        topAvg = -1.0
        topStd = -1.0
        startDates = []
        for date in corrData.axes[0]:
            if date < corrData.axes[0][-1]-timedelta(days=30):
                startDates.append(date)

        
        for date in startDates:
            avg = corrData[date:date+timedelta(days=30)].mean()
            std = corrData[date:date+timedelta(days=30)].std()
            if avg-std < topAvg-topStd:
                topAvg = avg
                topStd = std
                topDate = date

        return (topDate, topAvg, topStd)

    def plot(self):
        # retrieve stock data
        c = Collector()
        s1 = self.symbol1.text()
        s2 = self.symbol2.text()
        samples = int(self.s.text())
        covsamples = int(self.samples.text())
        start = self.startdate.text()
        end = self.enddate.text()
        
        pltdata = pd.DataFrame()
        if s1 == "NYSE":
            f1 = c.get_nyse_stock_data(start, end)
        elif s1 == "SEHK":
            f1 = c.get_sehk_stock_data(start, end)
        elif s1 == "LSE":
            f1 = c.get_lse_stock_data(start, end)
        else:
            f1 = c.get_stock_data(s1,start,end)
        pltdata[s1] = pd.rolling_mean(f1.Return,samples)
        if s2 == "NYSE":
            f2 = c.get_nyse_stock_data(start, end)
        elif s2 == "SEHK":
            f2 = c.get_sehk_stock_data(start, end)
        elif s2 == "LSE":
            f2 = c.get_lse_stock_data(start, end)
        else:
            f2 = c.get_stock_data(s2,start,end)
        pltdata[s2] = pd.rolling_mean(f2.Return,samples)
        pltdata['Corr'] = pd.rolling_corr(pltdata[s1], pltdata[s2], covsamples)
        
        if self.useGarch.isChecked():
            am = arch_model(pltdata['Corr'][pd.notnull(pltdata['Corr'])], lags=5, mean="ARX")
            res = am.fit()
            pltdata['Corr2'] = res.resid
        #elif self.useArch.isChecked():
        #    am1 = arch_model(pltdata['Corr'][pd.notnull(pltdata['Corr'])], vol='ARCH', lags=5, mean="ARX")
        #    res = am1.fit(iter=5)
        #    pltdata['Corr2'] = res.resid
        #Trying to fit an ARMA model causes an unknown lockup. Disabled for now.
        #elif self.useArma.isChecked():
        #    print "Test"
        #    arma_res = sm.tsa.ARMA(pltdata['Corr'], (5,0))
        #    print arma_res
        #    arma_resres = arma_res.fit()
        #    pltdata['Corr2'] = arma_resres.resid
        #    print pltdata['Corr2']
        else:
            pltdata['Corr2'] = pltdata['Corr']
            
        high_data = self.find_high_region(pltdata['Corr2'])
        low_data = self.find_low_region(pltdata['Corr2'])
        zscore = (high_data[1] - low_data[1]) / low_data[2]
        
        print "Z-score is ", zscore        
        
        h = HeadlineGrabber()
        headline = h.get_headline(high_data[0].to_datetime())
        
        
        if abs(zscore) > 1:
            self.zscore.setText("Contagion found at "+str(high_data[0])+" with Z-score " + str(zscore))
            self.conclusion.setText("Headline for article: "+headline)
        else:
            self.zscore.setText("No contagion found")
            self.conclusion.setText(" ")
            
        
        
    
        pltdata['mean'] = [pltdata['Corr2'].mean()]*len(pltdata['Corr2'])
        pltdata['upperstd'] = [pltdata['Corr2'].mean()+pltdata['Corr2'].std()]*len(pltdata['Corr2'])
        pltdata['lowerstd'] = [pltdata['Corr2'].mean()-pltdata['Corr2'].std()]*len(pltdata['Corr2'])

        self.axes1.cla()
        self.axes2.cla()
        pltdata[s1].plot(ax=self.axes1, legend=True)
        pltdata[s2].plot(ax=self.axes1, legend=True)
        pltdata['Corr2'].plot(ax=self.axes2, legend=True)
        pltdata['mean'].plot(ax=self.axes2, legend=True)
        pltdata['upperstd'].plot(ax=self.axes2, legend=True)
        pltdata['lowerstd'].plot(ax=self.axes2, legend=True)
        self.std.setText("   Std: %0.3f" % pltdata['Corr2'].std())
        self.average.setText("   Average: %0.3f" % pltdata['Corr2'].mean())

        # refresh canvas
        self.canvas.draw()
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())





