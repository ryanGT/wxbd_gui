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

from wxbd_gui.wxbd_utils import params_mini_panel

myborder = 5
border_kwargs = {'flag':wx.ALL, 'border':myborder}

class AddActuatorDialog(wx.Dialog): 
    def create_params_panels(self):
        self.params_panels = []

        for i in range(max_params):
            j = i + 1
            param_str = "Param %i" % j
            curpanel = params_mini_panel(self.panel, param_str) 
            self.params_panels.append(curpanel)
            self.params_sizer.Add(curpanel, **border_kwargs)#, style=wx.ALL, border=15)

    
    def create_params_sizer_and_panel(self):
        print("in new create_params_sizer_and_panel")
        self.params_panel = wx.Panel(self.panel) 
        self.params_sizer = wx.BoxSizer(wx.VERTICAL)


    def _get_choice_list(self):
        return pybd.actuator_list


    def __init__(self, parent, title): 
        wx.Dialog.__init__(self,parent, title = title, \
                size=(350,500), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        panel = wx.Panel(self) 
        self.panel = panel

        self.parent = parent
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        self.choice_list = self._get_choice_list() 
        self.main_choice = wx.Choice(panel, \
                                          choices=self.choice_list)

        self.name_box = wx.TextCtrl(panel)
        self.label1 = wx.StaticText(panel, label = "Actuator Type")
        self.label2 = wx.StaticText(panel, label = "Actuator Name")
        self.vbox.AddMany([ (self.label1, 0, wx.ALL, myborder), \
                            (self.main_choice, 0, wx.ALL, myborder), \
                            (self.label2, 0, wx.ALL, myborder), \
                            (self.name_box, 0, wx.ALL|wx.EXPAND, myborder), \
                          ])

        print("before new call")
        self.create_params_sizer_and_panel()
        self.create_params_panels()
        self.vbox.Add(self.params_sizer, flag=wx.ALL, border=5)

        self.main_sizer = self.vbox
        ## Buttons
        self.go_button = wx.Button(self.panel, label="Add Actuator")
        self.cancel_button = wx.Button(self.panel, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        button_sizer.Add(self.go_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        self.vbox.Add(button_sizer, 1, flag = wx.ALL, border = 15)

        ## Params panels
        self.main_choice.Bind(wx.EVT_CHOICE, self.OnActuatorChoice)
        #self.Bind(wx.EVT_LISTBOX, self.on_block_type_choice, self.block_type_list) 
        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)

        self.params_dict = self.get_params_dict()

        # set default actuator choice
        my_choice = self.choice_list[0]
        self.choice_selected(my_choice)

        panel.SetSizer(self.vbox)
        


    def get_params_list(self, chosen_type):
        params_list = self.params_dict[chosen_type]
        return params_list


    def get_suggested_name(self):
        raise NotImplementedError()

    def get_params_dict(self):
        return pybd.actuator_params_dict


    def get_default_params(self, chosen_type):
        dp = pybd.actuator_default_params[chosen_type]
        return dp


    def suggest_name(self, chosen_type):
        return self.parent.bd.suggest_actuator_name(chosen_type)


    def choice_selected(self, chosen_type):
        params = self.get_params_list(chosen_type)
        print("params: %s" % params)

        self.set_params_labels(params)
        m = len(params)
        print("m = %s" % m)
        self.hide_panels(m)
        self.show_panels(m)
        self.set_params_labels(params)
        default_params = self.get_default_params(chosen_type)
        self.assign_default_values(params, default_params)
        self.params = params
        self.default_params = default_params

        # suggest actuator name
        suggest_name = self.suggest_name(chosen_type)
        self.name_box.SetValue(suggest_name)
        
        # save things for other methods
        self.chosen_type = chosen_type
        #self.param_list = param_list
        self.panel.Layout()
        self.panel.Update()



    def on_cancel_button(self, event):
        self.EndModal(0)



    def set_instance(self, myinstance):
        self.actuator_instance = myinstance


    def on_go_button(self, event):
        ind, my_choice = self.get_my_choice()
        print("my_choice = %s" % my_choice)
        mydict = self.read_params_from_boxes()
        print("mydict = %s" % mydict)
        act_name = self.name_box.GetValue()
        # steps:
        # - get chosen class
        # - get parameters
        # - convert parameters to float or int if needed
        # - create actuator or sensor
        # - append actuator or sensor to parent's block_diagram
        #chosen_type = self.main_chooser_var.get()
        #print("chosen_type: %s" % chosen_type)

        myclass = getattr(pybd, my_choice)
        #variable_name = self.variable_name_var.get()
        #print("variable_name: %s" % variable_name)

        kwargs = self.read_params_from_boxes()
        print("kwargs = %s" % kwargs)

        myinstance = myclass(**kwargs)
        self.set_instance(myinstance)
        #self.append_instance_to_bd(myinstance)
        #self.update_parent_gui()
        #self.destroy()



        ##----
        self.EndModal(1)



    def handle_plant_choice(self):
        # - are sensors and actuators defined?
        # - what messages do I show?
        # - do I exit/return None?
        # - add sensors and actuators to params sizer
        pass


    def delete_params_panels(self):
        if hasattr(self, 'params_panels'):
            for item in self.params_panels:
                item.remove_widgets()
                item.del_widgets()
                del item
            del self.params_panels
            self.panel.Layout()
            self.panel.Update()




    def delete_params_sizer_and_panel(self):
        if hasattr(self, 'params_sizer'):
            self.main_sizer.Remove(self.params_sizer)
            del self.params_sizer
        if hasattr(self, 'params_panel'):
            del self.params_panel

        self.panel.Layout()
        self.panel.Update()


    def get_my_choice(self):
        act_ind = self.main_choice.GetSelection()
        my_choice = self.choice_list[act_ind]
        return act_ind, my_choice


    def OnActuatorChoice(self,event): 
        ind, my_choice = self.get_my_choice()
        print("my_choice: %s" % my_choice)
        self.choice_selected(my_choice)



    def hide_panels(self, m):
        q = max_params - m
        for i in range(q):
            h = m+i
            print("h = %i" % h)
            curpanel = self.params_panels[h]
            curpanel.Hide()
            curpanel.Layout()
            curpanel.Update()



    def show_panels(self, m):
        for i in range(m):
            print("showing i = %i" %i)
            curpanel = self.params_panels[i]
            curpanel.Show()
            curpanel.Layout()
            curpanel.Update()



    def set_params_labels(self, params_list):
        for i, p in enumerate(params_list):
            curpanel = self.params_panels[i]
            curpanel.SetLabel(p)


    def assign_default_values(self, params_list, default_params):
        for i, p in enumerate(params_list):
            curpanel = self.params_panels[i]
            if p in default_params:
                dval = default_params[p]
                curpanel.SetValue(dval)



    def read_params_from_boxes(self):
        mydict = {}

        for i, p in enumerate(self.params):
            curpanel = self.params_panels[i]
            curstr = curpanel.GetValue()
            try:
                myvalue = float(curstr)
            except:
                myvalue = curstr
            mydict[p] = myvalue
        return mydict

    # from old version:
    #def create_params_panels(self, params):
    #    # - doing this as two columns seems tricky
    #    # - I need to add two labels and then two widgets in 
    #    #   alternating rows
    #    # - is this worth the pain?
    #    # - do I divide them ahead of time into column groups?
    #    # - do I create multiple panels somehow?
    #    # - does each label/widget pair go on a panel?
    #    self.params_widget_dict = {}
    #    self.params_panels = []
    #
    #    for param in params:
    #        curpanel = params_mini_panel(self.panel, param) 
    #        self.params_panels.append(curpanel)
    #        self.params_widget_dict[param] = curpanel
    #        self.params_sizer.Add(curpanel)


    def populate_default_params(self, default_params):
        # - How does this work?
        # - how do you know where to put the values?
        #     - a dictionary of param names and corresponding widgets?
        pass





class AddSensorDialog(AddActuatorDialog): 
    def get_default_params(self, chosen_type):
        dp = pybd.sensor_default_params[chosen_type]
        return dp


    def suggest_name(self, chosen_type):
        return self.parent.bd.suggest_sensor_name(chosen_type)


    def _get_choice_list(self):
        return pybd.sensor_list



    def set_instance(self, myinstance):
        self.sensor_instance = myinstance


    def __init__(self, *args, **kwargs):
        AddActuatorDialog.__init__(self, *args, **kwargs)
        self.label1.SetLabel("Sensor Type")
        self.label2.SetLabel("Sensor Name")

        self.params_dict = pybd.sensor_params_dict

        # set default actuator choice
        my_choice = pybd.sensor_list[0]
        self.main_choice.SetItems(pybd.sensor_list) 
        self.choice_selected(my_choice)
        self.go_button.SetLabel("Add Sensor")
        self.panel.SetSizer(self.vbox)
        

    def get_params_dict(self):
        return pybd.sensor_params_dict


