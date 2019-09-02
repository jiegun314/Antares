# Use dict to get general information on code level

import sqlite3
import pandas as pd
import calculation as cclt
import numpy as np
import time


class SNOPExportV2:

    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"
    file_path = "../data/_Source_Data/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # Get active code list
    def get_active_codes(self):
        file_name = self.__class__.bu_name + "_Active_Codes"
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
        print("Start get the active code list")
        df = pd.read_excel(file_fullname, dtype=object)
        # 读取所有元素
        data = df.values
        code_list = []
        for item in data:
            code_list.append(item[0])
        # 测试阶段返回N个数字
        return code_list

    # Return all the sales data
    def get_code_sales_list(self, sales_type):
        file_name = self.__class__.bu_name + "_" + sales_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Month, Quantity, Value_Standard_Cost, Value_SAP_Price from " + file_name + \
                  " GROUP by Material, Month Order by Month"
        c.execute(sql_cmd)
        result = c.fetchall()
        conn.commit()
        conn.close()
        return result

    # Return all the Inventory Data
    def get_code_inventory_list(self, inv_type):
        file_name = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        if inv_type == "JNJ_INV":
            sql_cmd = "SELECT Material, Month, sum(Available_Stock), sum(Value_Standard_Cost), sum(Value_SAP_Price)" \
                      " from " + file_name + " GROUP BY Material, Month ORDER BY Month"
        else:
            sql_cmd = "SELECT Material, Month, sum(Quantity), sum(Value_Standard_Cost), sum(Value_SAP_Price) from " \
                      + file_name + " GROUP BY Material, Month ORDER BY Month"
        result = c.execute(sql_cmd).fetchall()
        conn.commit()
        conn.close()
        return result

    def get_sales_data(self):
        # Get Month list
        time_start = time.time()
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -24)
        # print(month_list)
        # Get active code list
        active_code_list = self.get_active_codes()
        print("Data Length:", len(active_code_list))
        # Generate sales type list
        sales_type = ["GTS", "LPSales", "IMS"]
        lst_sales_df = []
        for sales_type_item in sales_type:
            sales_list = self.get_code_sales_list(sales_type_item)
            # Generate Dict
            df = pd.DataFrame(sales_list)
            df.rename(
                columns={0: "Material", 1: "Month", 2: "Quantity", 3: "Value_Standard_Cost", 4: "Value_SAP_Price"},
                inplace=True)
            # Generate pivot_table
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            print(sales_type_item, " is ready!")
            lst_sales_df.append(pivot_result)
        # Generate inventory type list
        inventory_type = ["JNJ_INV", "LP_INV"]
        lst_inv_df = []
        for inv_type_item in inventory_type:
            inventory_list = self.get_code_inventory_list(inv_type_item)
            # Generate Dict
            df = pd.DataFrame(inventory_list)
            df.rename(
                columns={0: "Material", 1: "Month", 2: "Quantity", 3: "Value_Standard_Cost", 4: "Value_SAP_Price"},
                inplace=True)
            # Generate pivot_table
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            print(inv_type_item, " is ready!")
            lst_inv_df.append(pivot_result)
        # Get sales result of single code
        snop_result = []
        for code_name in active_code_list:
            # initiate blank list
            code_output = [code_name, ]
            # Load sales data
            for sales_item_df in lst_sales_df:
                try:
                    code_result = sales_item_df.loc[code_name, ["Quantity", "Value_Standard_Cost", "Value_SAP_Price"]]
                except KeyError:
                    code_output.extend([x*0 for x in range(0, 24)])
                else:
                    value_type = ["Quantity", "Value_Standard_Cost", "Value_SAP_Price"]
                    for value_type_item in value_type:
                        final_result = code_result.loc[value_type_item, month_list]
                        code_output.extend(final_result.values.tolist())
            # Load inventory data
            for inv_item_df in lst_inv_df:
                try:
                    code_result = inv_item_df.loc[code_name, ["Quantity", "Value_Standard_Cost", "Value_SAP_Price"]]
                except KeyError:
                    # Alert! the zero input should be same quantity as available inventory month
                    code_output.extend([x * 0 for x in range(0, 24)])
                else:
                    value_type = ["Quantity", "Value_Standard_Cost", "Value_SAP_Price"]
                    for value_type_item in value_type:
                        final_result = code_result.loc[value_type_item, month_list]
                        code_output.extend(final_result.values.tolist())
            print(code_name, '-', len(code_output))
            snop_result.append(code_output)
        time_end = time.time()
        print('time cost', int(time_end - time_start), 's')
        # Transfer to array
        array_output = np.array(snop_result)
        df = pd.DataFrame(array_output)
        # Export to Excel
        current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_" + current_time + "_Test.xlsx"
        file_fullname = self.__class__.export_path + file_name
        df.to_excel(file_fullname, sheet_name="Code", index_label="Material")


if __name__ == '__main__':
    TestModule = SNOPExportV2("TU")
    TestModule.get_sales_data()
