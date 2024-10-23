import wx

import py_block_diagram as pybd
import copy

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

max_params = 4# the maximum number of parameres a block is assumed to have

myborder = 5
border_kwargs = {'flag':wx.ALL, 'border':myborder}

class PrintBlocksDialog(wx.Dialog):
    def get_other_block_names(self):
        all_names = self.parent.get_block_names()
        other_names = [item for item in all_names if item != self.block_name]
        self.other_names = other_names
        return self.other_names



    def __init__(self, parent):
        mytitle = "Choose the Print Blocks"
        wx.Dialog.__init__(self,parent, title = mytitle, \
                #size=(350,400), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        panel = wx.Panel(self) 
        self.panel = panel
        self.parent = parent
        self.bd = self.parent.bd
        self.vbox = wx.BoxSizer(wx.VERTICAL) 

        self.main_sizer = self.vbox

        self.hsizer1 = wx.BoxSizer(wx.HORIZONTAL) 


        ## handle incoming pbdrint blocks
        self.print_blocks_list = []
        if hasattr(self.bd, 'print_blocks'):
            if len(self.bd.print_blocks) > 0:
                for block in self.bd.print_blocks:
                    name = self.bd.get_name_for_block(block)
                    self.print_blocks_list.append(name)

        all_names = self.parent.get_block_names()
        self.remaining_list = [item for item in all_names if item not in \
                               self.print_blocks_list]

        ##msizer 1
        self.msizer1 = wx.BoxSizer(wx.VERTICAL) 
        self.remaining_list_box = wx.ListBox(panel, \
                                        size = (150,150), \
                                        choices=self.remaining_list, \
                                        style = wx.LB_SINGLE)
        self.msizer1.AddMany([(wx.StaticText(self.panel, \
                                    label = "Remaining Blocks")), \
                              (self.remaining_list_box, 0, wx.EXPAND), \
                              ])
 

        self.hsizer1.Add(self.msizer1)


        self.msizer2 = wx.BoxSizer(wx.VERTICAL) 
        self.add_button = wx.Button(self.panel, label="Add -->")
        self.remove_button = wx.Button(self.panel, label="<-- Remove")
        self.msizer2.Add(self.add_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        self.msizer2.Add(self.remove_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        self.hsizer1.Add(self.msizer2)


        self.msizer3 = wx.BoxSizer(wx.VERTICAL) 
        
        self.print_blocks_list_box = wx.ListBox(panel, \
                                        size = (150,150), \
                                        choices=self.print_blocks_list, \
                                        style = wx.LB_SINGLE)
        self.msizer3.AddMany([(wx.StaticText(self.panel, \
                                    label = "Print Blocks")), \
                              (self.print_blocks_list_box, 0, wx.EXPAND), \
                              ])
 

        self.hsizer1.Add(self.msizer3)



        self.msizer4 = wx.BoxSizer(wx.VERTICAL) 
        self.up_button = wx.Button(self.panel, label="Move Up")
        self.down_button = wx.Button(self.panel, label="Move Down")
        self.msizer4.Add(self.up_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        self.msizer4.Add(self.down_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        self.hsizer1.Add(self.msizer4)


        self.vbox.Add(self.hsizer1, 1, flag = wx.ALL|wx.EXPAND, border = 15)

        


        ## Buttons
        self.go_button = wx.Button(self.panel, label="Set Print Blocks")
        self.cancel_button = wx.Button(self.panel, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        button_sizer.Add(self.go_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        self.vbox.Add(button_sizer, 1, flag = wx.ALL, border = 15)

        ## Params panels
        ##self.main_choice.Bind(wx.EVT_CHOICE, self.OnActuatorChoice)
        #self.Bind(wx.EVT_LISTBOX, self.on_block_type_choice, self.block_type_list) 
        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.remove_button.Bind(wx.EVT_BUTTON, self.on_remove_button)
        self.up_button.Bind(wx.EVT_BUTTON, self.on_up_button)
        self.down_button.Bind(wx.EVT_BUTTON, self.on_down_button)


        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)

        panel.SetSizerAndFit(self.vbox)
        #panel.SetSizer(self.vbox)
        #panel.Fit()
        panel.Layout()
        panel.Update()
        self.Fit()
        self.Layout()
        self.Update()
        


    def on_add_button(self, *args, **kwargs):
        print("on_add_button")
        ind = self.remaining_list_box.GetSelection()
        name = self.remaining_list_box.GetString(ind)
        self.remaining_list_box.Delete(ind)
        self.print_blocks_list_box.Append(name)
        


    def on_remove_button(self, *args, **kwargs):
        print("on_remove_button")
        ind = self.print_blocks_list_box.GetSelection()
        name = self.print_blocks_list_box.GetString(ind)
        self.print_blocks_list_box.Delete(ind)
        self.remaining_list_box.Append(name)


    

    def on_up_button(self, *args, **kwargs):
        print("on_up_button")
        ind = self.print_blocks_list_box.GetSelection()
        if ind > 0:
            name = self.print_blocks_list_box.GetString(ind)
            self.print_blocks_list_box.Delete(ind)
            self.print_blocks_list_box.Insert(name, ind-1)
            self.print_blocks_list_box.SetSelection(ind-1)


    

    def on_down_button(self, *args, **kwargs):
        print("on_down_button")
        ind = self.print_blocks_list_box.GetSelection()
        N = self.print_blocks_list_box.GetCount()
        print("ind: %s" % ind)
        print("N: %s" % N)
        if (ind >= 0) and (ind < (N-1)):
            name = self.print_blocks_list_box.GetString(ind)
            self.print_blocks_list_box.Delete(ind)
            self.print_blocks_list_box.Insert(name, ind+1)
            self.print_blocks_list_box.SetSelection(ind+1)



    def on_cancel_button(self, event):
        self.EndModal(0)


    def on_go_button(self, event):
        print("go!")
        pb_list = self.print_blocks_list_box.GetStrings()
        print("pb_list:")
        print(pb_list)
        self.bd.set_print_blocks_from_names(pb_list)
        self.EndModal(1)

