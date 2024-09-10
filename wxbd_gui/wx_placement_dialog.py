import wx

import py_block_diagram as pybd
import copy

myborder = 5
left_or_right = wx.LEFT|wx.RIGHT
not_bottom = left_or_right|wx.TOP
not_top = left_or_right|wx.BOTTOM 


## The Plan:
##
## - add list of block types when category is chosen
## - when a block type is chosen:
##     - delete params widgets if needed
##     - delete old params panel and params sizer if needed
##     - handle plant choice
##          - are actuators and sensors defined?
##     - build params panel
##     - make list of params widgets
##     - determine whether or not to display actuators and/or sensors

#class params_mini_panel(wx.Panel):
#    def __init__(self, parent, param_label):
#        wx.Panel.__init__(self, parent)
#        self.param_label = param_label
#        self.vbox = wx.BoxSizer(wx.VERTICAL) 
#        # - create label and textctrl
#        # - create vertical sizer
#        # - add tabel and textctrl to sizer with padding
#        self.label = wx.StaticText(self, label=param_label)
#        self.text = wx.TextCtrl(self, size=(100,10))
#        self.vbox.Add(self.label, wx.TOP|wx.LEFT|wx.RIGHT)
#        self.vbox.Add(self.text, wx.BOTTOM|wx.LEFT|wx.RIGHT)#|wx.EXPAND)
#        self.SetSizer(self.vbox)
#
#
#    def SetLabel(self, label):
#        self.label.SetLabel(label)
#
#
#    def SetValue(self, value):
#        self.text.SetValue(str(value))
#
#
#    def GetValue(self):
#        return self.text.GetValue()
#
#
#    def SetValue(self, value):
#        mystr = str(value)
#        self.text.SetValue(mystr)
#
#
#    def remove_widgets(self):
#        N = len(self.vbox.GetChildren())
#        print("N = %i" % N)
#        for i in range(N):
#            self.vbox.Remove(0)
#        
#        self.Layout()
#        self.Update()
#
#
#
#    def del_widgets(self):
#        del self.text
#        del self.label
#        self.Layout()
#        self.Update()
#
#
class RelativePanel(wx.Panel):
    def get_other_block_names(self):
        all_names = self.parent.bd.block_name_list
        self.block_name = self.parent.get_selected_block_name()
        other_names = [item for item in all_names if item != self.block_name]
        self.other_names = other_names
        return self.other_names



    def set_relative_choices(self):
        self.get_other_block_names()
        self.relative_block.Clear()
        self.relative_block.Insert(self.other_names, 0)


    def get_rel_block_name(self):
        ind =  self.relative_block.GetSelection()
        relname = self.relative_block.GetString(ind)
        return relname


    def get_rel_dir(self):
        ind = self.relative_dir.GetSelection()
        reldir = self.relative_dir.GetString(ind)
        return reldir



    def set_relative_block_by_name(self, relblockname):
        ind = self.relative_block.FindString(relblockname)
        self.relative_block.SetSelection(ind)



    def set_relative_dir(self, dirstring):
        ind = self.relative_dir.FindString(dirstring)
        self.relative_dir.SetSelection(ind)


    def set_rel_dist(self, dist):
        self.dist_box.SetValue(str(dist))


    def set_xshift(self, shift):
        self.xshift_box.SetValue(str(shift))


    def set_yshift(self, shift):
        self.yshift_box.SetValue(str(shift))



    def get_float_from_box(self, attr):
        widget = getattr(self, attr)
        mystr = widget.GetValue()
        myfloat = float(mystr)
        return myfloat


    def on_btn(self, *args, **kwargs):
        block_instance = self.parent.get_block_instance()
        rel_block_name = self.get_rel_block_name()
        rel_block = self.parent.bd.get_block_by_name(rel_block_name)
        rel_pos = self.get_rel_dir().lower()
        rel_dist = self.get_float_from_box("dist_box")
        xshift = self.get_float_from_box("xshift_box")
        yshift = self.get_float_from_box("yshift_box")

        block_instance.place_relative(rel_block=rel_block, rel_pos=rel_pos, rel_distance=rel_dist, \
                                      xshift=xshift, yshift=yshift)
        self.parent.EndModal(1)
        

    #----------------------------------------------------------------------
    def make_widgets(self):
        self.relative_block = wx.Choice(self, \
                                choices=[], \
                                size=(100,-1))
        self.set_relative_choices()

        rel_label = wx.StaticText(self, label = "Relative Block")


        dir_label = wx.StaticText(self, label = "Relative Direction")

        self.relative_dir = wx.Choice(self, \
                                choices=['Right','Left','Above','Below'], \
                                size=(100,-1))
        self.relative_dir.SetSelection(0)

        dist_label = wx.StaticText(self, label = "Relative Distance")
        self.dist_box = wx.TextCtrl(self, size=(100,-1))
        self.dist_box.SetValue("4")

        xshift_label = wx.StaticText(self, label = "x shift")
        self.xshift_box = wx.TextCtrl(self, size=(100,-1))
        self.xshift_box.SetValue("0")
 
        yshift_label = wx.StaticText(self, label = "y shift")
        self.yshift_box = wx.TextCtrl(self, size=(100,-1))
        self.yshift_box.SetValue("0")

        
        self.btn = wx.Button(self, label="Place Relative")
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(rel_label, 0, not_bottom, 10) 
        sizer.Add(self.relative_block, 0, not_top, 10)
        def add_pair(topitem, bottomitem):
            sizer.Add(topitem, 0, not_bottom, 10) 
            sizer.Add(bottomitem, 0, not_top, 10)
        
        add_pair(dir_label, self.relative_dir)
        add_pair(dist_label, self.dist_box)
        add_pair(xshift_label, self.xshift_box)
        add_pair(yshift_label, self.yshift_box)



        self.btn.Bind(wx.EVT_BUTTON, self.on_btn)


        sizer.Add(self.btn, 0, wx.ALL, 10)
        self.SetSizer(sizer)



    def __init__(self, parent, real_parent):
        """"""
        wx.Panel.__init__(self, parent=parent)
        # this is slightly tricky in that the parent is a panel, 
        # not my class
        self.parent = real_parent  
        self.make_widgets()
        self.SetBackgroundColour(wx.Colour(240, 251, 252))


        
class AbsPanel(RelativePanel):
    def make_widgets(self):
        btn = wx.Button(self, label="Place Absolute")
        sizer = wx.BoxSizer(wx.VERTICAL)

        def add_pair(topitem, bottomitem):
            sizer.Add(topitem, 0, not_bottom, 10) 
            sizer.Add(bottomitem, 0, not_top, 10)

        x_label = wx.StaticText(self, label = "abs x") 
        self.abs_x_box = wx.TextCtrl(self, size=(50,-1))
        add_pair(x_label, self.abs_x_box)
        y_label = wx.StaticText(self, label = "abs y") 
        self.abs_y_box = wx.TextCtrl(self, size=(50,-1))
        add_pair(y_label, self.abs_y_box) 

        self.abs_x_box.SetValue("0")
        self.abs_y_box.SetValue("0")

        self.btn = btn
        self.btn.Bind(wx.EVT_BUTTON, self.on_btn)
 
        sizer.Add(btn, 0, wx.ALL, 10)
        self.SetSizer(sizer)



    def on_btn(self, *args, **kwargs):
        block_instance = self.parent.get_block_instance()
        x = self.get_abs_x()
        y = self.get_abs_y()
        block_instance.place_absolute(x,y)
        self.parent.EndModal(1)


    def set_abs_x(self, val):
        self.abs_x_box.SetValue(str(val))


    def set_abs_y(self, val):
        self.abs_y_box.SetValue(str(val))


    def get_abs_x(self):
        return float(self.abs_x_box.GetValue())


    def get_abs_y(self):
        return float(self.abs_y_box.GetValue())



    def __init__(self, parent, real_parent):
        """"""
        RelativePanel.__init__(self, parent, real_parent) 
        self.SetBackgroundColour(wx.Colour(243, 252, 240))

        
        


class PlacementDialog(wx.Dialog): 
    def get_selected_block_name(self):
        ind = self.block_choice.GetSelection()
        block_name = self.block_choice.GetString(ind)
        return block_name


    def make_widgets(self):
        # main ideas:
        # - block choice at the top with label
        #     - which block are we placing/editing the placement of?
        # - notebook with tabs for relative and absolute placement
        #     - each their own class
        self.panel = wx.Panel(self) 
        self.fgsizer = wx.FlexGridSizer(3, 1, 5, 5)
        self.wrapper = wx.BoxSizer(wx.VERTICAL)
 

        block_label = wx.StaticText(self.panel, label = "Block to Place")
        self.block_choice = wx.Choice(self.panel, \
                choices=self.bd.block_name_list, \
                size=(100,-1))

        notebook = wx.Notebook(self.panel)
        relpanel = RelativePanel(notebook, self)
        notebook.AddPage(relpanel, "Relative")
        
        abspanel = AbsPanel(notebook, self)
        notebook.AddPage(abspanel, "Absolute")
        self.notebook = notebook

        self.abspanel = abspanel
        self.relpanel = relpanel

        self.fgsizer.AddMany([ (block_label, 0, wx.LEFT|wx.RIGHT|wx.TOP), \
                               (self.block_choice, 0, \
                                wx.LEFT|wx.RIGHT|wx.TOP),
                               (notebook, 0, \
                                wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND),
                               ])
    
        self.fgsizer.AddGrowableCol(0, 1)
        self.fgsizer.AddGrowableRow(2, 1)

        self.main_sizer = self.fgsizer 
        self.wrapper.Add(self.fgsizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
        ## Bind block_choice
        ## - load current placement stuff from the block instance
        self.block_choice.Bind(wx.EVT_CHOICE, self.on_block_selected)
        ## Buttons
        #self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        #self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        #self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)

        #self.Bind(wx.EVT_CLOSE, self.on_cancel_button)
        self.panel.SetSizer(self.wrapper)



    def get_block_instance(self):
        block_name = self.get_selected_block_name()
        block_instance = self.bd.get_block_by_name(block_name)
        return block_instance



    def load_placement_params_from_block(self):
        block_instance = self.get_block_instance()
        # is it placed?
        # - abs or rel?
        # - other parameters
        if block_instance.isplaced():
            # for now, not doing anything if it isn't placed
            # - maybe try to guess reasonable defaults in the future
            # - but the software doesn't really allow the creation of an
            #   unplaced block anymore
            if block_instance.placement_type == 'absolute':
                self.notebook.SetSelection(1)#self.abspanel)
                self.abspanel.set_abs_x(block_instance.x)
                self.abspanel.set_abs_y(block_instance.y)



            elif block_instance.placement_type == 'relative':
                self.notebook.SetSelection(0)#self.relpanel)
                self.relpanel.set_relative_block_by_name(block_instance.rel_block_name)
                self.relpanel.set_relative_dir(block_instance.rel_pos)
                self.relpanel.set_rel_dist(block_instance.rel_distance)
                self.relpanel.set_xshift(block_instance.xshift)
                self.relpanel.set_yshift(block_instance.yshift)
                #self.rel_block = rel_block
                #self.rel_pos = rel_pos
                #self.rel_distance = rel_distance
                #self.xshift = xshift
                #self.yshift = yshift
        


    def on_block_selected(self, *args, **kwargs):
        print("in on_block_selected")
        self.relpanel.set_relative_choices()
        self.load_placement_params_from_block()


    def __init__(self, parent, title): 
        wx.Dialog.__init__(self, parent, title = title, \
                size=(300,550), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        self.parent = parent
        self.bd = self.parent.bd
        self.make_widgets()
        self.block_choice.SetSelection(0)
        self.load_placement_params_from_block()


    
    def on_cancel_button(self, event):
        self.EndModal(0)


    def on_go_button(self, event):
        self.EndModal(1)


