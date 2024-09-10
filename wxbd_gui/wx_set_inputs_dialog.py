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

class SetInputsDialog(wx.Dialog):
    def _get_choice_list(self):
        return pybd.actuator_list


    def get_other_block_names(self):
        all_names = self.parent.get_block_names()
        other_names = [item for item in all_names if item != self.block_name]
        self.other_names = other_names
        return self.other_names



    def __init__(self, parent, block_name, block_instance):
        mytitle = "Choose the Input(s) for %s" % block_name
        wx.Dialog.__init__(self,parent, title = mytitle, \
                #size=(350,400), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        self.block_name = block_name
        self.block_instance = block_instance
        panel = wx.Panel(self) 
        self.panel = panel
        self.parent = parent
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.get_other_block_names()
        self.input_choices_1 = wx.Choice(panel, choices=self.other_names)
        self.input_choices_2 = wx.Choice(panel, choices=self.other_names)
        self.label1 = wx.StaticText(panel, label = "Input 1")
        self.label2 = wx.StaticText(panel, label = "Input 2")
        self.vbox.AddMany([ (self.label1, 0, wx.ALL, myborder), \
                            (self.input_choices_1, 0, wx.ALL|wx.EXPAND, myborder), \
                            (self.label2, 0, wx.ALL, myborder), \
                            (self.input_choices_2, 0, wx.ALL|wx.EXPAND, myborder), \
                          ])

        self.main_sizer = self.vbox
        ## Buttons
        self.go_button = wx.Button(self.panel, label="Set Input(s)")
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
        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)

        # set default actuator choice
        my_choice = self.other_names[0]
        #self.choice_selected(my_choice)

        ## check for number of inputs
        if self.block_instance.num_inputs == 1:
            self.hide_input_2_stuff()
        panel.SetSizer(self.vbox)
        


    def hide_input_2_stuff(self):
        self.input_choices_2.Hide()
        self.label2.Hide()
        self.panel.Layout()
        self.panel.Update()



    def on_cancel_button(self, event):
        self.EndModal(0)


    def get_block_name_fromn_widget(self, widget):
        ind = widget.GetSelection()
        name = widget.GetString(ind)
        return name


    def get_block_instance_from_widget(self, widget):
        myname = self.get_block_name_fromn_widget(widget)
        myinstance = self.parent.bd.get_block_by_name(myname)
        return myinstance


    def on_go_button(self, event):
        in1_instance = self.get_block_instance_from_widget(self.input_choices_1)
        self.block_instance.set_input_block1(in1_instance)
        if self.block_instance.num_inputs > 1: 
            in2_instance = self.get_block_instance_from_widget(self.input_choices_2)
            self.block_instance.set_input_block2(in2_instance)

        ## need to handle input2 or higher here if needed
        self.EndModal(1)


    def get_my_choice(self):
        act_ind = self.main_choice.GetSelection()
        my_choice = self.choice_list[act_ind]
        return act_ind, my_choice

