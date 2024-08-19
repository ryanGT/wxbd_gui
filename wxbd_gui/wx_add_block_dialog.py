import wx

import py_block_diagram as pybd

class AddBlockDialog(wx.Dialog): 
    def __init__(self, parent, title): 
        super(AddBlockDialog, self).__init__(parent, title = title, size = (250,150)) 
        panel = wx.Panel(self) 
        # - create dialog of my design
        # - show it
        # - get response in some form
        sizer = wx.FlexGridSizer(5, 2, 5, 5)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        self.categories_choice = wx.Choice(panel,choices=pybd.block_categories)
        sizer.AddMany([ (wx.StaticText(panel, label = "Block Category")),
                        (wx.StaticText(panel, label = "Block Name")),
                        (self.categories_choice, 0, wx.EXPAND),
                        (wx.TextCtrl(panel), 0, wx.EXPAND),
                       ])
 
        sizer.AddGrowableCol(1, 1)
 
        wrapper.Add(sizer, 1, flag = wx.ALL | wx.EXPAND, border = 15)
        self.categories_choice.Bind(wx.EVT_CHOICE, self.OnCategoryChoice)
           
        cat_ind = self.categories_choice.GetSelection()
        print("cat_ind: %s" % cat_ind)
        self.category_selected()
        panel.SetSizer(wrapper)


    def category_selected(self):
        cat_ind = self.categories_choice.GetSelection()
        chosen_cat = pybd.block_categories[cat_ind]
        new_list = pybd.block_category_dict[chosen_cat]
        print("new_list: %s" % new_list)


    def OnCategoryChoice(self,event): 
        cat_choice = self.categories_choice.GetSelection()
        print("cat_choice: %s" % cat_choice)
        self.category_selected()



