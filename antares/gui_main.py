from gui_design import MyFrame1
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC
import public_function as pub_func


class DragonGUI(MyFrame1):
    bu_name = "TU"

    def set_bu_name(self, bu_name):
        self.__class__.bu_name = bu_name

    def bu_submit(self, event):
        self.clear_all_content()
        dict_bu_list = {'SPINE': 'SP', 'JOINT': 'JT', 'MITEK': 'MT', 'TRAUMA': 'TU', 'CMFT': 'CMF', 'PT': 'PT'}
        bu_result = self.rdbxBusinessUnit.GetStringSelection()
        self.__class__.bu_name = dict_bu_list[bu_result]
        self.txtLog.write("%s has been selected" % bu_result)
        self.statusBar.SetStatusText("Working BU: %s" % self.__class__.bu_name, 0)
        pass

    # Virtual event handlers, override them in your derived class
    def codeSubmit(self, event):
        # clean the column
        self.clear_frame_content()
        calculation_type = self.rdbxCalculationType.GetStringSelection()
        if calculation_type == "by Code":
            self.display_code_mapping_inventory()
        else:
            self.display_h5_inventory_detail()

    def display_h5_inventory(self, event):
        self.clear_frame_content()
        h5_name = self.lstbxH5.GetStringSelection()
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        [inventory_list, inventory_total] = CodeCalculation.get_h5_inv_detail(h5_name, table_name)
        self.show_inventory_list(inventory_list, 3)
        self.StatusBar.SetStatusText("Total Inventory: %s" % ("{:,.0f}".format(inventory_total)), 1)
        self.txtLog.Clear()
        self.txtLog.write("%s has been listed" % h5_name)
        pass

    def display_code_mapping_inventory(self):
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
                self.listCtrlOutput.SetItem(index, j + 1, str_output)
        self.txtLog.write("Done, with data of %s." % table_name)
        pass

    def display_h5_inventory_detail(self):
        self.txtLog.write("Display H5 Inventory")
        h5_name_hint = self.txtMaterialCode.Value
        h5_name_list = pub_func.get_available_h5_list(h5_name_hint, self.__class__.bu_name)
        self.lstbxH5.Clear()
        for item in h5_name_list:
            self.lstbxH5.Append(item)

    def get_current_inventory_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 1
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        [inventory_result, total_inventory] = CodeCalculation.get_current_inventory(table_name)
        self.show_inventory_list(inventory_result, data_trigger_point)
        self.StatusBar.SetStatusText("Total Available Stock: %s, Total Useful Stock: %s."
                                     % ("{:,.0f}".format(total_inventory[0]), "{:,.0f}".format(total_inventory[1])), 1)
        self.txtLog.Clear()
        self.txtLog.write("Current Inventory List done, with data of %s." % table_name)

    def get_current_bo_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 4
        CodeCalculation = CIC(self.__class__.bu_name)
        table_name = CodeCalculation.get_newest_date()
        inventory_result = CodeCalculation.get_current_bo(table_name)
        self.show_inventory_list(inventory_result, data_trigger_point)
        self.txtLog.write("Current Backorder List done, with data of %s." % table_name)

    def display_aging_backorder(self, event):
        self.clear_frame_content()
        CodeCalculation = CIC(self.__class__.bu_name)
        # set exception list with abnormal backorder information
        exception_list = ["INV20200330", "INV20200331"]
        self.txtLog.Clear()
        self.txtLog.write("Calculation ongoing, please wait a moment...")
        [inventory_result, mapping_days] = CodeCalculation.calculate_aging_backorder(exception_list)
        data_trigger_point = 5
        self.show_inventory_list(inventory_result, data_trigger_point)
        self.StatusBar.SetStatusText("Total Mapping %s days" % ("{:,.0f}".format(mapping_days)), 1)
        self.txtLog.Clear()
        self.txtLog.write("Aging backorder calculation finished.")

    # shared function to display data in column list
    def show_inventory_list(self, inventory_result, data_trigger_point):
        column_title = ["No", ] + list(inventory_result[0])
        for i in range(0, len(column_title)):
            if i <= data_trigger_point:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_LEFT)
            else:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_RIGHT)
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                str_output = "{:,.0f}".format(inventory_result[i][j]) if j >= data_trigger_point else str(
                    inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j + 1, str_output)

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
        self.StatusBar.SetStatusText(" ", 1)

    def clear_all_content(self):
        self.listCtrlOutput.ClearAll()
        self.lstbxH5.Clear()
        self.txtMaterialCode.Clear()
        self.txtLog.Clear()
        self.StatusBar.SetStatusText(" ", 1)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    DragonGUI(None).Show()
    app.MainLoop()
