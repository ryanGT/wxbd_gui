import wx

import py_block_diagram as pybd
import copy
myborder = 5
left_or_right = wx.LEFT|wx.RIGHT
not_bottom = left_or_right|wx.TOP
not_top = left_or_right|wx.BOTTOM 



def get_selected_string(widget):
    ind = widget.GetSelection()
    item = widget.GetString(ind)
    return item


class MenuParamsDialog(wx.Dialog): 
    def make_global_params_panel(self):
        self.gp_panel = wx.Panel(self.main_panel)
        self.gp_sizer = wx.GridSizer(2,vgap=0, hgap=10)
        self.global_params = wx.Choice(self.gp_panel, \
                    choices=self.global_params_list, size=(200,-1))
        label1 = wx.StaticText(self.gp_panel, label = "Global/System Parameters")
        empty1 = wx.StaticText(self.gp_panel, label = "")
        self.global_button = wx.Button(self.gp_panel, label="Add Global Param")
        self.gp_sizer.AddMany([(label1, 0, not_bottom, myborder), \
                               (empty1, 0), \
                               # wx.EXPAND|not_top
                               (self.global_params, 0, not_top, myborder), \
                               (self.global_button, 0, wx.ALL, myborder)])
        self.gp_panel.SetSizer(self.gp_sizer) 


    def make_block_params_panel(self):
        self.bp_panel = wx.Panel(self.main_panel)
        self.bp_sizer = wx.FlexGridSizer(4, 2, 0, 5)

        self.block_choice = wx.Choice(self.bp_panel, \
                                      choices=self.bd.block_name_list)
        label1 = wx.StaticText(self.bp_panel, label = "Block")
        empty1 = wx.StaticText(self.bp_panel, label = "")
        label2 = wx.StaticText(self.bp_panel, label = "Block Parameters")
        empty2 = wx.StaticText(self.bp_panel, label = "")
        empty3 = wx.StaticText(self.bp_panel, label = "")

        self.add_block_param_button = wx.Button(self.bp_panel, label="Add -->")
        self.block_params_listbox = wx.ListBox(self.bp_panel, size = (200,-1), \
                                               choices=[], \
                                               style = wx.LB_EXTENDED)#wx.LB_MULTIPLE|
 
        self.bp_sizer.AddMany([(label1, 0, not_bottom, myborder), \
                               (empty1, 0), \
                               (self.block_choice, 0, wx.EXPAND|not_top, myborder), \
                               (empty2, 0), \
                               (label2, 0, not_bottom, myborder), \
                               (empty3, 0), \
                               (self.block_params_listbox, 0, wx.EXPAND|not_top, myborder), \
                               (self.add_block_param_button, 0, wx.ALL, myborder)])

        self.bp_sizer.AddGrowableRow(3, 1)
        #self.bp_sizer.AddGrowableCol(0, 1)

        self.bp_panel.SetSizer(self.bp_sizer) 



    def make_chosen_params_panel(self):
        self.chosen_panel = wx.Panel(self.main_panel)
        self.chosen_sizer = wx.FlexGridSizer(4, 2, 0, 5)

        # add empty stuff at the top to shift it all down
        for i in range(4):
            curempty = wx.StaticText(self.chosen_panel, label = "")
            self.chosen_sizer.Add(curempty)

        label1 = wx.StaticText(self.chosen_panel, label = "Menu Parameters")
        empty1 = wx.StaticText(self.chosen_panel, label = "")
        empty2 = wx.StaticText(self.chosen_panel, label = "")
        empty3 = wx.StaticText(self.chosen_panel, label = "")

        self.remove_param_button = wx.Button(self.chosen_panel, label="Remove")
        self.chosen_params_listbox = wx.ListBox(self.chosen_panel, size = (200,-1), \
                                               choices=[], \
                                               style = wx.LB_EXTENDED)#wx.LB_MULTIPLE|
 
        self.chosen_sizer.AddMany([(label1, 0, not_bottom, myborder), \
                               (empty1, 0), \
                               (self.chosen_params_listbox, 0, wx.EXPAND|not_top, myborder), \
                               (self.remove_param_button, 0, wx.ALL, myborder), \
                               ])

        self.chosen_sizer.AddGrowableRow(3, 1)
        #self.chosen_sizer.AddGrowableCol(0, 1)

        self.chosen_panel.SetSizer(self.chosen_sizer) 


    def make_widgets(self):
        self.main_panel = wx.Panel(self) 
        self.wrapper = wx.BoxSizer(wx.VERTICAL)
        self.make_global_params_panel()
        self.wrapper.Add(self.gp_panel, flag=wx.EXPAND|wx.ALL, border=myborder)
        

        ## create hsizer
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.make_block_params_panel()
        #self.wrapper.Add(self.bp_panel, flag=wx.EXPAND|wx.ALL, border=myborder)
        self.hsizer.Add(self.bp_panel, flag=wx.EXPAND|wx.ALL, border=myborder)



        self.make_chosen_params_panel()
        #self.wrapper.Add(self.chosen_panel, flag=wx.EXPAND|wx.ALL, border=myborder)
        self.hsizer.Add(self.chosen_panel, flag=wx.EXPAND|wx.ALL, border=myborder)

        self.wrapper.Add(self.hsizer, flag=wx.EXPAND)

        self.go_button = wx.Button(self.main_panel, label="Done")
        self.cancel_button = wx.Button(self.main_panel, label="Cancel")
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.cancel_button, 0,flag = wx.ALL, \
                         border=15)
        empty1 = wx.StaticText(self.main_panel, label = "")
        button_sizer.Add(empty1, 1,flag = wx.ALL|wx.EXPAND, \
                         border=15)

        button_sizer.Add(self.go_button, 0,flag = wx.ALL, \
                         border=15)
        self.wrapper.Add(button_sizer, 1, flag = wx.ALL|wx.EXPAND, border = 15)


        
        self.main_panel.SetSizer(self.wrapper)

        

    def __init__(self, parent, title): 
        wx.Dialog.__init__(self,parent, title = title, \
                size=(700,400), \
                style=wx.RESIZE_BORDER|wx.CAPTION|wx.CLOSE_BOX)#, size = (250,150)) 
        self.parent = parent
        self.bd = self.parent.bd
        self.global_params_list = ['','stop_t']
        self.make_widgets()

        ## Bind stuff
        self.go_button.Bind(wx.EVT_BUTTON, self.on_go_button)
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel_button)
        self.global_button.Bind(wx.EVT_BUTTON, self.on_add_global_button)
        self.add_block_param_button.Bind(wx.EVT_BUTTON, self.on_add_button)
        self.remove_param_button.Bind(wx.EVT_BUTTON, self.on_remove_button)
        #self.Bind(wx.EVT_CLOSE, self.on_cancel_button)

        self.block_choice.Bind(wx.EVT_CHOICE, self.on_block_selected)
        self.block_choice.SetSelection(0)
        self.on_block_selected()


        bd_has_params = 0
        if hasattr(self.bd, "menu_param_list"):
            print("bd.menu_param_list: %s" % self.bd.menu_param_list)
                  
            if self.bd.menu_param_list:
                item_str_list = [row[0] for row in self.bd.menu_param_list]
                self.menu_params_list = item_str_list
                self.update_params_list()
                bd_has_params = 1

        if not bd_has_params:
            self.menu_params_list = []



    def on_go_button(self, *args, **kwargs):
        #append_menu_param_from_block(self, block, param_name, int_only=0):
        # Steps:
        # - split strings
        # - get blocks by name
        # - call append_menu_param_from_block
        # 
        # Note that the two append methods below default to 
        # float rather than int on the Arduino level.
        # - if I load the menu params from a csv from seld.bd
        #   and save those to the combobox, I loose the int preference
        #   - I can't think of that many int menu params right now, 
        #     but throwing away the option seems risky in the long run

        # Future feature: read from self.int_bool_list
        #                 to determine if a menu_param is only
        #                 allowed to be an int

        ## Assuming we have loaded the params correctly from self.bd, 
        ## we need to clear the list in self.bd before re-appending 
        ## everything
        self.bd.menu_param_list = []#clear
        for menu_str in self.menu_params_list:
            if "." in menu_str:
                # block parameters
                block_name, param_name = menu_str.split('.',1)
                block = self.bd.get_block_by_name(block_name)
                self.bd.append_menu_param_from_block(block, param_name)
            else:
                # global parameters
                self.bd.append_menu_param_global_variable(menu_str, \
                                            int_only=0)

        self.EndModal(1)
         


    def on_remove_button(self, *args, **kwargs):
        selected_indices = self.chosen_params_listbox.GetSelections()
        if selected_indices:
            selected_indices.reverse()
            for ind in selected_indices:
                self.menu_params_list.pop(ind)

            self.update_params_list()


    def _get_selected_params(self):
        selected_indices = self.block_params_listbox.GetSelections()
        selected_params = [self.block_params_listbox.GetString(ind) for ind in \
                                  selected_indices]
        return selected_params


    def append_to_int_bool(self):
        self.int_bool_list.append(0)#<-- no ints, only floats for menu_params
                                    #    for now.


    def update_params_list(self):
        self.chosen_params_listbox.Clear()
        if self.menu_params_list:
            self.chosen_params_listbox.InsertItems(self.menu_params_list,0)	

   
    def on_add_button(self, *args, **kwargs):
        block_name = get_selected_string(self.block_choice)
        selected_params = self._get_selected_params()
        param_strs = ["%s.%s" % (block_name, param) for param in \
                      selected_params]
        for item in param_strs:
            if item not in self.menu_params_list:
                self.menu_params_list.append(item)
        self.update_params_list()


    def load_menu_params_from_bd(self, *args, **kwargs):
        param_strs = []
        int_bool_list = []
        if hasattr(self.bd, "menu_param_list"):
            for row in self.bd.menu_param_list:
                param_strs.append(row[0])
                int_bool_list.append(row[1])
        
        self.menu_params_list = param_strs
        self.int_bool_list = int_bool_list
        self.menu_params_var.set(self.menu_params_list)


   
    def on_add_global_button(self, *args, **kwargs):
        var_name = get_selected_string(self.global_params)
        if var_name.strip():
            print("var_name = %s" % var_name)
            #do not allow duplicated entries:
            if var_name not in self.menu_params_list:
                self.menu_params_list.append(var_name)
                self.chosen_params_listbox.Append(var_name)


    def set_block_param_list(self, params_list):
        self.block_params_listbox.Clear()
        self.block_params_listbox.InsertItems(params_list,0)	
       

    def on_block_selected(self, *args, **kwargs):
        block_name = get_selected_string(self.block_choice)
        print("selected block name: %s" % block_name)
        block_instance = self.bd.get_block_by_name(block_name)
        self.selected_block = block_instance
        self.params_list = self.selected_block.param_list
        self.set_block_param_list(self.params_list)


    def on_save_changes_btn(self, *args, **kwargs):
        # approach:
        # - read the values from the widgets (done)
        # - see which values have changed (done)
        # - assign the changes to the block params
        # - deal with variable name changes if they have occured
        #     - how do we check for any blocks that have this block as an input?
        # - what happens if the user changed a sensor or actuator name?
        #     - do we want to make this impossible?
        #     - do we want to show comboxes for these
        other_kwargs = self.get_params_kwargs(self.N_params)
        kwargs = self.get_required_attrs_as_dict()
        kwargs.update(other_kwargs)
        self.new_kwargs = kwargs
        print("new_kwargs = %s" % self.new_kwargs)

        for key, value in self.original_kwargs.items():
            new_value = self.new_kwargs[key]
            if new_value != value:
                print("this changed: %s, %s --> %s" % (key, value, new_value))
                new_value = value_from_str(new_value)
                setattr(self.selected_block, key, new_value)
                if key == "variable_name":
                    self.bd.change_block_name(self.selected_block, new_value, value)
                    self.parent.block_list_var.set(self.bd.block_name_list)

        self.EndModal(1)
                

    def on_cancel_button(self, event):
        self.EndModal(0)

 
