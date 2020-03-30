import sqlite3
# import pandas as pd
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


if __name__ == "__main__":
    test = CurrentInventoryDisplay("TU")
    test.display_code_status()
    # test.inv_data_sync(50)