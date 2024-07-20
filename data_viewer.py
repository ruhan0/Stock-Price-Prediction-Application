import wx
import datetime as dt
# matplotlib.use('WXAgg')
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import numpy as np


class GraphPanel(wx.Panel):
    def __init__(self, parent, filepath, *args, **kw):
        super().__init__(parent, *args, **kw)

        df = pd.DataFrame()
        with open(filepath, 'r') as csvfile:
            df = pd.read_csv(csvfile)

        self.figure = Figure(figsize=(2,2))
        self.fig1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()



        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()
        


        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        self.fig1.set_xlabel('Year')
        self.fig1.set_ylabel('Price')
        self.fig1.set_title('Stock Price Historical Data')
        self.fig1.plot(df['Close'], label="daily price", color='orange', linestyle='solid')
        self.fig1.legend(title="daily price")

class ArimaPanel(wx.Panel):
    def __init__(self, parent, train:pd.Series, test:pd.Series, prediction:pd.Series):
        super().__init__(parent)

        self.figure = Figure(figsize=(2,2))
        self.fig1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        self.fig1.set_xlabel('Date')
        self.fig1.set_ylabel('Price')
        self.fig1.set_title('Future Forecasting')
        self.fig1.plot(train, label="Train", color='black', linestyle='solid')
        self.fig1.plot(test, label="Test", color='blue', linestyle='solid')
        self.fig1.plot(test.index, prediction, label="predicted", color='red')
        self.fig1.legend()
        
class HmmPanel(wx.Panel):
    def __init__(self, parent, df:pd.DataFrame, future_df:pd.DataFrame):
        super().__init__(parent)

        self.figure = Figure(figsize=(2,2))
        self.fig1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        self.fig1.set_xlabel('Date')
        self.fig1.set_ylabel('Price')
        self.fig1.set_title('Future Forecasting')
        self.fig1.plot(df.index, df['Close'],label="Actual Price", color='black', linestyle='solid')
        # self.fig1.plot(df.index, df['predicted_price'],label="Predicted Price", color='blue', linestyle='solid')
        self.fig1.plot(future_df.index, future_df['Future_Price'], label="Future Predicted Price", color='red')
        self.fig1.legend()


class HmmFrame(wx.Frame):
    def __init__(self, parent, df, future_df):
        super().__init__(parent, title="ARIMA Graph", size=(600,500))

        self.panel = HmmPanel(self ,df, future_df)
        self.Show()

        

class ArimaFrame(wx.Frame):
    def __init__(self, parent, train, test, prediction):
        super().__init__(parent, title="ARIMA Graph", size=(600,500))

        self.panel = ArimaPanel(self, train, test, prediction)
        self.Show()


class OhlcPanel(wx.Panel):
    def __init__(self, parent, filepath):
        super().__init__(parent)

        df = pd.DataFrame()
        with open(filepath, 'r') as csvfile:
            df = pd.read_csv(csvfile)

        self.figure = Figure(figsize=(2,2))
        self.fig1 = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()



        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.SetSizer(sizer)
        self.Fit()

        df = df.reset_index()
        df = df[-30:]
        green_df = df[df.Close > df.Open].copy()
        green_df["Height"] = green_df["Close"] - green_df["Open"]

        red_df = df[df.Close < df.Open].copy()
        red_df["Height"] = red_df["Open"] - red_df["Close"]

        self.fig1.vlines(x=green_df["Date"], ymin=green_df["Low"], ymax=green_df["High"],
           color="green")
        self.fig1.vlines(x=red_df["Date"], ymin=red_df["Low"], ymax=red_df["High"],
           color="orangered")
        
        self.fig1.bar(x=green_df["Date"], height=green_df["Height"], bottom=green_df["Open"], color="green");

        self.fig1.bar(x=red_df["Date"], height=red_df["Height"], bottom=red_df["Close"], color="orangered");

        self.fig1.set_xlabel("Date")
        self.fig1.set_ylabel("Price ($)")
        self.fig1.set_title("OHLC Candlestick Chart")
        self.fig1.tick_params(axis='x', colors='white')





class OhlcFrame(wx.Frame):
    def __init__(self, parent, filepath, *args, **kw):
        super().__init__(parent, title="OHCL graph",size=(600,500))

        self.panel = OhlcPanel(self, filepath)
        self.Show()


class GraphFrame(wx.Frame):
    def __init__(self, parent, filepath, *args, **kw):
        super().__init__(parent, title="graph",size=(600,500),*args, **kw)

        self.panel = GraphPanel(self, filepath)
        self.Show()




# app = wx.App()
# frame = GraphFrame()
# app.MainLoop()