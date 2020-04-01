from wxPython_Test_01 import MyFrame1
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC


class DragonGUI(MyFrame1):
    bu_name = "TU"

    def set_bu_name(self, bu_name):
        self.__class__.bu_name = bu_name

    def bu_submit(self, event):
        self.clear_frame_content()
        dict_bu_list = {'SPINE': 'SP', 'JOINT': 'JT', 'MITEK': 'MT', 'TRAUMA': 'TU', 'CMFT': 'CMF', 'PT': 'PT'}
        bu_result = self.rdbxBusinessUnit.GetStringSelection()
        self.__class__.bu_name = dict_bu_list[bu_result]
        self.txtLog.write("%s has been selected" % bu_result)
        pass

    # Virtual event handlers, override them in your derived class
    def codeSubmit(self, event):
        # clean the column
        self.clear_frame_content()
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
                str_output = "{:,.0f}".format(inventory_result[i][j]) if j > 3 else str(inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j+1, str_output)
        self.txtLog.write("Done, with data of %s." % table_name)

    def get_current_inventory_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 1
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        inventory_result = CodeCalculation.get_current_inventory(table_name)[0]
        column_title = ["No", ] + list(inventory_result[0])
        for i in range(0, len(column_title)):
            if i <= data_trigger_point:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_LEFT)
            else:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_RIGHT)
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                str_output = "{:,.0f}".format(inventory_result[i][j]) if j >= data_trigger_point else str(inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j + 1, str_output)
        self.txtLog.write("Current Inventory List done, with data of %s." % table_name)

    def get_current_bo_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 4
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        inventory_result = CodeCalculation.get_current_bo(table_name)
        column_title = ["No", ] + list(inventory_result[0])
        for i in range(0, len(column_title)):
            if i <= data_trigger_point:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_LEFT)
            else:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_RIGHT)
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                str_output = "{:,.0f}".format(inventory_result[i][j]) if j >= data_trigger_point else str(inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j + 1, str_output)
        self.txtLog.write("Current Backorder List done, with data of %s." % table_name)
        pass

    def sync_inventory(self, event):
        lst_xcpt = []
        self.clear_frame_content()
        self.txtLog.write("Start to sync. Please wait~")
        CodeCalculation = CIC(self.__class__.bu_name)
        sync_result = CodeCalculation.inv_data_sync(90, lst_xcpt)
        if sync_result == "ERROR":
            self.txtLog.Clear()
            self.txtLog.write("Sync failure. Please make sure you've connected to JNJ network")
        else:
            self.txtLog.Clear()
            self.txtLog.write("Done. %s days succeed, %s days fail" % (sync_result[0], sync_result[1]))

    def clear_frame_content(self):
        self.listCtrlOutput.ClearAll()
        self.txtLog.Clear()
        pass


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    DragonGUI(None).Show()
    app.MainLoop()
