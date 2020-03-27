import sqlite3
# import pandas as pd
# import numpy as np
from tabulate import tabulate
import draw_chart as chart
import os
import calculation
import pandas as pd


class CurrentInventoryBackorder:
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    currency_rate = 7.0842

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # calculate long aging backorders
    def calculate_aging_backorder(self):
        # print title
        print("===Display Aging Backorder===")
        # get table list
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name DESC")
        table_list = [item[0] for item in c.fetchall()]
        current_day_table = table_list.pop(0)
        # get newest backorder
        sql_cmd = "SELECT Material FROM " + current_day_table + " WHERE Current_Backorder_Qty > 0"
        c.execute(sql_cmd)
        backorder_code_list = [item[0] for item in c.fetchall()]
        # set up tracing list with code, backorder days, open_status
        print("---Start to map backorder historical data---")
        backorder_tracing_list = []
        for item in backorder_code_list:
            backorder_tracing_list.append([item, 1, "Y"])
        # trace back for backorder
        for table_item in table_list:
            for code_item in backorder_tracing_list:
                if code_item[2] == "Y":
                    sql_cmd = "SELECT Current_Backorder_Qty FROM " + table_item + " WHERE Material = \'" \
                              + code_item[0] + "\'"
                    c.execute(sql_cmd)
                    backorder_result = c.fetchall()
                    backorder_qty = backorder_result[0][0] if backorder_result else 0
                    # if the backorder qty is positive, just add count for days, else remove from counting list
                    if backorder_qty > 0:
                        code_item[1] += 1
                    else:
                        code_item[2] = "N"
            # print("Backorder mapping of %s - Done." % table_item)
            print(">", end="", flush=True)
        backorder_tracing_list.sort(key=self.take_quantity, reverse=True)
        print("")
        print("---Start to generate result---")
        # get current day information
        backorder_output = []
        for backorder_item in backorder_tracing_list:
            sql_cmd = "SELECT Description, Hierarchy_5, CSC, Current_Backorder_Qty, " \
                  "sum(GIT_1_Week + GIT_2_Week + GIT_3_Week + GIT_4_Week) as GIT_Qty, Open_PO FROM " +  \
                  current_day_table + " WHERE Material = \'" + backorder_item[0] + "\'"
            c.execute(sql_cmd)
            result_temp = list(c.fetchall()[0])
            backorder_output.append([backorder_item[0], ] + result_temp + [backorder_item[1], ])
        # print out
        return backorder_output

    # display aging backorder list
    def display_aging_backorder(self):
        aging_backorder_list = self.calculate_aging_backorder()
        list_header = [["Material", "Description", "Hierarchy_5", "CSC", "BO Qty", "GIT Qty", "Open PO", "BO Days"], ]
        aging_backorder_output = list_header + aging_backorder_list
        print(tabulate(aging_backorder_output, headers="firstrow", tablefmt="psql"))

    def take_quantity(self, elem):
        return elem[1]


if __name__ == "__main__":
    test = CurrentInventoryBackorder("TU")
    test.display_aging_backorder()
