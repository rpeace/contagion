# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 10:43:18 2015

@author: rob
"""

from Collector import *
import connection
from HeadlineGrabber import *
import pandas as pd

import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from arch import arch_model
import statsmodels.api as sm
import scipy.stats
import seaborn as sns

class Window(QtGui.QDialog):    
    
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        
        staySmall = QtGui.QSizePolicy()
        staySmall.setHorizontalPolicy(QtGui.QSizePolicy.Fixed)
        staySmall.setVerticalPolicy(QtGui.QSizePolicy.Fixed)
        
        goBig = QtGui.QSizePolicy()
        goBig.setHorizontalPolicy(QtGui.QSizePolicy.Ignored)
        goBig.setVerticalPolicy(QtGui.QSizePolicy.Ignored)
        
        self.canvas.setSizePolicy(goBig)
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)
        
        self.sector1 = QtGui.QComboBox()
        self.sector1.addItem("(All)")
        self.region1 = QtGui.QComboBox()
        self.region1.currentIndexChanged.connect(self.update_country1)
        self.region1.addItem("(All)")
        self.country1 = QtGui.QComboBox()
        self.country1.addItem("(All)")
        self.market1 = QtGui.QComboBox()
        self.market1.addItem("(All)")
        self.symbol1 = QtGui.QLineEdit()
        
        self.sector2 = QtGui.QComboBox()
        self.sector2.addItem("(All)")
        self.region2 = QtGui.QComboBox()
        self.region2.currentIndexChanged.connect(self.update_country2)
        self.region2.addItem("(All)")
        self.country2 = QtGui.QComboBox()
        self.country2.addItem("(All)")
        self.market2 = QtGui.QComboBox()
        self.market2.addItem("(All)")
        self.symbol2 = QtGui.QLineEdit()
        
        for sector in connection.get_sectors():
            self.sector1.addItem(sector)
            self.sector2.addItem(sector)
        for region in connection.get_regions():
            self.region1.addItem(region)
            self.region2.addItem(region)
        for country in connection.get_countries(""):
            self.country1.addItem(country)
            self.country2.addItem(country)
        for market in connection.get_markets():
            self.market1.addItem(market)
            self.market2.addItem(market)
        
        self.models = QtGui.QButtonGroup(self)
        self.noModel = QtGui.QCheckBox('No modelling')
        self.models.addButton(self.noModel)
        self.useArma = QtGui.QCheckBox('Model with ARMA')
        self.models.addButton(self.useArma)
        self.useArch = QtGui.QCheckBox('Model with ARCH')
        self.models.addButton(self.useArch)
        self.useGarch = QtGui.QCheckBox('Model with GARCH')
        self.models.addButton(self.useGarch)
        
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
        self.average.setSizePolicy(staySmall)
        self.std.setSizePolicy(staySmall)
        self.zscore.setSizePolicy(staySmall)
        self.conclusion.setSizePolicy(staySmall)
        

        # set the layoutcovariance
        input1layout = QtGui.QVBoxLayout()
        input1layout.addWidget(QtGui.QLabel("Sector"))
        input1layout.addWidget(self.sector1)
        input1layout.addWidget(QtGui.QLabel("Region"))
        input1layout.addWidget(self.region1)
        input1layout.addWidget(QtGui.QLabel("Country"))
        input1layout.addWidget(self.country1)
        input1layout.addWidget(QtGui.QLabel("Market"))
        input1layout.addWidget(self.market1)
        input1layout.addWidget(QtGui.QLabel("Symbol"))
        input1layout.addWidget(self.symbol1)

        input2layout = QtGui.QVBoxLayout()
        input2layout.addWidget(QtGui.QLabel("Sector"))
        input2layout.addWidget(self.sector2)
        input2layout.addWidget(QtGui.QLabel("Region"))
        input2layout.addWidget(self.region2)
        input2layout.addWidget(QtGui.QLabel("Country"))
        input2layout.addWidget(self.country2)
        input2layout.addWidget(QtGui.QLabel("Market"))
        input2layout.addWidget(self.market2)
        input2layout.addWidget(QtGui.QLabel("Symbol"))
        input2layout.addWidget(self.symbol2)
        
        # User input that is not specific to each market. Also a button
        input3layout = QtGui.QVBoxLayout()
        input3layout.addWidget(QtGui.QLabel("Start date"))
        input3layout.addWidget(self.startdate)
        input3layout.addWidget(QtGui.QLabel("End date"))
        input3layout.addWidget(self.enddate)
        input3layout.addWidget(QtGui.QLabel("Smoothing level (# of samples)"))
        input3layout.addWidget(self.s)
        input3layout.addWidget(QtGui.QLabel("Rolling correlation samples"))
        input3layout.addWidget(self.samples)
        input3layout.addWidget(self.noModel)
        input3layout.addWidget(self.useArma)
        input3layout.addWidget(self.useArch)
        input3layout.addWidget(self.button)
        
        menuLayout = QtGui.QGridLayout()
        menuLayout.addWidget(QtGui.QLabel("Select market data"))
        menuLayout.addLayout(input1layout,1,0)
        menuLayout.addLayout(input2layout,1,1)
        menuLayout.addLayout(input3layout, 4, 0, 1, 2)
        
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
        
    def update_country1(self):
        self.country1.clear()
        self.country1.addItem("(All)")
        if self.region1.currentText() == "(All)":
            for country in connection.get_countries(""):
                self.country1.addItem(country)
        else:
            for country in connection.get_countries(self.region1.currentText()):
                self.country1.addItem(country)
        return
        
    def update_country2(self):
        self.country2.clear()
        self.country2.addItem("(All)")
        if self.region2.currentText() == "(All)":
            for country in connection.get_countries(""):
                self.country2.addItem(country)
        else:
            for country in connection.get_countries(self.region2.currentText()):
                self.country2.addItem(country)
        return
        
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

        return (topDate, corrData[topDate:topDate+timedelta(days=30)])
        
    def find_low_region(self, corrData):
        
        topAvg = 1.0
        topStd = 1.0
        startDates = []
        for date in corrData.axes[0]:
            if date < corrData.axes[0][-1]-timedelta(days=60):
                startDates.append(date)

        
        for date in startDates:
            avg = corrData[date:date+timedelta(days=60)].mean()
            std = corrData[date:date+timedelta(days=60)].std()
            if avg-std < topAvg-topStd:
                topAvg = avg
                topStd = std
                topDate = date

        return (topDate, corrData[topDate:topDate+timedelta(days=30)])

    def plot(self):
        # retrieve stock data
        c = Collector()
        region1 = self.region1.currentText()
        region2 = self.region2.currentText()
        market1 = self.market1.currentText()
        market2 = self.market2.currentText()
        sector1 = self.sector1.currentText()
        sector2 = self.sector2.currentText()
        country1 = self.country1.currentText()
        country2 = self.country2.currentText()
        s1 = self.symbol1.text()
        s2 = self.symbol2.text()
        samples = int(self.s.text())
        covsamples = int(self.samples.text())
        start = self.startdate.text()
        end = self.enddate.text()
        
        returnSeries1 = c.get_stock_data(market1, s1, start, end, region1, country1, sector1)
        returnSeries2 = c.get_stock_data(market2, s2, start, end, region2, country2, sector2) 

        pltdata = pd.DataFrame()
        pltdata["1"] = pd.rolling_mean(returnSeries1,samples)
        pltdata["2"] = pd.rolling_mean(returnSeries2,samples)
        pltdata['Corr'] = pd.rolling_corr(pltdata["1"], pltdata["2"], covsamples)
        
        
#        if self.useGarch.isChecked():
#            am = arch_model(pltdata['Corr'][pd.notnull(pltdata['Corr'])], lags=5, mean="ARX")
#            res = am.fit()
#            pltdata['Corr2'] = res.resid
        if self.useArch.isChecked():
            am1 = arch_model(pltdata['Corr'][pd.notnull(pltdata['Corr'])], vol='ARCH', lags=5, mean="ARX")
            res = am1.fit(iter=5)
            pltdata['Corr2'] = res.resid
        #Trying to fit an ARMA model causes an unknown lockup. Disabled for now.
        elif self.useArma.isChecked():
            arma_res = sm.tsa.ARMA(pltdata['Corr'], (5,0))
            arma_resres = arma_res.fit()
            pltdata['Corr2'] = arma_resres.resid
        else:
            pltdata['Corr2'] = pltdata['Corr']
            
        high_data = self.find_high_region(pltdata['Corr2'])
        low_data = self.find_low_region(pltdata['Corr2'])
        
        pscore = scipy.stats.ttest_ind(high_data[1], low_data[1])
        
        print "T test result:", pscore
        
        if pscore[1] < 0.05:
#            h = HeadlineGrabber()
#            headline = h.get_headline(high_data[0].to_datetime())
            self.zscore.setText("Contagion found at "+str(high_data[0])+" with P-score " + str(pscore[1]) + "                                                                                                            ")
#            self.conclusion.setText("Headline for article: "+headline)
        else:
            self.zscore.setText("No contagion found")
#            self.conclusion.setText(" ")
        
        pltdata['mean'] = [pltdata['Corr2'].mean()]*len(pltdata['Corr2'])
        pltdata['upperstd'] = [pltdata['Corr2'].mean()+pltdata['Corr2'].std()]*len(pltdata['Corr2'])
        pltdata['lowerstd'] = [pltdata['Corr2'].mean()-pltdata['Corr2'].std()]*len(pltdata['Corr2'])
        
        print pltdata

        self.axes1.cla()
        self.axes2.cla()
        pltdata["1"].plot(ax=self.axes1, legend=True)
        pltdata["2"].plot(ax=self.axes1, legend=True)
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





