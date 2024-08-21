import wx

import numpy as np

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.cbook as cbook
import matplotlib.cm as cm
from matplotlib.figure import Figure

ERR_TOL = 1e-5  # floating point slop for peak-detection


from wxbd_gui.wx_add_block_dialog import AddBlockDialog


class PlotPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, -1)

        self.fig = Figure((5, 4), 75)
        self.canvas = FigureCanvas(self, -1, self.fig)
        #self.toolbar = NavigationToolbar(self.canvas)  # matplotlib toolbar
        #self.toolbar.Realize()

        # Now put all into a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # This way of adding to sizer allows resizing
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        # Best to allow the toolbar to resize!
        #sizer.Add(self.toolbar, 0, wx.GROW)
        self.SetSizer(sizer)
        self.Fit()

    def init_plot_data(self):
        ax = self.fig.add_subplot()

        x = np.arange(120.0) * 2 * np.pi / 60.0
        y = np.arange(100.0) * 2 * np.pi / 50.0
        self.x, self.y = np.meshgrid(x, y)
        z = np.sin(self.x) + np.cos(self.y)
        self.im = ax.imshow(z, cmap=cm.RdBu, origin='lower')

        zmax = np.max(z) - ERR_TOL
        ymax_i, xmax_i = np.nonzero(z >= zmax)
        if self.im.origin == 'upper':
            ymax_i = z.shape[0] - ymax_i
        self.lines = ax.plot(xmax_i, ymax_i, 'ko')

        #self.toolbar.update()  # Not sure why this is needed - ADS

    def GetToolBar(self):
        # You will need to override GetToolBar if you are using an
        # unmanaged toolbar in your frame
        #return self.toolbar
        pass

    def OnWhiz(self, event):
        self.x += np.pi / 15
        self.y += np.pi / 20
        z = np.sin(self.x) + np.cos(self.y)
        self.im.set_array(z)

        zmax = np.max(z) - ERR_TOL
        ymax_i, xmax_i = np.nonzero(z >= zmax)
        if self.im.origin == 'upper':
            ymax_i = z.shape[0] - ymax_i
        self.lines[0].set_data(xmax_i, ymax_i)

        self.canvas.draw()



class Window(wx.Frame):
    def __init__(self, title):
        super().__init__(parent = None, title = title)
        panel = wx.Panel(self)
 
        wrapper = wx.BoxSizer(wx.VERTICAL)
 
        sizer = wx.FlexGridSizer(3, 2, 5, 5)

        self.plotpanel = PlotPanel(panel)
        self.plotpanel.init_plot_data()

        sizer.AddMany([ (wx.StaticText(panel, label = "Username")),
                        (wx.TextCtrl(panel), 0, wx.EXPAND),
                        (wx.StaticText(panel, label = "Password")),
                        (wx.TextCtrl(panel), 0, wx.EXPAND),
                        (wx.StaticText(panel, label = "Address")),
                        (self.plotpanel, 0, wx.EXPAND) ])
 
        sizer.AddGrowableRow(2, 1)
        sizer.AddGrowableCol(1, 1)
 
        wrapper.Add(sizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
 
        panel.SetSizer(wrapper)

        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        exitMenuItem = fileMenu.Append(wx.Window.NewControlId(), "Exit",
                                       "Exit the application")
        otherMenuItem = fileMenu.Append(wx.Window.NewControlId(), "Other",
                                       "Do nothing")

        menuBar.Append(fileMenu, "&File")
        

        blockMenu = wx.Menu()
        addBlockMenuItem = blockMenu.Append(wx.Window.NewControlId(), "Add Block",
                                       "Add a new block to the block diagram system")
        menuBar.Append(blockMenu, "&Block")
  
        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)
        self.Bind(wx.EVT_MENU, self.onAddBlock, addBlockMenuItem)
        self.SetMenuBar(menuBar)
        
        self.Centre() 
        self.Show(True)
  		
			
 
 
    def onExit(self, event):
        """"""
        self.Close()


    def onAddBlock(self, event):
        """"""
        dlg = AddBlockDialog(self, "Add Block Dialog")
        dlg.ShowModal()


         

