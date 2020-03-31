from wxPython_Test_01 import MyFrame1
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC


class DragonGUI(MyFrame1):
    bu_name = "TU"

    def set_bu_name(self, bu_name):
        self.__class__.bu_name = bu_name

    def bu_submit(self, event):
        self.txtLog.Clear()
        dict_bu_list = {'SPINE': 'SP', 'JOINT': 'JT', 'MITEK': 'MT', 'TRAUMA': 'TU', 'CMFT': 'CMFT', 'PT': 'PT'}
        bu_result = self.rdbxBusinessUnit.GetStringSelection()
        self.bu_name = dict_bu_list[bu_result]
        self.txtLog.write("%s has been selected" % bu_result)
        pass

    # Virtual event handlers, override them in your derived class
    def codeSubmit(self, event):
        # clean the column
        self.clean_column_list()
        # get code list and newest timing to mapping
        code_name_list = self.txtMaterialCode.Value.split()
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        inventory_result = CodeCalculation.inventory_mapping(code_name_list, table_name)
        column_title = ["No", ] + inventory_result[0]
        for i in range(0, len(column_title)):
            self.listCtrlOutput.InsertColumn(i, column_title[i])
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                self.listCtrlOutput.SetItem(index, j+1, str(inventory_result[i][j]))
        self.txtLog.write("Done, with data of %s." % table_name)

    def clean_column_list(self):
        self.listCtrlOutput.ClearAll()
        self.txtLog.Clear()
        pass


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    DragonGUI(None).Show()
    app.MainLoop()
