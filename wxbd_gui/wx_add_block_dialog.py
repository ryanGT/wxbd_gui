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

max_params = 6# the maximum number of parameres a block is assumed to have

from wxbd_gui.wxbd_utils import params_mini_panel

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


class AddBlockDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(AddBlockDialog, self).__init__(parent, title = title, \
                size=(700,500), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        panel = wx.Panel(self) 
        self.panel = panel

        self.parent = parent

        sizer = wx.FlexGridSizer(10, 2, 5, 5)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        self.categories_choice = wx.Choice(panel,choices=pybd.block_categories)
        self.block_type_list = wx.ListBox(panel, size = (100,-1), \
                               choices=[], style = wx.LB_SINGLE)
       
        self.block_name_box = wx.TextCtrl(panel)

        sizer.AddMany([ (wx.StaticText(panel, label = "Block Category")),
                        (wx.StaticText(panel, label = "Block Name")),
                        (self.categories_choice, 0, wx.EXPAND),
                        (self.block_name_box, 0, wx.EXPAND),
                        (wx.StaticText(panel, label = "Block Types")),
                        (wx.StaticText(panel, label = "(empty)")),
                        (self.block_type_list, 0, wx.EXPAND),
                        (wx.StaticText(panel, label = "(empty)")),
                       ])
    
        sizer.AddGrowableCol(0, 1)
        self.main_sizer = sizer 
        wrapper.Add(sizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
        ## Buttons
        self.go_button = wx.Button(self.panel, label="Add Block")
        self.cancel_button = wx.Button(self.panel, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        button_sizer.Add(self.go_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        wrapper.Add(button_sizer, 1, flag = wx.ALL, border = 15)

        ## Params panels
        self.create_params_sizer_and_panel()
        self.create_params_panels()
        self.main_sizer.Add(self.params_sizer, wx.EXPAND)

        self.categories_choice.Bind(wx.EVT_CHOICE, self.OnCategoryChoice)
          
        input_names = ['input_block_name', \
                       'input2_block_name', \
                       'input3_block_name']
        for name in input_names:
            setattr(self, name, None)

        cat_ind = self.categories_choice.GetSelection()
        print("cat_ind: %s" % cat_ind)
        self.category_selected()
        self.Bind(wx.EVT_LISTBOX, self.on_block_type_choice, self.block_type_list) 
        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)
        panel.SetSizer(wrapper)
        

    def _create_new_block(self, block_type, block_name, params):
        # - How did this work with mytk version?
        # - How do I want it to work now?
        kwargs = {}

        # ultimately, input_block_names need to be converted to actual block instances
        # - look up the block in parent.bd
        #
        # Approach:
        # - input_block_name, input2_block_name, and input3_block_name are attributes of this
        #   dialog box that the user may have optionally set
        # - input_block1 through input_block3 are attributes recognized by pybd
        # - I need to map from one to the other
        input_pairs = [('input_block_name','input_block1'), \
                       ('input2_block_name','input_block2'), \
                       ('input3_block_name','input_block3'), \
                       ]


        # This code seems to assume that input_block1_name, input2_block_name,
        # and input3_block_name are attributes of the AddBlockDialog that are
        # either set or set to None
        for attr, key in input_pairs:
            input_block_name = getattr(self, attr)
            if input_block_name is not None:
                input_block = self.parent.get_block_by_name(input_block_name)
                kwargs[key] = input_block
                key2 = key + '_name'
                kwargs[key2] = input_block_name 
        
        block_class = getattr(pybd, block_type)
        # how do I handle cases with input(s) set?

        # get actuator and sensor if it is a plant
        print("plant classes: %s" % pybd.plant_class_names)
        if block_type in pybd.plant_class_names:
            # we need to handle plant classes with no actuator and those with two sensors
            print("this is a plant")

            # possible cases:
            # - actuator or no actuator
            # - one sensor or two
            #     - must have at least one sensor to be a plant
            if block_type not in pybd.plants_with_no_actuators_names:
                # it has an actuator
                actuator_name = self.actuators_var.get()
                print("actuator_name: %s" % actuator_name)
                myactuator = self.bd.get_actuator_by_name(actuator_name)
                kwargs['actuator'] = myactuator

            if block_type in pybd.plants_with_two_sensors_names:
                # it has two sensors
                sensor1_name = self.sensors_var.get()
                print("sensor1_name: %s" % sensor1_name)
                sensor2_name = self.sensor2_var.get()
                print("sensor2_name: %s" % sensor2_name)
                sensor1 = self.bd.get_sensor_by_name(sensor1_name)                
                kwargs['sensor1'] = sensor1
                sensor2 = self.bd.get_sensor_by_name(sensor2_name)                
                kwargs['sensor2'] = sensor2                
            else:
                # it has only one sensor
                sensor_name = self.sensors_var.get()
                print("sensor_name: %s" % sensor_name)
                mysensor = self.bd.get_sensor_by_name(sensor_name)
                kwargs['sensor'] = mysensor



        # get additional kwargs from param boxes here:
        #other_kwargs = self.get_params_kwargs(self.N_params)
        ## print("other_kwargs:")
        ## print(other_kwargs)
        kwargs.update(params) 
        print("creating block in go_pressed")
        print("kwargs:")
        print(kwargs)
        new_block = pybd.create_block(block_class, block_type, block_name, **kwargs)
        return new_block

    
    def on_cancel_button(self, event):
        self.EndModal(0)



    def on_go_button(self, event):
        ind = self.block_type_list.GetSelection()
        block_type = self.block_type_list.GetString(ind)
        mydict = self.read_params_from_boxes()
        print("mydict = %s" % mydict)
        block_name = self.block_name_box.GetValue()
        new_block = self._create_new_block(block_type, block_name, mydict)
        self.parent.append_block_to_dict(block_name, new_block)
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



    def create_params_sizer_and_panel(self):
        self.params_panel = wx.Panel(self.panel) 
        self.params_sizer = wx.GridSizer(cols=2,vgap=5, hgap=5)


    def create_params_panels(self):
        self.params_panels = []

        for i in range(max_params):
            j = i + 1
            param_str = "Param %i" % j
            curpanel = params_mini_panel(self.panel, param_str) 
            self.params_panels.append(curpanel)
            self.params_sizer.Add(curpanel)#, style=wx.ALL, border=15)


        

    def category_selected(self):
        # Does all this stuff really go in the method for when a box is
        # selected?
        # - but how would you handle putting the actuators and sensors in the
        # params panel?
        # - do the actuators and sensors do in their own panel?
       
        cat_ind = self.categories_choice.GetSelection()
        chosen_cat = pybd.block_categories[cat_ind]
        if chosen_cat == 'plant':
            self.handle_plant_choice()
        new_list = pybd.block_category_dict[chosen_cat]
        print("new_list: %s" % new_list)
        self.block_type_list.Clear()
        self.block_type_list.InsertItems(new_list,0)	

    
    def OnCategoryChoice(self,event): 
        cat_choice = self.categories_choice.GetSelection()
        print("cat_choice: %s" % cat_choice)
        self.category_selected()



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
            print("i = %i" %i)
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


    def on_block_type_choice(self, event):
        print("block type selected")
        # this is where the params panel needs to be deleted and recreated
        #
        # - how to handle plants that have no actuators or something like that?
        #self.delete_params_panels()
        #self.delete_params_sizer_and_panel()
        #self.create_params_sizer_and_panel()
        ind = self.block_type_list.GetSelection()
        block_type = self.block_type_list.GetString(ind)
        params, default_params = self.get_params_for_block_type(block_type)
        suggested_name = self.parent.bd.suggest_block_name(block_type)
        self.block_name_box.SetValue(suggested_name)

        print("params: ")
        print(params)
        print('\n')
        print('default_params:')
        print(default_params)
        m = len(params)
        self.hide_panels(m)
        self.show_panels(m)
        self.set_params_labels(params)
        self.assign_default_values(params, default_params)
        self.params = params
        self.default_params = default_params
        #self.create_params_panels(params)
        #self.main_sizer.Add(self.params_sizer, wx.EXPAND)
        self.panel.Layout()
        self.panel.Update()


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




    def get_params_for_block_type(self, block_type):
        myclass = pybd.block_classes_dict[block_type]
        temp_block = myclass()
        py_params = temp_block.py_params
        default_params = {}
        if hasattr(temp_block, "default_params"):
            for key in py_params:
                if key in temp_block.default_params:
                    value = temp_block.default_params[key]
                else:
                    value = ''
                default_params[key] = value
        else:
            empty_list = ['']*len(py_params)
            default_params = dict(zip(py_params, empty_list))
            
        print("block py_params:")
        for key, value in default_params.items():
            print("%s : %s" % (key, value))

        ## - pop sensors and actuators from py_params before setting N_params
        ## - set defaults

        ## actuators and sensors are handled separately, so filter them out:
        all_params = copy.copy(py_params)
        mypoplist = ['actuator','sensor', \
                     'sensor1','sensor2', \
                     'sensor_name','actuator_name']
        param_list = [item for item in all_params if item not in mypoplist]
        
        #N_params = len(param_list)
        #N_unused = self.max_params - N_params
        #self.N_params = N_params
        #self.unhide_used_widgets(N_params)
        #self.hide_unsed_widgets(N_unused)
        #self.update_param_labels(param_list)
        #self.set_default_params(param_list, default_params)
        return param_list, default_params
            


