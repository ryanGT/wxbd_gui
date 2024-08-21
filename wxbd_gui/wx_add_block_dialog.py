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


class params_mini_panel(wx.Panel):
    def __init__(self, parent, param_label):
        wx.Panel.__init__(self, parent)
        self.param_label = param_label
        self.vbox = wx.BoxSizer(wx.VERTICAL) 
        # - create label and textctrl
        # - create vertical sizer
        # - add tabel and textctrl to sizer with padding
        self.label = wx.StaticText(self, label=param_label)
        self.text = wx.TextCtrl(self, size=(100,10))
        self.vbox.Add(self.label, wx.TOP|wx.LEFT|wx.RIGHT)
        self.vbox.Add(self.text, wx.BOTTOM|wx.LEFT|wx.RIGHT)#|wx.EXPAND)
        self.SetSizer(self.vbox)


    def GetValue(self):
        return self.text.GetValue()


    def SetValue(self, mystr):
        self.text.SetValue(mystr)


    def remove_widgets(self):
        N = len(self.vbox.GetChildren())
        print("N = %i" % N)
        for i in range(N):
            self.vbox.Remove(0)
        
        self.Layout()
        self.Update()



    def del_widgets(self):
        del self.text
        del self.label
        self.Layout()
        self.Update()






class AddBlockDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(AddBlockDialog, self).__init__(parent, title = title, \
                size=(700,500), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        panel = wx.Panel(self) 
        self.panel = panel

        sizer = wx.FlexGridSizer(10, 2, 5, 5)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        self.categories_choice = wx.Choice(panel,choices=pybd.block_categories)
        self.block_type_list = wx.ListBox(panel, size = (100,-1), \
                               choices=[], style = wx.LB_SINGLE)
        
        sizer.AddMany([ (wx.StaticText(panel, label = "Block Category")),
                        (wx.StaticText(panel, label = "Block Name")),
                        (self.categories_choice, 0, wx.EXPAND),
                        (wx.TextCtrl(panel), 0, wx.EXPAND),
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

        self.categories_choice.Bind(wx.EVT_CHOICE, self.OnCategoryChoice)
           
        cat_ind = self.categories_choice.GetSelection()
        print("cat_ind: %s" % cat_ind)
        self.category_selected()
        self.Bind(wx.EVT_LISTBOX, self.on_block_type_choice, self.block_type_list) 
        panel.SetSizer(wrapper)
        

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
        self.params_sizer = wx.GridSizer(cols=2)
        

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


    def on_block_type_choice(self, event):
        print("block type selected")
        # this is where the params panel needs to be deleted and recreated
        #
        # - how to handle plants that have no actuators or something like that?
        self.delete_params_panels()
        self.delete_params_sizer_and_panel()
        self.create_params_sizer_and_panel()
        ind = self.block_type_list.GetSelection()
        block_type = self.block_type_list.GetString(ind)
        params, default_params = self.get_params_for_block_type(block_type)
        print("params: ")
        print(params)
        print('\n')
        print('default_params:')
        print(default_params)
        self.create_params_panels(params)
        self.main_sizer.Add(self.params_sizer, wx.EXPAND)
        self.panel.Layout()
        self.panel.Update()



    def create_params_panels(self, params):
        # - doing this as two columns seems tricky
        # - I need to add two labels and then two widgets in 
        #   alternating rows
        # - is this worth the pain?
        # - do I divide them ahead of time into column groups?
        # - do I create multiple panels somehow?
        # - does each label/widget pair go on a panel?
        self.params_widget_dict = {}
        self.params_panels = []

        for param in params:
            curpanel = params_mini_panel(self.panel, param) 
            self.params_panels.append(curpanel)
            self.params_widget_dict[param] = curpanel
            self.params_sizer.Add(curpanel)


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
            


