import wx

version = '1.0.2'

import numpy as np
import os, shutil, re, sys
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import \
    NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.cbook as cbook
import matplotlib.cm as cm
from matplotlib.figure import Figure

from krauss_misc import txt_mixin, rwkos
## ToDo:
##
## - make option to specify input(s) later
##    - need an input dialog
## - add keyboard short cuts (started)
## - add column labels to serial output in menu code

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


from wxbd_gui.wx_add_block_dialog import AddBlockDialog, ReplaceBlockDialog
from wxbd_gui.wx_add_actuator_or_sensor_dialog import AddActuatorDialog
from wxbd_gui.wx_set_inputs_dialog import SetInputsDialog
from wxbd_gui.wx_menu_params_dialog import MenuParamsDialog
from wxbd_gui.wx_placement_dialog import PlacementDialog
import py_block_diagram as pybd


def dict_to_key_value_strings(mydict):
    """Helper function for saving a dictionary to a text value by
    converting it to key:value strings as a list"""
    mylist = []
    pat = "%s:%s"
    for key, value in mydict.items():
        val_str = str(value)
        cur_str = pat % (key, val_str)
        mylist.append(cur_str)

    return mylist



class PlotPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, -1)

        self.fig = Figure((9, 7), 75)
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
        save_id = wx.Window.NewControlId()
        load_id = wx.Window.NewControlId()

        SaveMenuItem = fileMenu.Append(save_id, "Save to CSV", \
                                       "Save block diagram model to a .csv file")
        LoadMenuItem = fileMenu.Append(load_id, "Load from CSV", \
                                       "Load block diagram model from a .csv file")
        exitMenuItem = fileMenu.Append(wx.Window.NewControlId(), "Exit", \
                                       "Exit the application")

        about_menu = wx.Menu()
        versionMenuItem = about_menu.Append(wx.Window.NewControlId(), \
                                            "Show Version", \
                                            "Show versions message")

        a_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('L'), load_id ), \
                                     (wx.ACCEL_CTRL,  ord('S'), save_id )])
        self.SetAcceleratorTable(a_tbl)

        code_gen_menu = wx.Menu()
        arduino_code_gen = wx.Menu()
        set_arduino_template_MenuItem = arduino_code_gen.Append(wx.Window.NewControlId(), \
                        "Set Arduino Template File", \
                        "Open dialog to locate the Arduino template file")
        get_arduino_template_MenuItem = arduino_code_gen.Append(wx.Window.NewControlId(), \
                        "Get Arduino Template File", \
                        "Show the path to the Arduino Template File")
        set_arduino_output_MenuItem = arduino_code_gen.Append(wx.Window.NewControlId(), \
                        "Set Arduino Output Folder", \
                        "Open dialog to select the Arduino output folder")
        gen_arduino_code_MenuItem = arduino_code_gen.Append(wx.Window.NewControlId(), \
                        "Generate Arduino Code", \
                        "Open the template file and insert block diagram code in places")



        code_gen_menu.AppendSubMenu(arduino_code_gen, "Arduino Code Generation")

        menuBar.Append(fileMenu, "&File")



        blockMenu = wx.Menu()
        addBlockMenuItem = blockMenu.Append(wx.Window.NewControlId(), "Add Block",
                                       "Add a new block to the block diagram system")
        setInputsMenuItem = blockMenu.Append(wx.Window.NewControlId(), \
                        "Set Input(s)", "Specify the input(s) for a block")
        ReplaceBlockMenuItem = blockMenu.Append(wx.Window.NewControlId(), \
                                                "Replace Block",
                                       "Replace a block in the block diagram system")
        editPlacementMenuItem = blockMenu.Append(wx.Window.NewControlId(), \
                                                "Editted Block Placement",
                                       "Change where a block is placed on the block diagram")


        sysMenu = wx.Menu()
        menuParamsMenuItem = sysMenu.Append(wx.Window.NewControlId(), \
                    "Set Menu Params", \
                    "Choose which parameters should be requested each time before running a test")

        #addActuatorMenuItem = blockMenu.Append(wx.Window.NewControlId(), "Add Actuator",
        #                               "Add a new block to the block diagram system")

        menuBar.Append(blockMenu, "&Block")
        menuBar.Append(sysMenu, "&System")

        menuBar.Append(code_gen_menu, "&Code Generation")
        menuBar.Append(about_menu, "&About")


        self.Bind(wx.EVT_MENU, self.onExit, exitMenuItem)
        self.Bind(wx.EVT_MENU, self.onSave, SaveMenuItem)
        self.Bind(wx.EVT_MENU, self.onLoad, LoadMenuItem)
        self.Bind(wx.EVT_MENU, self.onAddBlock, addBlockMenuItem)
        self.Bind(wx.EVT_MENU, self.onEditPlacement, editPlacementMenuItem)
        self.Bind(wx.EVT_MENU, self.onReplaceBlock, ReplaceBlockMenuItem)
        self.Bind(wx.EVT_MENU, self.onSetInputs, setInputsMenuItem)
        self.Bind(wx.EVT_MENU, self.on_set_arduino_tempalate, \
                  set_arduino_template_MenuItem)
        self.Bind(wx.EVT_MENU, self.on_get_arduino_template_path, \
                  get_arduino_template_MenuItem)
        self.Bind(wx.EVT_MENU, self.on_set_arduino_output_folder, \
                set_arduino_output_MenuItem)
        self.Bind(wx.EVT_MENU, self.on_arduino_codegen_menu, \
                gen_arduino_code_MenuItem)
        self.Bind(wx.EVT_MENU, self.on_menu_params, menuParamsMenuItem)
        self.Bind(wx.EVT_MENU, self.on_show_versions, versionMenuItem)
        #self.Bind(wx.EVT_MENU, self.onAddActuator, addActuatorMenuItem)

        self.SetMenuBar(menuBar)

        self.bd = pybd.block_diagram()

        self.colorful_wires = 1

        self.param_list = ['arduino_template_path','arduino_output_folder', \
                           'python_template_path','python_output_path', \
                           'csv_path','rpi_template_path','rpi_output_path']
        """List of parameters to save to the configuration file as
        'key:value' string pairs."""
        self.params_path = "gui_params_pybd.txt"
        """Path to the txt file used for saving gui parameters listed
        in pybd_gui.param_list, such as
        `pybd_gui.arduino_template_path`."""
        self.load_params()


        self.Centre()
        self.Show(True)



    def on_show_versions(self, *args, **kwargs):
        line1 = "wxbd_gui version: %s" % version
        line2 = "python_block_diagram version: %s" % pybd.version
        msg = "\n".join([line1, line2])
        wx.MessageBox(msg, "Softare Versions", wx.OK | wx.ICON_WARNING)



    def on_menu_params(self, event):
        dlg = MenuParamsDialog(self, "Menu Parameters Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should menu.")
            # need to place the new block
            #self.on_draw_btn()

        dlg.Destroy()


    def get_block_names(self):
        count = self.block_listbox.GetCount()
        mylist = []
        for row in range(count):
            item = self.block_listbox.GetString(row)
            mylist.append(item)

        return mylist


    def onSetInputs(self, event):
        print("in onSetInputs")
        ind = self.block_listbox.GetSelection()
        print("ind = %s" % ind)
        if ind == -1:
            # nothing is selected
            wx.MessageBox('You must select a block before setting its input', \
                          'Select a block first', wx.OK | wx.ICON_WARNING)
            return None


        ## get the block name
        block_name = self.block_listbox.GetString(ind)
        print("block_name = %s" % block_name)
        ## get the actual block instance
        block_instance = self.bd.get_block_by_name(block_name)
        ## check that it is not an instance of pybd.no_input_block
        if isinstance(block_instance, pybd.no_input_block):
            msg = "The selected block has no inputs"
            wx.MessageBox(msg, \
                          'Selected block has no inputs', wx.OK | wx.ICON_WARNING)
            return None

        ## we have reached readiness with a valid block
        block_list = self.get_block_names()
        print("block_list: %s" % block_list)
        dlg = SetInputsDialog(self, block_name, block_instance)

        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something.")
            self.on_draw_btn()
            # need to place the new block

        dlg.Destroy()




    def load_params(self):
        """Load parameters for the gui from the txt file specified in
        `pybd_gui.params_path`.  The parameters are saved as key:value
        strings."""
        myfile = txt_mixin.txt_file_with_list(self.params_path)
        mylist = myfile.list
        mydict = pybd.break_string_pairs_to_dict(mylist)
        print("loaded params: %s" % mydict)
        for key, value in mydict.items():
            setattr(self, key, value)

        # hard code the rpi template path for lab
        # - rpi_template_path:/home/pi/345_lab_git/robolympics/wiringpi_line_following_i2c_template.c
        #testpath = "~/345_lab_git/robolympics/wiringpi_line_following_i2c_template.c"
        #testpath = "~/345_lab_git/lab_03_OL_DC_motor/wiringpi_rpi_siso_i2c_template.c"
        #testpath = "~/345_lab_git/robolympics/wiringpi_rpi_template_F23_v1.c"

        #"lab_02_RC_step_response/rpi_plus_arduino/wiringpi_rpi_siso_RC_filter.c"

        #fullpath = os.path.expanduser(testpath)
        #if os.path.exists(fullpath):
        #    self.rpi_template_path = fullpath
        #    print("set template path to default:\n %s" % fullpath)


        if 'csv_path' in mydict:
            #load the model from csv
            print("loading: %s" % self.csv_path)
            self.load_model_from_csv(self.csv_path)
            # draw the BD
            self.on_draw_btn()




    def save_params(self):
        """Save parameters from pybd_gui.param_list to a txt values as
        key:value string pairs."""
        mydict = self.build_save_params_dict()
        my_string_list = dict_to_key_value_strings(mydict)
        txt_mixin.dump(self.params_path, my_string_list)


    def build_save_params_dict(self):
        """Build a dictionary of parameters to save to a txt file so
        that various things in the gui are preserved from session to
        session.  The parameters are listed in pybd_gui.param_list."""
        mydict = {}
        for key in self.param_list:
            if hasattr(self, key):
                value = str(getattr(self, key))
                if value:
                    mydict[key] = value
        return mydict




    def on_set_arduino_output_folder(self, event):
        msg = "Choose the output folder for Arduino code"
        start_dir = ""

        dlg = wx.DirDialog(self, msg, \
                           start_dir,
                           style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            pathout = dlg.GetPath()
            # get rid of spaces in the final folder name
            rest, folder = os.path.split(pathout)
            clean_folder = rwkos.clean_filename(folder)
            if clean_folder != folder:
                print("clean_folder = %s" % clean_folder)
                curdir = os.getcwd()
                os.chdir(rest)
                os.rmdir(folder)
                os.mkdir(clean_folder)
                pathout = os.path.join(rest, clean_folder)
            self.arduino_output_folder = pathout
        else:
            pathout = None

        dlg.Destroy()



    def on_set_arduino_tempalate(self, event):
        print("setting arduino template file")
        openFileDialog = wx.FileDialog(self, "Select the Arduino Template File (ino)", "", "", \
                                       "ino files (*.ino)|*.ino", \
                                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return None
        else:
            self.arduino_template_path = openFileDialog.GetPath()

        openFileDialog.Destroy()


    def on_get_arduino_template_path(self, event):
        if hasattr(self, "arduino_template_path"):
            msg = "Arduino Template Path:\n%s" % self.arduino_template_path
        else:
            msg = "Arduino Template Path Not Set"
        wx.MessageBox(msg, 'Info', wx.OK | wx.ICON_INFORMATION)


    def on_arduino_codegen_menu(self, event):
        ## I dunno, maybe we need to do something before calling
        ## the real codegen; or maybe call codegen without the
        ## menu call.....
        self.arduino_codegen()


    def arduino_codegen(self):
        msg1 = "Arduino Template Path not Set"
        if not hasattr(self, "arduino_template_path"):
            wx.MessageBox(msg1, 'Info', wx.OK | wx.ICON_INFORMATION)
        elif not self.arduino_template_path:
            wx.MessageBox(msg1, 'Info', wx.OK | wx.ICON_INFORMATION)

        msg2 = "Arduino output folder not set"
        if not hasattr(self, "arduino_output_folder"):
            wx.MessageBox(msg2, 'Info', wx.OK | wx.ICON_INFORMATION)
        elif not self.arduino_output_folder:
            wx.MessageBox(msg2, 'Info', wx.OK | wx.ICON_INFORMATION)

        rest, output_name = os.path.split(self.arduino_output_folder)

        self.bd.generate_arduino_code(output_name, \
                                      template_path=self.arduino_template_path, \
                                      output_folder=rest, \
                                      )


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



    def Destroy(self, *args, **kwargs):
        print("in Destroy")
        # do I put save_params here?
        # - do I ever want to exit without altering params?
        # - how do I do that?
        wx.Frame.Destroy(self)
        return 1




    def Close(self, *args, **kwargs):
        print("in Close")
        wx.Frame.Close(self, *args, **kwargs)


    def onExit(self, event):
        """"""
        print("in onExit")
        self.save_params()
        self.Close()


    def on_save_as_menu(self, *args, **kwargs):
        saveFileDialog = wx.FileDialog(self, "Save Block Diagram to CSV file", "", "",
                                   "CSV files (*.csv)|*.csv", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if saveFileDialog.ShowModal() == wx.ID_CANCEL:
            print("you canceled")
            return None

        filename = saveFileDialog.GetPath()
        print (filename)
        if filename:
            self.bd.save_model_to_csv(filename)
            self.csv_path = filename
            # also need to set the parameter


    def onSave(self, event):
        print("in SaveMenuItem")
        if hasattr(self, 'csv_path'):
            self.bd.save_model_to_csv(self.csv_path)
        else:
            self.on_save_as_menu()



    def update_block_list(self):
        block_list = self.bd.block_name_list
        self.block_listbox.Clear()
        self.block_listbox.InsertItems(block_list,0)



    def load_model_from_csv(self, csvpath):
        new_bd = pybd.load_model_from_csv(csvpath)
        self.bd = new_bd
        self.update_block_list()
        self.on_draw_btn()
        ##self.block_list_var.set(self.bd.block_name_list)
        ## actuators and sensors
        ##self.actuators_var.set(self.bd.actuator_name_list)
        ##self.sensors_var.set(self.bd.sensor_name_list)




    def onLoad(self, event):
        print("in LoadMenuItem")
        openFileDialog = wx.FileDialog(self, "Select Model to Load (CSV)", "", "", \
                                       "CSV files (*.csv)|*.csv", \
                                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return None

        filename = openFileDialog.GetPath()
        print (filename)
        if filename:
            self.load_model_from_csv(filename)
            self.csv_path = filename



    def onReplaceBlock(self, event):
        """"""
        dlg = ReplaceBlockDialog(self, "Replace Block Dialog")
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


    def onEditPlacement(self, event):
        """"""
        dlg = PlacementDialog(self, "Add Block Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("Updating drawing")
            # need to place the new block
            self.on_draw_btn()

        dlg.Destroy()


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

            xlims = self.bd.get_xlims()
            ylims = self.bd.get_ylims()


            try:
                xlims = self.bd.get_xlims()
                ylims = self.bd.get_ylims()
                #ylims[0] -= 5
                print("xlims: %s" % xlims)
                print("ylims: %s" % ylims)

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



    def onAddActuator(self, event):
        dlg = AddActuatorDialog(self, "Add Actuator Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something.")
            # need to place the new block
            self.on_draw_btn()

        dlg.Destroy()


