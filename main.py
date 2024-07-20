import os
import wx
import csv
import wx.lib.newevent
import threading
import time
import pandas as pd
from data_viewer import GraphFrame, ArimaFrame, OhlcFrame, HmmFrame
from arima import arima_nodel, analyze_trend
from hmm_final import HMM_model

ProgressUpdateEvent, EVT_PROGRESS_UPDATE = wx.lib.newevent.NewEvent()

class Data(object):
    def __init__(self, stock, location):
        self.stock = stock
        self.location = location

class RightPanel(wx.Panel):
    def __init__(self, parent,*args, **kw):
        super().__init__(parent, *args, **kw)
        
        self.choices = ["ARIMA", "HMM", "Liquidity Zone"]
        self.data = pd.DataFrame()
        self.path = None
        self.train = None
        self.test = None
        self.prediction = None
        self.list = []
        self.df = None
        self.future_df = None
        self.future_df_clone = None


        self.txt = wx.StaticText(self, label="No data Data")
        self.combo_box = wx.ComboBox(self, choices=self.choices, style=wx.CB_READONLY, name="hola")
        self.combo_box.SetSelection(0)
        self.combo_box.SetValue("hola")
        self.model_txt = wx.StaticText(self, label="select training model")
        self.model_txt.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_EXTRALIGHT))
        self.model_txt.SetForegroundColour(wx.Colour(192,192,192))
        self.analyse_btn = wx.Button(self, label="Analyse")
        self.analyse_btn.Disable()
        self.preview = wx.Button(self, label="Preview")
        self.preview.Disable()
        self.buy = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.sell = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.progress = wx.Gauge(self, range=100)
        self.progress_txt = wx.StaticText(self)

        


        sbox = wx.StaticBox(self)
        self.buy_txt = wx.StaticText(self, label="Buy Price")
        self.buy_txt.SetForegroundColour(wx.GREEN)
        self.buy_txt.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_EXTRALIGHT))

        self.sell_txt = wx.StaticText(self, label="Sell Price")
        self.sell_txt.SetForegroundColour(wx.RED)
        self.sell_txt.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_EXTRALIGHT))



        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.txt, 0, wx.ALL|wx.CENTER, 15)
        main_sizer.Add(self.model_txt, 0, wx.CENTER|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)
        main_sizer.Add(self.combo_box, 0, wx.LEFT|wx.RIGHT|wx.CENTER|wx.EXPAND, 10)
        main_sizer.AddSpacer(10)
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        buy_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buy_sizer.Add(self.buy_txt, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        buy_sizer.AddSpacer(5)
        buy_sizer.Add(self.buy, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL,10)


        call_sizer = wx.BoxSizer(wx.HORIZONTAL)
        call_sizer.Add(self.sell_txt, wx.ALL|wx.ALIGN_CENTER_VERTICAL,5)
        call_sizer.AddSpacer(5)
        call_sizer.Add(self.sell, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL,10)

        sbox_sizer.Add(buy_sizer, wx.ALL|wx.CENTER, 5)
        sbox_sizer.AddSpacer(10)
        sbox_sizer.Add(call_sizer, wx.ALL|wx.CENTER, 5)
        main_sizer.Add(sbox_sizer, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.CENTER|wx.EXPAND, 10)
        main_sizer.Add(self.analyse_btn, 0, wx.TOP|wx.LEFT|wx.RIGHT|wx.CENTER, 20)
        main_sizer.Add(self.preview, 0, wx.TOP|wx.CENTER, 10)
        main_sizer.AddSpacer(40)
        main_sizer.Add(self.progress_txt, 0, wx.LEFT, 10)
        main_sizer.Add(self.progress, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        self.SetSizer(main_sizer)

        #event handlers
        self.Bind(wx.EVT_BUTTON, self.onClickModel, self.analyse_btn)
        self.Bind(EVT_PROGRESS_UPDATE, self.onProgress)
        # self.Bind(EVT_PROGRESS_UPDATE, self.onProgress_hmm)
        self.Bind(wx.EVT_BUTTON, self.onPreview, self.preview)

    def onPreview(self, event):
        if self.combo_box.GetSelection() == 0:
            ArimaFrame(self, self.train, self.test, self.prediction)
        if self.combo_box.GetSelection() == 1:
            HmmFrame(self, self.df, self.future_df)

    def enable_analyse(self):
        self.analyse_btn.Enable()


    def onClickModel(self, event):
        selected_index = self.combo_box.GetSelection()
        print(selected_index)

        if selected_index != wx.NOT_FOUND:
            if selected_index == 0:
                label = self.txt.GetLabel()
                if label == 'Apple.csv':
                    order = (2,3,9)
                    self.on_run_model(order)
                elif label == 'Nvidia.csv':
                    order = (7,7,10)
                    self.on_run_model(order)
                elif label == 'Reliance.csv':
                    order = (2,3,5)
                    self.on_run_model(order)
                elif label == 'Tesla.csv':
                    order = (7,1,3)
                    self.on_run_model(order)
            elif selected_index == 1:
                self.on_run_hmm()

            # elif selected_index == 2:


    def on_run_hmm(self):
        self.progress_txt.SetLabel("Running model ...")
        self.progress.SetValue(0)
        threading.Thread(target=self.run_hmm).start()
    
    def run_hmm(self):
        n=20
        for i in range(n):
            wx.PostEvent(self, ProgressUpdateEvent(value=int((i+1)/n*100)))
            time.sleep(0.3)
            if self.progress.GetValue() == 75:
                break
        
        self.df, self.future_df = HMM_model(self.data)
        self.future_df_clone = self.future_df['Future_Price']
        wx.PostEvent(self, ProgressUpdateEvent(value=100))
        time.sleep(2)
        self.progress.SetValue(0)
        self.progress_txt.SetLabel("")
        return


    # def onProgress_hmm(self, event):
    #     self.progress.SetValue(event.value)
    #     if event.value == 100 :
    #         self.buy_sell_price(self.future_df)
    #         self.preview.Enable()






    def on_run_model(self, order_param):
        self.progress_txt.SetLabel("Running model ...")
        self.progress.SetValue(0)
        threading.Thread(target=self.run_model,args=(self.data, order_param)).start()
        

    def run_model(self, data, order):
        n = 20
        for i in range(n):
            wx.PostEvent(self, ProgressUpdateEvent(value=int((i+1)/n*100)))
            time.sleep(0.1)
            if self.progress.GetValue() == 75:
                break
        
        self.train, self.test, self.prediction = arima_nodel(data, order)
        wx.PostEvent(self, ProgressUpdateEvent(value=100))
        time.sleep(2)
        self.progress.SetValue(0)
        self.progress_txt.SetLabel("")
        return

    def onProgress(self, event):
        if self.combo_box.GetSelection() == 0:
            self.progress.SetValue(event.value)
            if event.value == 100 :
                self.buy_sell_price(self.prediction)
                self.preview.Enable()
        
        elif self.combo_box.GetSelection() == 1:
            
            self.progress.SetValue(event.value)
            if event.value == 100 :
                print("hola")
                self.buy_sell_price(self.future_df_clone)
                self.preview.Enable()


    
    def buy_sell_price(self, llist:pd.Series):
        self.buy.Clear()
        self.sell.Clear()
        llist = llist.to_list()
        llist = [round(element, 1) for element in llist]
        trend = analyze_trend(llist)
        if trend == True:
            self.buy.SetValue(str(llist[0]))
        elif trend == False:
            self.sell.SetValue(str(llist[0]))


    def update_data(self,path):
        self.txt.SetLabel(os.path.basename(path))
        with open(path, 'r') as file:
            self.data = pd.read_csv(file, parse_dates=['Date'])
        
 


class LeftPanel(wx.Panel):
    def __init__(self, parent, right_panel, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.right_panel = right_panel
        self.model_data = pd.DataFrame()

        self.load_btn = wx.Button(self, label="Load Data")
        
        self.txt = wx.StaticText(self, label="Welcome user")
        self.txt.SetForegroundColour(wx.Colour(128,128,128))
        self.txt.SetForegroundColour(wx.Colour(146,193,170))
        self.txt.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_EXTRALIGHT))

        # preview button
        self.graph_btn = wx.Button(self, label = "Graph")
        self.ohlc_btn = wx.Button(self, label = "OHLC")
        self.data_btn = wx.Button(self, label = "Data")

        self.graph_btn.Disable()
        self.ohlc_btn.Disable()
        self.data_btn.Disable()

        self.listbox = wx.ListBox(self, size=(50,100))
        default_text = "                No Stocks Loaded"
        self.listbox.Append(default_text)

        #Layout
        sbox = wx.StaticBox(self, label="Preview")
        sbox_sizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        sbox_sizer.Add(self.graph_btn, 0, wx.ALL, 5)
        sbox_sizer.Add(self.ohlc_btn, 0, wx.ALL, 5)
        sbox_sizer.Add(self.data_btn, 0, wx.ALL, 5)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row_sizer.Add(self.load_btn, 0, wx.ALL)
        row_sizer.Add(self.txt, 0, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 100)
        

        main_sizer.Add(row_sizer, 0, wx.LEFT|wx.RIGHT|wx.TOP, 15)
        main_sizer.Add(self.listbox, 0, wx.ALL|wx.EXPAND, 15)
        main_sizer.AddSpacer(10)
        main_sizer.Add(sbox_sizer, 0, wx.ALIGN_CENTER|wx.DOWN)
        self.SetSizer(main_sizer)



        #event handlers
        self.Bind(wx.EVT_BUTTON, self.onLoad, self.load_btn)
        self.Bind(wx.EVT_LISTBOX, self.onListSelect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)

        # wx.EVT_RIGHT_UP
        # wx.EVT_RIGHT_DCLICK
        


    def onRightClick(self, event):
        # self.popup_menu = wx.Menu()
        # stock = self.popup_menu.Append(wx.ID_ANY,"Analyse")
        # self.Bind(wx.EVT_MENU, self.SetStock, stock)

        # pos = event.GetPosition()
        # item = self.listbox.HitTest(pos)

        # if item != wx.NOT_FOUND:
        #     self.listbox.SetSelection(item)
        
        # self.PopupMenu(self.popup_menu, event.GetPosition())
        # self.popup_menu.Destroy()

        # Create a popup menu
        self.popup_menu = wx.Menu()
        preview_item = self.popup_menu.Append(wx.ID_ANY, "Analyse Data")
        self.Bind(wx.EVT_MENU, self.SetStock, preview_item)

        # Get the item index under the cursor
        pos = event.GetPosition()
        item = self.listbox.HitTest(pos)

        # Set the selection to the item under the cursor
        if item != wx.NOT_FOUND:
            self.listbox.SetSelection(item)

        # Show the popup menu
        self.PopupMenu(self.popup_menu, event.GetPosition())
        self.popup_menu.Destroy()

    def SetStock(self, event):
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            filepath = self.listbox.GetClientData(selection)
            self.right_panel.update_data(filepath)
            self.right_panel.enable_analyse()

            with open(filepath, 'r') as data:
                self.model_data = pd.read_csv(data)


    def onListSelect(self, event):
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            path = self.listbox.GetClientData(selection)

            def onGraph(self, path):
                GraphFrame(self, path)
            
            def onOhlc(self, path):
                OhlcFrame(self, path)

            def onData_sheet(self, path):
                    with open(path, 'r', newline='') as csvfile:
                        reader = csv.reader(csvfile)
                        preview = ''
                        for i, row in enumerate(reader):
                            preview += ', '.join(row) + '\n'
                            if i >= 9:  # Limit to previewing first 10 rows
                                break
                    wx.MessageBox(preview, 'Preview of ' + os.path.basename(path), wx.OK)

    
            self.graph_btn.Enable()
            self.Bind(wx.EVT_BUTTON, lambda evt:onGraph(self, path), self.graph_btn)
            self.Bind(wx.EVT_BUTTON, lambda evt:onOhlc(self, path), self.ohlc_btn)
            self.Bind(wx.EVT_BUTTON, lambda evt:onData_sheet(self, path), self.data_btn)
            self.ohlc_btn.Enable()
            self.data_btn.Enable()






    def onLoad(self, event):
        with wx.FileDialog (self, "Open CSV files", wildcard="CSV files (*.csv)|*.csv",
                            style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE) as filedialog:


            if filedialog.ShowModal() == wx.ID_CANCEL: 
                return

            paths = filedialog.GetPaths() 
            self.listbox.Clear()

            for path in paths:
                self.listbox.Append(os.path.basename(path), path)
        



class MainFrame(wx.Frame):
    def __init__(self, *args, **kw):
        style = wx.STAY_ON_TOP | wx.DEFAULT_FRAME_STYLE
        super().__init__(None, title="Project X.II", style=style, size=((475,365)), *args, **kw)

        splitter = wx.SplitterWindow(self, style=wx.SP_THIN_SASH)
        self.right_panel = RightPanel(splitter)
        self.left_panel = LeftPanel(splitter, self.right_panel)
        
        
        self.right_panel.SetBackgroundColour(wx.Colour(58,64,61))
        splitter.SplitVertically(self.left_panel, self.right_panel)
        splitter.SetSashPosition(300)


        self.Centre()
        self.Show()

app = wx.App()
frame = MainFrame()
app.MainLoop()

