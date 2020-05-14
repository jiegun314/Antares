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

    def get_all_master_data(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        datasheet_name = self.__class__.bu_name + '_Master_Data_Demo'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = "SELECT * FROM " + datasheet_name
        df = pd.read_sql(sql=sql_cmd, con=conn)
        # code_list = df['Material'].values.tolist()
        return df

    # Return all the sales data
    def get_code_sales_list(self, sales_type, month_list):
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item + '\",'
        str_month_list = str_month_list.rstrip(',')
        file_name = self.__class__.bu_name + "_" + sales_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        sql_cmd = "SELECT Material, Month, Quantity, Value_Standard_Cost, Value_SAP_Price from " + file_name + \
                  " WHERE Month IN (" + str_month_list + ") GROUP by Material, Month Order by Month"
        df = pd.read_sql(sql=sql_cmd, con=conn)
        conn.commit()
        conn.close()
        return df

    # Return all the Inventory Data
    def get_code_inventory_list(self, inv_type, month_list):
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item + '\",'
        str_month_list = str_month_list.rstrip(',')
        file_name = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        if inv_type == "JNJ_INV":
            sql_cmd = "SELECT Material, Month, sum(Available_Stock) as Quantity, " \
                      "sum(Value_Standard_Cost) as Value_Standard_Cost, sum(Value_SAP_Price) as Value_SAP_Price FROM " \
                      + file_name + " WHERE Month IN (" + str_month_list + ") GROUP BY Material, Month ORDER BY Month"
        else:
            sql_cmd = "SELECT Material, Month, sum(Quantity) as Quantity, " \
                      "sum(Value_Standard_Cost) as Value_Standard_Cost, sum(Value_SAP_Price) as Value_SAP_Price from " \
                      + file_name + " WHERE Month IN (" + str_month_list + ") GROUP BY Material, Month ORDER BY Month"
        df = pd.read_sql(sql=sql_cmd, con=conn)
        conn.commit()
        conn.close()
        return df

    # Return recent ESO result of 2 cycle.
    def get_code_eso_list(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_ESO.db'
        datasheet_name = self.__class__.bu_name + '_ESO'
        # get recent 2 cycle.
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 2'
        c = conn.cursor()
        c.execute(sql_cmd)
        month_list = c.fetchall()
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item[0] + '\",'
        str_month_list = str_month_list.rstrip(',')
        # get ESO result of most recent 2 cycles.
        sql_cmd = 'SELECT * FROM ' + datasheet_name + ' WHERE Month IN (' + str_month_list + ")"
        df_eso = pd.read_sql(sql=sql_cmd, con=conn)
        df_eso_result = pd.pivot_table(df_eso, index='Material',
                                       values=['Excess_Quantity', 'Slow_Moving_Quantity', 'Obsolete_Quantity',
                                               'ESO_Quantity', 'ESO_Value_Standard_Cost'],
                                       columns="Month", fill_value=0)
        return df_eso_result

    def get_sales_data(self):
        # Get Month list
        time_start = time.time()
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -24)
        # initiate column name list
        # Get active code list
        df_material_master = self.get_all_master_data()
        lst_column_name = list(df_material_master)
        list_material_master = df_material_master.values.tolist()
        active_code_list = df_material_master['Material'].values.tolist()
        print("Data Length:", len(active_code_list))
        # Get eso_result
        df_eso_result = self.get_code_eso_list()
        lst_column_name += [item[0] + "-" + item[1] for item in list(df_eso_result)]
        # Generate sales type list
        sales_type = ["GTS", "LPSales", "IMS"]
        lst_sales_df = []
        for sales_type_item in sales_type:
            df = self.get_code_sales_list(sales_type_item, month_list)
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            # print(len(list(pivot_result)))
            print(sales_type_item, " is ready!")
            lst_column_name += [sales_type_item + "-" + item[0] + "-" + item[1] for item in list(pivot_result)]
            lst_sales_df.append(pivot_result)
        # Generate inventory type list
        inventory_type = ["JNJ_INV", "LP_INV"]
        lst_inv_df = []
        for inv_type_item in inventory_type:
            df = self.get_code_inventory_list(inv_type_item, month_list)
            # Generate pivot_table
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            print(inv_type_item, " is ready!")
            lst_column_name += [inv_type_item + "-" + item[0] + "-" + item[1] for item in list(pivot_result)]
            lst_inv_df.append(pivot_result)
        # Get sales result of single code
        snop_result = []
        for code_item in list_material_master:
            # initiate blank list
            code_name = code_item[0]
            # load master data
            code_output = code_item
            # load eso
            try:
                code_eso_result = df_eso_result.loc[code_name]
            except KeyError:
                code_output.extend([x * 0 for x in range(0, len(df_eso_result.columns))])
            else:
                code_output.extend(code_eso_result.values.tolist())
            # Load sales data
            for sales_item_df in lst_sales_df:
                try:
                    code_result = sales_item_df.loc[code_name]
                except KeyError:
                    code_output.extend([x * 0 for x in range(0, len(sales_item_df.columns))])
                else:
                    code_output.extend(code_result.values.tolist())
            # Load inventory data
            for inv_item_df in lst_inv_df:
                try:
                    code_result = inv_item_df.loc[code_name]
                except KeyError:
                    # Alert! the zero input should be same quantity as available inventory month
                    code_output.extend([x * 0 for x in range(0, len(inv_item_df.columns))])
                else:
                    code_output.extend(code_result.values.tolist())
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
        df.to_excel(file_fullname, sheet_name="Code", index=False, header=lst_column_name, freeze_panes=(1, 1))
        print('Done~')


if __name__ == '__main__':
    TestModule = SNOPExportV2("TU")
    TestModule.get_sales_data()
    # TestModule.get_code_eso_list()
