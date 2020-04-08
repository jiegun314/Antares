from gui_design import DragonFrame, dlgAbout
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC
import public_function as pb_func


class DragonGUI(DragonFrame):
    bu_name = ""
    table_to_use = ""

    def __init__(self, parent):
        DragonFrame.__init__(self, parent)
        self.pnlSummary.Hide()
        self.Layout()
        # set TU as default BU
        self.__class__.bu_name = "TU"
        self.display_bu_update()
        # set ICON
        self.icon = wx.Icon(u'.icon/logo.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icon)
        # set default as today
        self.chkbxToday.SetValue(1)
        self.dtpkDate.Disable()
        self.set_db_table("newest")

    def set_bu_name(self, bu_name):
        self.__class__.bu_name = bu_name

    def select_bu_CMFT(self, event):
        self.__class__.bu_name = "CMF"
        self.display_bu_update()
        # update current date to CMF
        self.set_db_table("newest")

    def select_bu_TU(self, event):
        self.__class__.bu_name = "TU"
        self.display_bu_update()
        # update current date to TU
        self.set_db_table("newest")

    def select_bu_PT(self, event):
        self.__class__.bu_name = "PT"
        self.display_bu_update()
        # update current date to PT
        self.set_db_table("newest")

    def display_bu_update(self):
        self.txtLog.Clear()
        self.txtLog.write("%s has been selected" % self.__class__.bu_name)
        self.statusBar.SetStatusText("Working BU: %s" % self.__class__.bu_name, 0)

    def set_date_as_today(self, event):
        # clean the column
        self.clear_frame_content()
        today_status = self.chkbxToday.GetValue()
        if today_status:
            self.dtpkDate.Disable()
            self.set_db_table("newest")
        else:
            self.dtpkDate.Enable()
        pass

    def set_checking_date(self, event):
        [date_year, date_month, date_day] = str(self.dtpkDate.GetValue()).split()[0].split("/")
        if len(date_month) == 1:
            date_month = "0" + date_month
        if len(date_day) == 1:
            date_day = "0" + date_day
        date_to_check = date_year + date_month + date_day
        self.set_db_table(date_to_check)
        self.txtLog.Clear()
        self.txtLog.AppendText("%s would be used." % date_to_check)

    # define the table for calculation in datepicker
    def set_db_table(self, date):
        CodeCalculation = CIC(self.__class__.bu_name)
        self.table_to_use = CodeCalculation.get_newest_date() if date == "newest" else "INV" + date

    # Virtual event handlers, override them in your derived class
    def codeSubmit(self, event):
        # clean the column
        self.clear_frame_content()
        calculation_type = self.rdbxCalculationType.GetStringSelection()
        if calculation_type == "by Code":
            self.display_code_mapping_inventory()
        else:
            self.list_h5_name()

    def display_h5_inventory(self, event):
        self.clear_frame_content()
        h5_name = self.lstbxCodeSelection.GetStringSelection()
        CodeCalculation = CIC(self.__class__.bu_name)
        [inventory_list, inventory_total] = CodeCalculation.get_h5_inv_detail(h5_name, self.table_to_use)
        self.show_inventory_list(inventory_list, 3)
        self.StatusBar.SetStatusText("Total Inventory: %s" % ("{:,.0f}".format(inventory_total)), 1)
        self.txtLog.Clear()
        self.txtLog.write("%s has been listed" % h5_name)

    def display_code_mapping_inventory(self):
        # get code list and newest timing to mapping
        code_name_input = self.txtMaterialCode.Value.split()
        code_name_list = []
        for item in code_name_input:
            code_name_list.append(item.upper())
        # show in code list
        self.lstbxCodeSelection.Clear()
        for code_item in code_name_list:
            self.lstbxCodeSelection.Append(code_item)
        CodeCalculation = CIC(self.__class__.bu_name)
        inventory_result = CodeCalculation.inventory_mapping(code_name_list, self.table_to_use)
        column_title = ["No", ] + inventory_result[0]
        for i in range(0, len(column_title)):
            self.listCtrlOutput.InsertColumn(i, column_title[i])
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                str_output = "{:,.0f}".format(inventory_result[i][j]) if j > 3 else str(inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j + 1, str_output)
        self.txtLog.write("Done, with data of %s." % self.table_to_use)

    def list_h5_name(self):
        self.txtLog.write("Display H5 Inventory")
        h5_name_hint = self.txtMaterialCode.Value
        h5_name_list = pb_func.get_available_h5_list(h5_name_hint, self.__class__.bu_name)
        self.lstbxCodeSelection.Clear()
        for item in h5_name_list:
            self.lstbxCodeSelection.Append(item)

    def get_current_inventory_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 1
        CodeCalculation = CIC(self.__class__.bu_name)
        [inventory_result, total_inventory] = CodeCalculation.get_current_inventory(self.table_to_use)
        self.show_inventory_list(inventory_result, data_trigger_point)
        self.StatusBar.SetStatusText("Total Available Stock: %s, Total Useful Stock: %s."
                                     % ("{:,.0f}".format(total_inventory[0]), "{:,.0f}".format(total_inventory[1])), 1)
        self.txtLog.Clear()
        self.txtLog.write("Current Inventory List done, with data of %s." % self.table_to_use)

    def get_current_bo_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 4
        CodeCalculation = CIC(self.__class__.bu_name)
        inventory_result = CodeCalculation.get_current_bo(self.table_to_use)
        [backorder_total_qty, backorder_total_value] = inventory_result[-1][4:6]
        self.show_inventory_list(inventory_result, data_trigger_point)
        self.txtLog.write("Current Backorder List done, with data of %s." % self.table_to_use)
        self.StatusBar.SetStatusText("Total Backorder Qty; %s, Value: %s" %
                                     ("{:,.0f}".format(backorder_total_qty), "{:,.0f}".format(backorder_total_value)), 1)

    def display_aging_backorder(self, event):
        self.clear_frame_content()
        CodeCalculation = CIC(self.__class__.bu_name)
        # set exception list with abnormal backorder information
        exception_list = pb_func.get_exception_list(self.__class__.bu_name, "Aging_Backorder")
        self.txtLog.Clear()
        self.txtLog.write("Calculation ongoing, please wait a moment...")
        [inventory_result, mapping_days] = CodeCalculation.calculate_aging_backorder(exception_list)
        data_trigger_point = 6
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
            self.txtLog.write("Done. %s days succeed, %s days fail. Update to %s" %
                              (sync_result[0], sync_result[1], sync_result[2]))

    # export one-day JNJ inventory detail list
    def export_inventory(self, event):
        self.clear_frame_content()
        self.txtLog.write("Start to export. Please wait~")
        CodeCalculation = CIC(self.__class__.bu_name)
        inventory_file = CodeCalculation.export_inventory_data(self.table_to_use)
        self.clear_frame_content()
        if inventory_file:
            self.txtLog.write("Done, Inventory detail exported to %s." % inventory_file)
        else:
            self.txtLog.write("Error. No data in that day, please choose the correct date")

    # export one-day backorder detail
    def export_backorder(self, event):
        self.clear_frame_content()
        self.txtLog.write("Start to export. Please wait~")
        CodeCalculation = CIC(self.__class__.bu_name)
        inventory_file = CodeCalculation.export_backorder_data(self.table_to_use)
        self.clear_frame_content()
        if inventory_file:
            self.txtLog.write("Done, Backorder detail exported to %s." % inventory_file)
        else:
            self.txtLog.write("Error. No data in that day, please choose the correct date")

    # display code trend
    def display_code_trend(self, event):
        self.clear_frame_content()
        code_name = self.lstbxCodeSelection.GetStringSelection()
        self.txtLog.write("Inventory Trend of %s is under generating. Please wait~" % code_name)
        CodeCalculation = CIC(self.__class__.bu_name)
        CodeCalculation.generate_code_inv_trend(code_name)
        self.clear_frame_content()
        self.txtLog.write("Done. The chart would be opened in your web browser.")

    # display h5 trend
    def display_h5_trend(self, event):
        self.clear_frame_content()
        h5_name = self.lstbxCodeSelection.GetStringSelection()
        self.txtLog.write("Inventory Trend of %s is under generating. Please wait~" % h5_name)
        CodeCalculation = CIC(self.__class__.bu_name)
        CodeCalculation.generate_h5_inventory_trend(h5_name)
        self.clear_frame_content()
        self.txtLog.write("Done. The chart would be opened in your web browser.")
        pass

    # click bu total option
    def bu_level_selected(self, event):
        self.clear_all_content()
        bu_level_status = self.chkbxWholeBU.GetValue()
        if bu_level_status:
            self.txtMaterialCode.Disable()
            self.txtLog.write("BU Level of %s is selected" % self.__class__.bu_name)
            self.lstbxCodeSelection.Append("ALL")
            self.lstbxCodeSelection.SetSelection(0)
        else:
            self.txtMaterialCode.Enable()
            self.txtLog.write("BU Level of %s is unselected" % self.__class__.bu_name)

    # display pending inventory
    def display_pending_inventory(self, event):
        self.clear_frame_content()
        CodeCalculation = CIC(self.__class__.bu_name)
        self.txtLog.write("Generating pending inventory trend. Please wait~")
        CodeCalculation.generate_pending_trend()
        self.txtLog.Clear()
        self.txtLog.write("Done. The chart would be opened in your web browser.")
        pass

    # clear input area:
    def clear_input(self, event):
        self.txtMaterialCode.Clear()
        self.lstbxCodeSelection.Clear()
        self.txtLog.Clear()
        self.listCtrlOutput.ClearAll()

    def clear_frame_content(self):
        self.listCtrlOutput.ClearAll()
        self.txtLog.Clear()
        self.StatusBar.SetStatusText(" ", 1)

    def clear_all_content(self):
        self.listCtrlOutput.ClearAll()
        self.lstbxCodeSelection.Clear()
        self.txtMaterialCode.Clear()
        self.txtLog.Clear()
        self.StatusBar.SetStatusText(" ", 1)

    # show about dialog
    def show_about_dialog(self, event):
        DragonDialog(self).Show()

    # close program
    def exit_dragon(self, event):
        self.Close(True)


#
class DragonDialog(dlgAbout):

    def close_about_dialog(self, event):
        self.Close(True)


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    DragonGUI(None).Show()
    app.MainLoop()
