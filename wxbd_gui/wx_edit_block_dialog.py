import wx

import py_block_diagram as pybd
import copy

## The Plan:
##
## - show the name of the block
## - show its parameters
## - show the actuator and sensor if relevant


max_params = 6# the maximum number of parameres a block is assumed to have

from wxbd_gui.wxbd_utils import params_mini_panel
from wxbd_gui.wx_add_actuator_or_sensor_dialog import AddActuatorDialog, \
                        AddSensorDialog



class EditBlockDialog(wx.Dialog): 
    def _make_main_sizers_and_panel(self):
        self.panel = wx.Panel(self) 
        self.fgsizer = wx.FlexGridSizer(6, 1, 5, 5)
        self.wrapper = wx.BoxSizer(wx.VERTICAL)
 


    def handle_actuator_and_sensor(self):
        # how do I test for a plant?
        if isinstance(self.block_instance, pybd.plant):
            if not isinstance(self.block_instance, pybd.plant_no_actuator):
                print("block has an actuator")
                # - create button
                # - add it to fgsizer
                # - bind it
                self.change_act_button = wx.Button(self.panel, \
                        label="Change Actuator")
                self.fgsizer.Add(self.change_act_button, flag = wx.ALL, \
                         border=7)
                self.change_act_button.Bind(wx.EVT_BUTTON, self.on_change_act)
            # all plants have sensors (I think)
            self.change_sensor_button =  wx.Button(self.panel, \
                        label="Change Sensor")
            self.fgsizer.Add(self.change_sensor_button, flag = wx.ALL, \
                         border=7)
            self.change_sensor_button.Bind(wx.EVT_BUTTON, \
                                           self.on_change_sensor)


    def on_change_sensor(self, *args, **kwargs):
        print("in on_change_sensor")
        dlg = AddSensorDialog(self, "Add Sensor Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something with this sensor.")
            self.sensor = dlg.sensor_instance
            old_name = self.block_instance.sensor_name
            new_name = self.sensor.variable_name
            self.bd.replace_sensor(old_name, new_name, self.sensor)
            self.block_instance.replace_sensor(self.sensor)
            self.load_values_from_instance()
            # need to place the new block
            #self.on_draw_btn()
        else:
            self.sensor = None

        dlg.Destroy()



    def on_change_act(self, *args, **kwargs):
        print("in on_change_act")
        dlg = AddActuatorDialog(self, "Add Actuator Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something with this actuator.")
            self.actuator = dlg.actuator_instance
            old_name = self.block_instance.actuator_name
            new_name = self.actuator.variable_name
            self.bd.replace_actuator(old_name, new_name, self.actuator)
            self.block_instance.replace_actuator(self.actuator)
            #I should also update the actutor name box
            self.load_values_from_instance()
        else:
            self.actuator = None

        dlg.Destroy()
        return out



    def make_widgets(self):
        self.block_name_box = wx.TextCtrl(self.panel)
        self.block_name_box.SetValue(self.block_name)

        self.fgsizer.AddMany([ (wx.StaticText(self.panel, label = "Block Name")),
                        (self.block_name_box, 0, wx.EXPAND),
                       ])
    
        self.fgsizer.AddGrowableCol(0, 1)
        self.main_sizer = self.fgsizer 
        self.wrapper.Add(self.fgsizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
        ## Buttons
        self.go_button = wx.Button(self.panel, label="Apply")
        self.cancel_button = wx.Button(self.panel, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, wx.ALIGN_LEFT,flag = wx.ALL, \
                         border=15)
        button_sizer.Add(self.go_button, wx.ALIGN_RIGHT,flag = wx.ALL, \
                         border=15)
        self.wrapper.Add(button_sizer, 1, flag = wx.ALL, border = 15)

        ## Params panels
        self.create_params_sizer_and_panel()
        self.create_params_panels()
        self.main_sizer.Add(self.params_sizer, wx.EXPAND)

        ## I need to handle sensor and actuator if needed
        self.handle_actuator_and_sensor()

        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)

        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)


        self.load_values_from_instance()
        self.panel.SetSizer(self.wrapper)




    def __init__(self, parent, title, block_name, block_instance): 
        super(EditBlockDialog, self).__init__(parent, title = title, \
                size=(400,550), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        self.parent = parent
        self.bd = self.parent.bd
        self.block_name = block_name
        self.block_instance = block_instance
        self.param_list = self.block_instance.param_list
        self._make_main_sizers_and_panel()
        self.make_widgets()


    def deselect_inputs(self):
        inds = self.input_list.GetSelections()
        for ind in inds:
            self.input_list.Deselect(ind)
                

    
    def on_clear_button(self, event):
        if not hasattr(self, "input_selection_ind"):
            # do nothing
            # - nothing was selected
            return None
        else:
            if self.input_selection_ind is not None:
                self.input_list.Deselect(self.input_selection_ind)
                self.input_selection_ind = None
                self.input_block_name = None


    def on_input_choice(self, event):
        ind = self.input_list.GetSelection()
        self.input_selection_ind = ind
        print("ind = %s" % ind)
        if ind is not None:
            input_string = self.bd.block_name_list[ind]
            print("input_string = %s" % input_string)
            self.input_block_name = input_string



    def _create_new_block(self, block_type, block_name, params):
        # - How did this work with mytk version?
        # - How do I want it to work now?
        kwargs = {}

        ##-------------------------------------------------
        ## Key questions for wx version:
        # - how am I handling inputs?
        # - how am I handling actuators and sensors?
        ##-------------------------------------------------

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
                input_block = self.bd.get_block_by_name(input_block_name)
                kwargs[key] = input_block
                key2 = key + '_name'
                kwargs[key2] = input_block_name 
        
        print("after looking for inputs, kwargs = %s" % kwargs)

        block_class = getattr(pybd, block_type)
        # how do I handle cases with input(s) set?

        # get actuator and sensor if it is a plant
        print("plant classes: %s" % pybd.plant_class_names)
        
        has_act = 0
        has_sense_1 = 0
        if block_type in pybd.plant_class_names:
            # we need to handle plant classes with no actuator and those with two sensors
            print("this is a plant")

            # possible cases:
            # - actuator or no actuator
            # - one sensor or two
            #     - must have at least one sensor to be a plant
            if block_type not in pybd.plants_with_no_actuators_names:
                print("plant has an actuator")
                out = self.onAddActuator()
                print("out = %s" % out)
                if out != 1:
                    # users cancelled actuator creation dialog
                    # - do nothing
                    return None

                kwargs['actuator'] = self.actuator
                has_act = 1

            if block_type in pybd.plants_with_two_sensors_names:
                print("fix two sensors plants")
                pass
                # it has two sensors
                #sensor1_name = self.sensors_var.get()
                #print("sensor1_name: %s" % sensor1_name)
                #sensor2_name = self.sensor2_var.get()
                #print("sensor2_name: %s" % sensor2_name)
                #sensor1 = self.bd.get_sensor_by_name(sensor1_name)                
                #kwargs['sensor1'] = sensor1
                #sensor2 = self.bd.get_sensor_by_name(sensor2_name)                
                #kwargs['sensor2'] = sensor2                
            else:
                # it has only one sensor
                out = self.onAddSensor()
                print("out = %s" % out)
                if out != 1:
                    # users cancelled sensor creation dialog
                    # - do nothing
                    return None
                # if out == 1, then self.sensor has been set with the 
                # sensor instance

                kwargs['sensor'] = self.sensor
                has_sense_1 = 1

            
        ## I need to append the actuator and sensor to
        ## self.bd, but I want to make sure the block creation
        ## was successful so that I don't add multiple actuators
        ## or sensors that are kind of floating
        if has_act:
            self.bd.append_actuator(self.actuator)
        if has_sense_1:
            self.bd.append_sensor(self.sensor)

        # get additional kwargs from param boxes here:
        #other_kwargs = self.get_params_kwargs(self.N_params)
        ## print("other_kwargs:")
        ## print(other_kwargs)
        kwargs.update(params) 
        print("creating block in go_pressed")
        print("kwargs:")
        print(kwargs)
        new_block = pybd.create_block(block_class, block_type, \
                block_name, **kwargs)
        return new_block

    
    def on_cancel_button(self, event):
        self.EndModal(0)



    def get_block_type_and_name(self):
        ind = self.block_type_list.GetSelection()
        block_type = self.block_type_list.GetString(ind)
        block_name = self.block_name_box.GetValue()
        return block_type, block_name

 

    def on_go_button(self, event):
        mydict = self.read_params_from_boxes()
        print("mydict = %s" % mydict)
        # how do we handle any changes the user made?
        # - what if they changed the block name?
        # - can I immediately use setattr on mydict to update things?
        #     - done
        for key, val in mydict.items():
            setattr(self.block_instance, key, val)


        curname = self.block_name_box.GetValue()
        if curname != self.block_name:
            new_name = curname
            old_name = self.block_name
            self.parent.change_block_name(self.block_instance, old_name, \
                    new_name)

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

        N = len(self.block_instance.param_list)

        for i in range(N):
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



    def set_params_labels(self, param_list):
        for i, p in enumerate(param_list):
            curpanel = self.params_panels[i]
            curpanel.SetLabel(p)


    def load_values_from_instance(self):
        # need to also handle the labels of the text boxes
        # - i.e. static text
        for i, p in enumerate(self.param_list):
            curpanel = self.params_panels[i]
            if hasattr(self.block_instance, p):
                val = getattr(self.block_instance, p)
                # does the params_panel handle converting
                # this to a str?
                curpanel.SetValue(str(val))
                curpanel.SetLabel(p)


    def read_params_from_boxes(self):
        mydict = {}

        for i, p in enumerate(self.param_list):
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
            


