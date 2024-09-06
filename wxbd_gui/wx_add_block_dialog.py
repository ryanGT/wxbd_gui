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
from wxbd_gui.wx_add_actuator_or_sensor_dialog import AddActuatorDialog, \
                        AddSensorDialog


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
    def _make_main_sizers_and_panel(self):
        self.panel = wx.Panel(self) 
        self.fgsizer = wx.FlexGridSizer(9, 2, 5, 5)
        self.wrapper = wx.BoxSizer(wx.VERTICAL)
 

    def make_widgets(self):
        self.categories_choice = wx.Choice(self.panel,choices=pybd.block_categories)
        self.block_type_list = wx.ListBox(self.panel, size = (100,-1), \
                               choices=[], style = wx.LB_SINGLE)
        self.input_list = wx.ListBox(self.panel, size = (100,-1), \
                                 choices=self.bd.block_name_list, \
                                 style = wx.LB_SINGLE)
        self.clear_button = wx.Button(self.panel, label="Clear Input")

       
        self.block_name_box = wx.TextCtrl(self.panel)

        self.fgsizer.AddMany([ (wx.StaticText(self.panel, label = "Block Category")),
                        (wx.StaticText(self.panel, label = "Block Name")),
                        (self.categories_choice, 0, wx.EXPAND),
                        (self.block_name_box, 0, wx.EXPAND),
                        (wx.StaticText(self.panel, label = "Block Types")),
                        (wx.StaticText(self.panel, label = "Input")),
                        (self.block_type_list, 0, wx.EXPAND),
                        (self.input_list, 0, wx.EXPAND),
                        (wx.StaticText(self.panel, label = "")),
                        (self.clear_button, 0, wx.ALL),
                       ])
    
        self.fgsizer.AddGrowableCol(0, 1)
        self.main_sizer = self.fgsizer 
        self.wrapper.Add(self.fgsizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
        ## Buttons
        self.go_button = wx.Button(self.panel, label="Add Block")
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

        self.categories_choice.Bind(wx.EVT_CHOICE, self.OnCategoryChoice)
          
        input_names = ['input_block_name', \
                       'input2_block_name', \
                       'input3_block_name']
        for name in input_names:
            setattr(self, name, None)

        cat_ind = 0#self.categories_choice.GetSelection()
        print("cat_ind: %s" % cat_ind)
        self.category_selected()
        self.Bind(wx.EVT_LISTBOX, self.on_block_type_choice, self.block_type_list) 
        self.Bind(wx.EVT_LISTBOX, self.on_input_choice, self.input_list) 

        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.clear_button.Bind(wx.EVT_BUTTON, self.on_clear_button)

        self.Bind(wx.EVT_CLOSE, self.on_cancel_button)
        self.panel.SetSizer(self.wrapper)




    def __init__(self, parent, title): 
        super(AddBlockDialog, self).__init__(parent, title = title, \
                size=(700,550), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        self.parent = parent
        self.bd = self.parent.bd
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


    def onAddActuator(self, event=None):
        dlg = AddActuatorDialog(self, "Add Actuator Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something with this actuator.")
            self.actuator = dlg.actuator_instance
            # need to place the new block
            #self.on_draw_btn()
        else:
            self.actuator = None

        dlg.Destroy()
        return out


    def onAddSensor(self, event=None):
        dlg = AddSensorDialog(self, "Add Sensor Dialog")
        out = dlg.ShowModal()
        print("out = %s" % out)
        if out == 1:
            # If the add block dialog returned 1, it
            # called append_block_to_dict.
            # guess the block placement, then draw
            print("I should do something with this sensor.")
            self.sensor = dlg.sensor_instance
            # need to place the new block
            #self.on_draw_btn()
        else:
            self.sensor = None

        dlg.Destroy()
        return out


#    def _create_new_block(self, block_type, block_name, mydict):
#        block_class = getattr(pybd, block_type)
#
#        if block_type in pybd.plant_class_names:
#            # we need to handle plant classes with no actuator and those with two sensors
#            print("this is a plant")
#
#            # possible cases:
#            # - actuator or no actuator
#            # - one sensor or two
#            #     - must have at least one sensor to be a plant
#            if block_type not in pybd.plants_with_no_actuators_names:
#                # it has an actuator
#                print("plant has an actuator")
#                out = self.onAddActuator(event)
#                print("out = %s" % out)
#                if out != 1:
#                    # users cancelled actuator creation dialog
#                    # - do nothing
#                    return None
#                # if out == 1, then self.actuator has been set with the 
#                # actuator instance
#
#            if block_type in pybd.plants_with_two_sensors_names:
#                ## handle this eventually
#                pass
#            #    # it has two sensors
#            #    sensor1_name = self.sensors_var.get()
#            #    print("sensor1_name: %s" % sensor1_name)
#            #    sensor2_name = self.sensor2_var.get()
#            #    print("sensor2_name: %s" % sensor2_name)
#            #    sensor1 = self.bd.get_sensor_by_name(sensor1_name)                
#            #    kwargs['sensor1'] = sensor1
#            #    sensor2 = self.bd.get_sensor_by_name(sensor2_name)                
#            #    kwargs['sensor2'] = sensor2                
#            else:
#                print("plant has an actuator")
#                out = self.onAddSensor(event)
#                print("out = %s" % out)
#                if out != 1:
#                    # users cancelled sensor creation dialog
#                    # - do nothing
#                    return None
#                # if out == 1, then self.sensor has been set with the 
#                # sensor instance
#
#            #    # it has only one sensor
#            #    sensor_name = self.sensors_var.get()
#            #    print("sensor_name: %s" % sensor_name)
#            #    mysensor = self.bd.get_sensor_by_name(sensor_name)
#            #    kwargs['sensor'] = mysensor
#
#
#        new_block = pybd.create_block(block_class, block_type, \
#                block_name, **kwargs)
#        return new_block 


    def get_block_type_and_name(self):
        ind = self.block_type_list.GetSelection()
        block_type = self.block_type_list.GetString(ind)
        block_name = self.block_name_box.GetValue()
        return block_type, block_name

 

    def on_go_button(self, event):
        mydict = self.read_params_from_boxes()
        print("mydict = %s" % mydict)
        block_type, block_name = self.get_block_type_and_name()
         # if we are about to create a plant, we need to do something
        # - does it need an actuator?
        #     - more than one?
        # - does it need a sensor?
        #     - more than one?
                # how do I handle cases with input(s) set?

        # get actuator and sensor if it is a plant
        #print("plant classes: %s" % pybd.plant_class_names)
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
            



class ReplaceBlockDialog(AddBlockDialog):
    def make_widgets(self):
        replace_label = wx.StaticText(self.panel, label = "Block to Replace")
        self.replace_choice = wx.Choice(self.panel,choices=self.bd.block_name_list)

        empty1 = wx.StaticText(self.panel, label = "")
        empty2 = wx.StaticText(self.panel, label = "")

        self.fgsizer.AddMany([ (replace_label, 0, wx.LEFT|wx.RIGHT|wx.TOP), \
                               (empty1, 0), \
                               (self.replace_choice, 0, \
                                wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND),
                               (empty2, 0)])
        AddBlockDialog.make_widgets(self)
        self.go_button.SetLabel("Replace Block")
        self.replace_choice.SetSelection(0)
        self.replace_choice.Bind(wx.EVT_CHOICE, self.on_replacement_selected)
        self.on_replacement_selected()



    def _get_old_block_name(self):
        ind = self.replace_choice.GetSelection()
        old_name = self.replace_choice.GetString(ind)
        return old_name


    def on_replacement_selected(self, *args, **kwargs):
        # what needs to actually happen here?
        # - copy any info from the block to replace into a kwargs dict
        # - the new block should have the same input(s) and placement info
        #   as the block it is replacing
        # - is there anything else to copy over?
        print("in on_replacement_selected")
        # if the old block has inputs, set the input widget values here
        self.old_block_name = self._get_old_block_name()
        print("self.old_block_name = %s" % self.old_block_name)
        self.old_block = self.bd.get_block_by_name(self.old_block_name)
        #self.input_block1 = input_block1
        has_input = 0
        if hasattr(self.old_block, "input_block1_name"):
            input1_name = self.old_block.input_block1_name
            if input1_name:
                #selection_clear(0, END), then selection_set
                #mylist = self.input_choice.get(0, "end")
                #ind = int(mylist.index(input1_name))
                #self.input_choice.selection_set(ind)
                #-----
                #
                # What is the wxPython way to do this?
                #
                #-----
                ind = self.input_list.FindString(input1_name)
                self.input_list.SetSelection(ind)
                has_input = 1
        
        if not has_input:
            # clear selection
            self.deselect_inputs()


    def get_input_names(self):
        input_kwargs = {}
        for i in range(1,3):
            attr = "input_block%i_name" % i
            if hasattr(self.old_block, attr):
                val = getattr(self.old_block, attr)
                input_kwargs[attr] = val
        self.input_kwargs = input_kwargs


    def get_old_position_info(self):
        placement_kwargs = {}
        if hasattr(self.old_block, "placement_type") and self.old_block.placement_type:
            pt = self.old_block.placement_type
            placement_kwargs['placement_type'] = pt
            if pt == 'absolute':
                mykeys = ['abs_x','abs_y']
            else:
                mykeys = ['rel_block_name','rel_pos','rel_distance','xshift','yshift']
            
            for key in mykeys:
                attr = getattr(self.old_block, key)
                placement_kwargs[key] = attr

        self.placement_kwargs = placement_kwargs
        return self.placement_kwargs




    def set_inputs(self, new_block):
        for i in range(1,3):
            attr = "input_block%i_name" % i
            if attr in self.input_kwargs:
                name = self.input_kwargs[attr]
                if name:
                    # the defaults inherited from block might nead to an empty
                    # name
                    # - if the input is a sensor, this breaks:
                    if self.parent.bd.has_block(name):
                        in_block = self.parent.bd.get_block_by_name(name)
                    else:
                        # hope the other option is true
                        in_block = self.parent.bd.get_sensor_by_name(name)

                    method_name = "set_input_block%i" % i
                    if hasattr(new_block, method_name):
                        mymethod = getattr(new_block, method_name)
                        mymethod(in_block)
     


    def place_new_block(self, new_block, place_dict):
        # Next step:
        # - read parameters from the numbered param boxes for kwargs
        # - kwargs are handled by self._create_new_block, which mostly reads
        #   from the widgets
        # - if we want to pass kwargs from old block to new block, we should
        #   probably pass those values to the widgets as an intermediate step
        # - placement stuff needs to be handled separately
        #
        # Conceptual question: do I force the new block to have the same
        # input(s) as the old block?
        #import pdb
        #pdb.set_trace()
        #place_dict = copy.copy(self.placement_kwargs)
        pt = place_dict.pop('placement_type')

        print("place_dict = %s" % place_dict)

        if pt == 'absolute':
            # get abs kwargs
            #place_absolute(self, x=None, y=None):
            x_abs = place_dict['abs_x']
            y_abs = place_dict['abs_y']
            new_block.place_absolute(x=x_abs, y=y_abs)
        elif pt == 'relative':
            rel_block_name = place_dict.pop('rel_block_name')
            if rel_block_name in self.parent.bd.block_dict:
                rel_block = self.parent.get_block_by_name(rel_block_name)
                new_block.place_relative(rel_block, **place_dict)
        else:
            pt_str = pt.strip()
            if pt_str:
                raise ValueError("placement type not understood: %s" % pt_str)
            
        # - handle input(s)
        # get_block_by_name
        # set_input_block1
        # set_input_block2
        # - handled placement
        # - find all references in self.parent.bd and replace them:
        # When this is done, how to I verify that the dict is right and 
        # the name of the new_block matches the old_block and all 
        # references have updated?
        #self.destroy()



    def on_go_button(self, event):
        print("I should do something.")
        mydict = self.read_params_from_boxes()
        print("mydict = %s" % mydict)
        block_type, block_name = self.get_block_type_and_name()
         # if we are about to create a plant, we need to do something
        # - does it need an actuator?
        #     - more than one?
        # - does it need a sensor?
        #     - more than one?
                # how do I handle cases with input(s) set?

        # get actuator and sensor if it is a plant
        #print("plant classes: %s" % pybd.plant_class_names)
        new_block = self._create_new_block(block_type, block_name, mydict)

        self.get_input_names()
        self.set_inputs(new_block)
        self.get_old_position_info()
        place_dict = copy.copy(self.placement_kwargs)
        self.place_new_block(new_block, place_dict)
        self.parent.bd.replace_block(self.old_block, new_block)
        self.parent.update_block_list()

        self.EndModal(1)


