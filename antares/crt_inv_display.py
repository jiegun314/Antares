import sqlite3
# import numpy as np
from crt_inv_calculation import CurrentInventoryCalculation as CIC
from tabulate import tabulate
import draw_chart as chart
import os
import public_function as pb_func
import pandas as pd


class CurrentInventoryDisplay:
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    source_file_path = "../data/_Source_Data/"
    oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    currency_rate = 7.0842

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def display_code_status(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Single Code Inventory===")
        # 获取日期
        code_name = input("Input Material Code: ").upper()
        # check if this code exist in material master
        while not CodeCalculation.check_code(code_name):
            code_name = input("Wrong code, please re-input: ").upper()
        # start to get inventory data from oneclick database
        str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        # check if this date exist in newest oneclick file
        while not CodeCalculation.check_date_availability(table_name):
            print("!!Error - Wrong date, Please re-input! ")
            str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
            table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        code_inv_output = CodeCalculation.get_code_inv(code_name, table_name)
        print(tabulate(code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="github"))

    def display_mapping_inventory(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Inventory Status Mapping with Lists===")
        # get data file
        file_fullname = self.__class__.source_file_path + "Data_Mapping.txt"
        try:
            fo = open(file_fullname, "r")
        except FileNotFoundError:
            print("!Error, please make sure you have put Data_Mapping.txt under _Source_Data folder")
            return
        code_list = [item.strip() for item in fo.readlines()]
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = CodeCalculation.get_newest_date()
        else:
            table_name = "INV" + inventory_date
        if not CodeCalculation.check_date_availability(table_name):
            print("!Error, please make sure you input the correct date.")
            return
        inventory_result = CodeCalculation.inventory_mapping(code_list, table_name)
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result))))

    def display_h5_inv_detail(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Hierarchy_5 Inventory Detail List===")
        # Get H5 Name
        h5_input = input("Input Hierarchy_5 Name : ")
        h5_name = pb_func.get_available_h5_name(h5_input, self.__class__.bu_name)
        # if not right h5 name, return
        if h5_name == "NULL":
            print("No such Hierarchy_5 name and please try again!~")
            return
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        [inventory_result, total_inv_value] = CodeCalculation.get_h5_inv_detail(h5_name, table_name)
        print("Total Inventory Value of " + h5_name + " is %s" % (format(total_inv_value, ",.0f")))
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result)), floatfmt=",.0f"))

    def display_current_backorder(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Current Backorder List===")
        # 获取日期
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        backorder_result = CodeCalculation.get_current_bo(table_name)
        print(tabulate(backorder_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(backorder_result)), floatfmt=",.0f"))

    # display aging backorder list
    def display_aging_backorder(self):
        # print title
        print("===Display Aging Backorder===")
        # set exception list with abnormal backorder information
        exception_list = ["INV20200330", "INV20200331"]
        CodeCalculation = CIC(self.__class__.bu_name)
        [aging_backorder_list, mapping_days] = CodeCalculation.calculate_aging_backorder(exception_list)
        print("---Aging Backorder List within %s days---" % mapping_days)
        print(tabulate(aging_backorder_list, headers="firstrow", tablefmt="psql"))

    def display_current_inventory(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Current Inventory List by Hierarchy_5===")
        # 获取日期
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        inventory_result, summary_result = CodeCalculation.get_current_inventory(table_name)
        print(tabulate(inventory_result, headers="firstrow", tablefmt="psql",
                       showindex=range(1, len(inventory_result)), floatfmt=",.0f"))
        total_available_stock_value, total_useful_stock_value, total_stock_value = summary_result
        print("Total Available Stock Value: RMB - %s, USD - %s"
              % (format(total_available_stock_value, ",.0f"),
                 format(total_available_stock_value / self.__class__.currency_rate, ",.0f")))
        print("Total Useful Stock Value: RMB - %s, USD - %s"
              % (format(total_useful_stock_value, ',.0f'),
                 format(total_useful_stock_value / self.__class__.currency_rate, ',.0f')))
        print("Total Stock Value: RMB - %s, USD - %s"
              % (format(total_stock_value, ',.0f'), format(total_stock_value / self.__class__.currency_rate, ',.0f')))

    def export_inventory_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        # print title
        print("===Export Inventory Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        inventory_file = CodeCalculation.export_inventory_data(table_name)
        print("Inventory detail exported to " + inventory_file)

    def export_backorder_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        # print title
        print("===Export Backorder Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        backorder_file = CodeCalculation.export_backorder_data(table_name)
        print("Backorder detail exported to " + backorder_file)

    def synchronize_oneclick_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        lst_xcpt = ['20190118', ]
        print("===Sync Current Inventory Data from Oneclick===")
        sync_result = CodeCalculation.inv_data_sync(90, lst_xcpt)
        if sync_result == "Error":
            print("!Error, the sharefolder cannot be opened. Make sure you've connected to JNJ network and try again.")
        else:
            print(">> Synchronization succeed!")
            print(">> %s days succeed, %s days fail" % (sync_result[0], sync_result[1]))


if __name__ == "__main__":
    test = CurrentInventoryDisplay("TU")
    test.display_current_inventory()
    # test.inv_data_sync(50)
