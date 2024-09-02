import wx

class params_mini_panel(wx.Panel):
    def __init__(self, parent, param_label):
        wx.Panel.__init__(self, parent)
        self.param_label = param_label
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        # - create label and textctrl
        # - create vertical sizer
        # - add tabel and textctrl to sizer with padding
        self.label = wx.StaticText(self, label=param_label)
        self.text = wx.TextCtrl(self, size=(100,10))
        self.vbox.Add(self.label, wx.TOP|wx.LEFT|wx.RIGHT)
        self.vbox.Add(self.text, wx.BOTTOM|wx.LEFT|wx.RIGHT)#|wx.EXPAND)
        self.SetSizer(self.vbox)


    def SetLabel(self, label):
        self.label.SetLabel(label)


    def SetValue(self, value):
        self.text.SetValue(str(value))


    def GetValue(self):
        return self.text.GetValue()


    def SetValue(self, value):
        mystr = str(value)
        self.text.SetValue(mystr)


    def remove_widgets(self):
        N = len(self.vbox.GetChildren())
        print("N = %i" % N)
        for i in range(N):
            self.vbox.Remove(0)
        
        self.Layout()
        self.Update()



    def del_widgets(self):
        del self.text
        del self.label
        self.Layout()
        self.Update()




