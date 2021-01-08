from gui_design import DragonFrame, dlgAbout
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC
from crt_inv_calculation import TraumaCurrentInventoryCalculation as TU_CIC
import public_function as pb_func
import pandas as pd
import os


class DragonGUI(DragonFrame):
    bu_name = ""
    table_to_use = ""

    def __init__(self, parent):
        DragonFrame.__init__(self, parent)
        # set TU as default BU
        self.__class__.bu_name = "TU"
        self._set_calculation_module()
        self.display_bu_update()
        # set ICON
        self.icon = wx.Icon(u'.icon/logo.png', wx.BITMAP_TYPE_PNG)
        self.SetIcon(self.icon)
        # set default as today
        self.chkbxToday.SetValue(1)
        self.dtpkDate.Disable()
        self.set_db_table("newest")

    # choose the right class to load
    def _set_calculation_module(self):
        if self.__class__.bu_name == 'TU':
            self.calculation_module = TU_CIC()
        else:
            self.calculation_module = CIC(self.__class__.bu_name)

    def set_bu_name(self, bu_name):
        self.__class__.bu_name = bu_name

    def _reset_bu(self):
        self._set_calculation_module()
        self.display_bu_update()
        # update current date to CMF
        self.set_db_table("newest")

    def select_bu_CMFT(self, event):
        self.__class__.bu_name = "CMF"
        self._reset_bu()

    def select_bu_TU(self, event):
        self.__class__.bu_name = "TU"
        self._reset_bu()

    def select_bu_PT(self, event):
        self.__class__.bu_name = "PT"
        self._reset_bu()

    def select_bu_JT(self, event):
        self.__class__.bu_name = "JT"
        self._reset_bu()

    def select_bu_MT(self, event):
        self.__class__.bu_name = "MT"
        self._reset_bu()

    def select_bu_SP(self, event):
        self.__class__.bu_name = "Spine"
        self._reset_bu()

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
        date_to_check = self.dtpkDate.GetValue().Format("%Y%m%d")
        self.set_db_table(date_to_check)
        self.txtLog.Clear()
        self.txtLog.AppendText("%s would be used." % date_to_check)

    # define the table for calculation in datepicker
    def set_db_table(self, date):
        self.table_to_use = self.calculation_module.get_newest_date() if date == "newest" else "INV" + date

    # Virtual event handlers, override them in your derived class
    def codeSubmit(self, event):
        # clean the column
        self.clear_frame_content()
        calculation_type = self.rdbxCalculationType.GetStringSelection()
        if calculation_type == "Code":
            self.display_code_mapping_inventory()
        else:
            self.list_h5_name()

    def display_h5_inventory(self, event):
        self.clear_frame_content()
        if self.rdbxCalculationType.GetStringSelection() == "Code":
            return
        h5_name = self.lstbxCodeSelection.GetStringSelection()
        [inventory_list, inventory_total] = self.calculation_module.get_h5_inv_detail(h5_name, self.table_to_use)
        self.show_list(inventory_list, 3)
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
        if self.__class__.bu_name == 'TU':
            inventory_result = self.calculation_module.inventory_mapping_with_ned_inv(code_name_list, self.table_to_use)
        else:
            inventory_result = self.calculation_module.inventory_mapping(code_name_list, self.table_to_use)
        data_trigger_point = 4
        self.show_list(inventory_result, data_trigger_point)
        self.txtLog.write("Done, with data of %s." % self.table_to_use)

    def list_h5_name(self):
        self.txtLog.write("Display H5 Inventory")
        h5_name_hint = self.txtMaterialCode.Value.split('\n').pop(0).strip(' ')
        h5_name_list = pb_func.get_available_h5_list(h5_name_hint, self.__class__.bu_name)
        self.lstbxCodeSelection.Clear()
        for item in h5_name_list:
            self.lstbxCodeSelection.Append(item)

    def get_current_inventory_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 1
        [inventory_result, total_inventory] = self.calculation_module.get_current_inventory(self.table_to_use)
        self.show_list(inventory_result, data_trigger_point)
        self.StatusBar.SetStatusText("Total Available Stock: %s, Total Useful Stock: %s."
                                     % ("{:,.0f}".format(total_inventory[0]), "{:,.0f}".format(total_inventory[1])), 1)
        self.txtLog.Clear()
        self.txtLog.write("Current Inventory List done, with data of %s." % self.table_to_use)

    def get_current_bo_list(self, event):
        self.clear_frame_content()
        data_trigger_point = 4
        inventory_result = self.calculation_module.get_current_bo(self.table_to_use)
        [backorder_total_qty, backorder_total_value] = inventory_result[-1][4:6]
        self.show_list(inventory_result, data_trigger_point)
        self.txtLog.write("Current Backorder List done, with data of %s." % self.table_to_use)
        self.StatusBar.SetStatusText("Total Backorder Qty; %s, Value: %s" %
                                     ("{:,.0f}".format(backorder_total_qty), "{:,.0f}".format(backorder_total_value)),
                                     1)

    def display_backorder_trend(self, event):
        self.clear_frame_content()
        self.txtLog.write("Generating backorder trend. Please wait~")
        self.calculation_module.generate_backorder_trend()
        self.txtLog.Clear()
        self.txtLog.write("Done. The chart would be opened in your web browser.")

    def display_aging_backorder(self, event):
        self.clear_frame_content()
        # set exception list with abnormal backorder information
        exception_list = pb_func.get_exception_list(self.__class__.bu_name, "Aging_Backorder")
        self.txtLog.Clear()
        self.txtLog.write("Calculation ongoing, please wait a moment...")
        [inventory_result, mapping_days] = self.calculation_module.generate_aging_backorder_list(exception_list)
        data_trigger_point = 6
        self.show_list(inventory_result, data_trigger_point)
        self.StatusBar.SetStatusText("Total Mapping %s days" % ("{:,.0f}".format(mapping_days)), 1)
        self.txtLog.Clear()
        self.txtLog.write("Aging backorder calculation finished.")

    # shared function to display data in column list
    def show_list(self, inventory_result, data_trigger_point):
        column_title = ["No", ] + list(inventory_result[0])
        for i in range(0, len(column_title)):
            if i <= data_trigger_point:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_LEFT)
            else:
                self.listCtrlOutput.InsertColumn(i, column_title[i], wx.LIST_FORMAT_RIGHT)
        for i in range(1, len(inventory_result)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            for j in range(0, len(inventory_result[i])):
                if j >= data_trigger_point:
                    # replace 0 with "-" for numbers
                    str_output = "-" if inventory_result[i][j] == 0 else "{:,.0f}".format(inventory_result[i][j])
                else:
                    str_output = str(inventory_result[i][j])
                self.listCtrlOutput.SetItem(index, j + 1, str_output)

    def click_item_in_list(self, event):
        self.txtLog.Clear()
        selected_row = self.listCtrlOutput.GetFocusedItem()
        column_length = self.listCtrlOutput.GetColumnCount()
        lst_column_name = []
        # get column name
        for i in range(column_length):
            lst_column_name.append(self.listCtrlOutput.GetColumn(i).Text)
        if 'Material' in lst_column_name:
            material_code_index = lst_column_name.index('Material')
            selected_code = self.listCtrlOutput.GetItem(selected_row, material_code_index).Text
            self.txtLog.write("Inventory Trend of %s is under generating. Please wait~" % selected_code)
            self.calculation_module.generate_code_inv_trend(selected_code)
            self.txtLog.Clear()
            self.txtLog.write("Done. The chart for %s would be opened in your web browser." % selected_code)
        elif 'Hierarchy_5' in lst_column_name:
            material_code_index = lst_column_name.index('Hierarchy_5')
            selected_code = self.listCtrlOutput.GetItem(selected_row, material_code_index).Text
            self.txtLog.write("Inventory Trend of %s is under generating. Please wait~" % selected_code)
            self.calculation_module.generate_h5_inventory_trend_two_dimension(selected_code)
            self.txtLog.Clear()
            self.txtLog.write("Done. The chart for %s would be opened in your web browser." % selected_code)
        else:
            self.txtLog.write("No valid code or hierarchy was selected.")

    # export data in control list
    def export_listed_data(self, event):
        column_length = self.listCtrlOutput.GetColumnCount()
        # get column name
        column_data, lst_column_name = [], []
        for i in range(column_length):
            lst_column_name.append(self.listCtrlOutput.GetColumn(i).Text)
        # column_data.append(lst_column_name)
        # get data
        # get data length
        data_length = self.listCtrlOutput.GetItemCount()
        for i in range(data_length):
            data_in_line = []
            for j in range(column_length):
                # convert "-" to 0
                data = self.listCtrlOutput.GetItem(i, j).Text if self.listCtrlOutput.GetItem(i, j).Text != "-" else 0
                data_in_line.append(data)
            column_data.append(data_in_line)
        # convert to dataframe
        # column_data_transpose = [[row[i] for row in column_data] for i in range(len(column_data[0]))]
        df = pd.DataFrame(data=column_data, columns=lst_column_name)
        df.set_index(["No"], inplace=True)
        # open file dialogue
        wildcard = 'Excel文件(*.xlsx)|*.xlsx|所有文件(*.*)|*.*'
        dlg = wx.FileDialog(self, '另存为', os.getcwd(),
                            defaultFile='output.xlsx',
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                            wildcard=wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            df.to_excel(file, index=False)
            dlg.Destroy()
        # df.to_excel("../data/_INV_Export/test.xlsx", index=False)

    def sync_inventory(self, event):
        lst_xcpt = []
        self.clear_frame_content()
        self.txtLog.write("Start to sync. Please wait~")
        sync_result = self.calculation_module.inv_data_sync(90, lst_xcpt)
        if sync_result == "ERROR":
            self.txtLog.Clear()
            self.txtLog.write("Sync failure. Please make sure you've connected to JNJ network")
        else:
            self.txtLog.Clear()
            self.txtLog.write("Done. %s days succeed, %s days fail. Update to %s" %
                              (sync_result[0], sync_result[1], sync_result[2]))
        # refresh the current date value
        if self.chkbxToday.GetValue():
            self.table_to_use = self.calculation_module.get_newest_date()

    # export one-day JNJ inventory detail list
    def export_inventory(self, event):
        self.clear_frame_content()
        self.txtLog.write("Start to export. Please wait~")
        df = self.calculation_module.export_inventory_data(self.table_to_use)
        self.clear_frame_content()
        default_file_name = self.__class__.bu_name + '_Inventory_' + self.table_to_use[3:] + '.xlsx'
        if isinstance(df, pd.DataFrame):
            # open file dialogue
            wildcard = 'Excel文件(*.xlsx)|*.xlsx|所有文件(*.*)|*.*'
            dlg = wx.FileDialog(self, '另存为', os.getcwd(),
                                defaultFile=default_file_name,
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                wildcard=wildcard)
            if dlg.ShowModal() == wx.ID_OK:
                file = dlg.GetPath()
                df.to_excel(file, index=False)
                dlg.Destroy()
            self.txtLog.write("Done, Inventory detail exported to %s." % file)
        else:
            self.txtLog.write("Error. No data in that day, please choose the correct date")

    # export one-day backorder detail
    def export_backorder(self, event):
        self.clear_frame_content()
        self.txtLog.write("Start to export. Please wait~")
        df = self.calculation_module.export_backorder_data(self.table_to_use)
        self.clear_frame_content()
        default_file_name = self.__class__.bu_name + '_Backorder_' + self.table_to_use[3:] + '.xlsx'
        if isinstance(df, pd.DataFrame):
            # open file dialogue
            wildcard = 'Excel文件(*.xlsx)|*.xlsx|所有文件(*.*)|*.*'
            dlg = wx.FileDialog(self, '另存为', os.getcwd(),
                                defaultFile=default_file_name,
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                                wildcard=wildcard)
            if dlg.ShowModal() == wx.ID_OK:
                file = dlg.GetPath()
                df.to_excel(file, index=False)
                dlg.Destroy()
            self.txtLog.write("Done, Backorder detail exported to %s." % file)
        else:
            self.txtLog.write("Error. No data in that day, please choose the correct date")

    # display inventory trend for both code and h5
    def display_inventory_trend(self, event):
        self.clear_frame_content()
        selected_name = self.lstbxCodeSelection.GetStringSelection()
        if selected_name != '':
            h5_fulllist = pb_func.get_full_h5_list(self.__class__.bu_name)
            self.txtLog.write("Inventory Trend of %s is under generating. Please wait~" % selected_name)
            # if h5 name is selected
            if selected_name in h5_fulllist or selected_name == 'ALL':
                self.calculation_module.generate_h5_inventory_trend_two_dimension(selected_name)
            else:
                self.calculation_module.generate_code_inv_trend(selected_name)
            self.clear_frame_content()
            self.txtLog.write("Done. The chart would be opened in your web browser.")
        else:
            self.txtLog.write("No code or hierarchy_5 was selected. Please try again.")

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
        self.txtLog.write("Generating pending inventory trend. Please wait~")
        self.calculation_module.generate_pending_trend()
        self.txtLog.Clear()
        self.txtLog.write("Done. The chart would be opened in your web browser.")

    # display low AB inventory
    def display_low_AB_inventory(self, event):
        self.clear_frame_content()
        if self.__class__.bu_name != 'TU':
            self.txtLog.write("Sorry, this function is not open for %s yet." % self.__class__.bu_name)
        else:
            df_low_inventory = self.calculation_module.get_low_inventory_alert()
            lst_low_inventory = [['Material'] + df_low_inventory.columns.values.tolist()] + df_low_inventory.reset_index().values.tolist()
            self.show_list(lst_low_inventory, 4)

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
