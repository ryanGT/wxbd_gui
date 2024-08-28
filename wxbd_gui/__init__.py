import wx

import numpy as np

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.cbook as cbook
import matplotlib.cm as cm
from matplotlib.figure import Figure

ERR_TOL = 1e-5  # floating point slop for peak-detection

## Open-Loop RC plan:
##
## - create step input
##     - auto-place it
## - create PWM actuator
## - create ADC sensor
## - create plant
##     - auto-place the plant
## - set the input for the plant
## - draw the wire
## - generate the code
##
## Closed-Loop RC:
##
## - add summing junction
## - place the summing junction
## - allow block placements to be adjusted
## - set both inputs for summing juntion
## - draw wires
## - generate code


from wxbd_gui.wx_add_block_dialog import AddBlockDialog

import py_block_diagram as pybd


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
        self.ax = ax

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
        super().__init__(parent = None, title = title, size=(900,600))
        panel = wx.Panel(self)
 
        wrapper = wx.BoxSizer(wx.VERTICAL)
 
        sizer = wx.FlexGridSizer(3, 2, 5, 5)

        self.plotpanel = PlotPanel(panel)
        self.plotpanel.init_plot_data()


        self.block_listbox = wx.ListBox(panel, size = (100,-1), \
                             choices=[], style = wx.LB_SINGLE)


        sizer.AddMany([ (wx.StaticText(panel, label = "")),\
                        (wx.StaticText(panel, label = "Blocks")),
                        (self.plotpanel, 0, wx.EXPAND), \
                        (self.block_listbox, 0, wx.EXPAND)])
 
        sizer.AddGrowableRow(1, 1)
        sizer.AddGrowableCol(0, 1)
 
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
        
        self.bd = pybd.block_diagram()

        self.colorful_wires = 1

        self.Centre() 
        self.Show(True)
  		
			
    def append_block_to_dict(self, block_name, new_block):
        self.bd.append_block_to_dict(block_name, new_block)
        success_place = self.bd.guess_block_placement(block_name, new_block)
        if success_place == 1:
            print("new block successfully placed")
        else:
            print("issue placing new block")
        # update listbox
        #!# Tk: self.block_list_var.set(self.bd.block_name_list)
        # - wxpython?
        #     - I think I need a listbox somewhere
        #     - should go on main page off to the right of the mpl panel
        self.block_listbox.Append(block_name)


    def onExit(self, event):
        """"""
        self.Close()


    def onAddBlock(self, event):
        """"""
        dlg = AddBlockDialog(self, "Add Block Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should draw something.")
            # need to place the new block
            self.on_draw_btn()

        dlg.Destroy()


         
    def on_draw_btn(self, *args, **kwargs):
        print("you pressed draw")
        ax = self.plotpanel.ax
        ax.clear()
        self.bd.update_block_list()
        block_list = self.bd.block_list
        print("block_list: %s" % block_list)
        if len(block_list) > 0:
            self.bd.ax = ax
            self.bd.draw(colorful_wires=self.colorful_wires)

            try:
                xlims = self.bd.get_xlims()
                ylims = self.bd.get_ylims()
                ax.set_xlim(xlims)
                ax.set_ylim(ylims)
                #self.xmin_var.set(str(xlims[0]))
                #self.xmax_var.set(str(xlims[1]))
                #self.ymin_var.set(str(ylims[0]))
                #self.ymax_var.set(str(ylims[1]))
            except:
                print("axes limits not set")

            self.bd.axis_off()
            self.plotpanel.canvas.draw()



