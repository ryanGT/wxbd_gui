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
        self.N = self.block_instance.num_inputs
        panel = wx.Panel(self) 
        self.panel = panel
        self.parent = parent
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.get_other_block_names()

        self.input_vars = []
        for i in range(self.N):
            curchoice = wx.Choice(panel, choices=self.other_names)
            label_text = self.block_instance.gui_input_labels[i]
            curlabel = wx.StaticText(panel, label=label_text)
            j = i+1
            attr_name = "input_choices_%i" % j
            self.input_vars.append(attr_name)
            setattr(self, attr_name, curchoice)
            self.vbox.AddMany([ (curlabel, 0, wx.ALL, myborder), \
                                (curchoice, 0, wx.ALL|wx.EXPAND, myborder), \
                                ])



        #self.input_choices_1 = wx.Choice(panel, choices=self.other_names)
        #self.input_choices_2 = wx.Choice(panel, choices=self.other_names)
        #self.label1 = wx.StaticText(panel, label = "Input 1")
        #self.label2 = wx.StaticText(panel, label = "Input 2")
        #self.vbox.AddMany([ (self.label1, 0, wx.ALL, myborder), \
        #                    (self.input_choices_1, 0, wx.ALL|wx.EXPAND, myborder), \
        #                    (self.label2, 0, wx.ALL, myborder), \
        #                    (self.input_choices_2, 0, wx.ALL|wx.EXPAND, myborder), \
        #                  ])

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


        # set the wx.Choice selections for inputs that 
        # are already specified
        self.check_existing_inputs()

        ## check for number of inputs
        #if self.block_instance.num_inputs == 1:
        #    self.hide_input_2_stuff()
        panel.SetSizer(self.vbox)
        


    def check_existing_inputs(self):
        # if the block instance already has some inputs set,
        # reflect that in the wx.Choice instances
        # - use GetString and SetSelection
        for i in range(self.N):
            func_name = self.block_instance.get_input_func_names[i]
            myfunc = getattr(self.block_instance, func_name)
            curname = myfunc()
            if curname:
                cur_var = self.input_vars[i]
                widget = getattr(self, cur_var)
                self.set_widget_by_name(widget, curname)


    def set_widget_by_name(self, widget, curname):
        ind = widget.FindString(curname)
        widget.SetSelection(ind)


#    def hide_input_2_stuff(self):
#        self.input_choices_2.Hide()
#        self.label2.Hide()
#        self.panel.Layout()
#        self.panel.Update()



    def on_cancel_button(self, event):
        self.EndModal(0)


    def get_block_name_from_widget(self, widget):
        ind = widget.GetSelection()
        print("ind: %s" % ind)
        try:
            name = widget.GetString(ind)
            return name
        except:
            print("bad index")
            print("ind: %s" % ind)
            return ""


    def get_block_instance_from_widget(self, widget):
        myname = self.get_block_name_from_widget(widget)
        myinstance = self.parent.bd.get_block_by_name(myname)
        return myinstance


    def on_go_button(self, event):
        # tk version retrieve set input function names from 
        # the block
        # for example, the functions to set the inputs for an if block are:
        # set_input_func_names=['set_bool_input', \
        #                       'set_input_block1', \
        #                       'set_input_block2'], \
        ## Old, hard coded version for wx 1.0:
        ##in1_instance = self.get_block_instance_from_widget(self.input_choices_1)
        ##self.block_instance.set_input_block1(in1_instance)
        ##if self.block_instance.num_inputs > 1: 
        ##    in2_instance = self.get_block_instance_from_widget(self.input_choices_2)
        ##    self.block_instance.set_input_block2(in2_instance)

        ## from tk version:
        for i in range(self.N):
            cur_var = self.input_vars[i]
            widget = getattr(self, cur_var)
            input_name = self.get_block_name_from_widget(widget)       
            print("input_name: %s" % input_name)
            if input_name.strip():# not just blank or spaces
                if input_name in self.parent.bd.block_dict:
                    input_block = self.parent.bd.get_block_by_name(input_name)
                elif input_name in self.parent.bd.sensors_dict:
                    input_block = self.parent.bd.get_sensor_by_name(input_name)
                func_name = self.block_instance.set_input_func_names[i]
                myfunc = getattr(self.block_instance, func_name)
                myfunc(input_block)
    
        ## need to handle input2 or higher here if needed
        self.EndModal(1)


    def get_my_choice(self):
        act_ind = self.main_choice.GetSelection()
        my_choice = self.choice_list[act_ind]
        return act_ind, my_choice

