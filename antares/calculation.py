import sqlite3
import time
import public_function as pb_fnc
import pandas as pd
import numpy as np


class InfoCheck:
    bu_name = ""
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # get all master data of single code
    def get_single_code_all_master_data(self, material_code, master_data_item_list):
        str_master_data = ','.join(master_data_item_list)
        database_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        datasheet_name = self.__class__.bu_name + "_Master_Data"
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        sql_cmd = 'SELECT %s FROM %s WHERE Material=\"%s\"' % (str_master_data, datasheet_name, material_code)
        c.execute(sql_cmd)
        result = c.fetchall()
        if result:
            return list(result[0])
        else:
            return 0

    # 读取单个代码全部的master data
    def get_master_data(self, code):
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + "Master_Data.db"
        # 表格名称，等于文件名称
        table_name = "MATERIAL_MASTER"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT Description, Chinese_Description, Hierarchy_4, Hierarchy_5, Sales_Status, Purchase_Status, " \
                  "Standard_Cost FROM " + table_name + " WHERE Material = \'" + code + "\' "
        c.execute(str_cmd)
        row = c.fetchall()
        list_title = ["Description", "Chinese_Description", "Hierarchy_4", "Hierarchy_5", "Sales_Status",
                      "Purchase_Status", "Standard_Cost"]
        return [list_title, list(row[0])]

    # 读取全部的master data list
    def get_master_data_list(self):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        result = c.execute("SELECT * from " + tbl_name)
        row = result.fetchall()
        conn.close()
        return list(row)

    # get master data for code list, phase out
    # def get_master_data_for_list(self, code_list, master_data_name):
    #     file_name = self.__class__.bu_name + "_Master_Data" if master_data_name == "SAP_Price" else "Master_Data"
    #     db_fullname = self.__class__.db_path + file_name + ".db"
    #     table_name = self.__class__.bu_name + "_SAP_Price" if master_data_name == "SAP_Price" else "MATERIAL_MASTER"
    #     master_data_result = []
    #     conn = sqlite3.connect(db_fullname)
    #     c = conn.cursor()
    #     for code_name in code_list:
    #         if master_data_name == "SAP_Price":
    #             sql_cmd = "SELECT Price FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
    #         else:
    #             sql_cmd = "SELECT " + master_data_name + " FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
    #         c.execute(sql_cmd)
    #         master_data_output = c.fetchall()
    #         if master_data_output:
    #             master_data_result.append(master_data_output[0][0])
    #         else:
    #             master_data_result.append(0)
    #     return master_data_result

    # get single column from bu master data
    def get_bu_master_data(self, code, column_name):
        file_name = self.__class__.bu_name + "_Master_Data"
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = 'SELECT %s FROM %s WHERE Material = \"%s\"' % (column_name, file_name, code)
        c.execute(sql_cmd)
        md_result = c.fetchall()
        if md_result:
            return md_result[0][0]
        else:
            return ""

    # by H5的销量数据
    def get_h5_sales_data(self, data_type, price_type, hierarchy, month_number):
        # 文件名，无后缀
        tbl_name = self.__class__.bu_name + "_" + data_type
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # 创建命令
        if price_type == "Standard_Cost":
            if hierarchy == "ALL":
                str_cmd = "SELECT month, sum(Value_Standard_Cost) from " + tbl_name + " GROUP BY month ORDER BY month"
            else:
                str_cmd = "SELECT month, sum(Value_Standard_Cost) from " + tbl_name + " WHERE Hierarchy_5 = '" + \
                      hierarchy + "\' COLLATE NOCASE GROUP BY month ORDER BY month"
        else:
            if hierarchy == "ALL":
                str_cmd = "SELECT month, sum(Value_SAP_Price) from " + tbl_name + " GROUP BY month ORDER BY month"
            else:
                str_cmd = "SELECT month, sum(Value_SAP_Price) from " + tbl_name + " WHERE Hierarchy_5 = \'" + \
                      hierarchy + "\' COLLATE NOCASE GROUP BY month ORDER BY month"
        c.execute(str_cmd)
        sales_result = self.data_mapping(c.fetchall(), pb_fnc.get_current_month(), 0 - month_number)
        return sales_result
    
    def get_h5_inventory_data(self, inv_type, price_type, h5_name, month_number):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_" + inv_type + "_INV"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        if h5_name == "ALL":
            str_cmd = "SELECT month, SUM(Value_%s) from %s GROUP BY month" % (price_type, tbl_name)
        else:
            str_cmd = "SELECT month, SUM(Value_%s) from %s WHERE Hierarchy_5 = \"%s\" COLLATE NOCASE " \
                      "GROUP BY month " % (price_type, tbl_name, h5_name)
        c.execute(str_cmd)
        h5_inv_result = self.data_mapping(c.fetchall(), pb_fnc.get_current_month(), 0 - month_number)
        return h5_inv_result

    # get sap_price by code
    def get_code_sap_price(self, code_name):
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        c.execute("SELECT Price FROM " + table_name + " WHERE Material = \'" + code_name + "\'")
        sap_price_result = c.fetchall()
        if not sap_price_result:
            return 0
        else:
            return sap_price_result[0][0]

    # get gtin by code
    def get_code_gtin(self, code_name):
        db_fullname = self.__class__.db_path + "Master_Data.db"
        filename = "GTIN"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        c.execute("SELECT Barcode from " + filename + " WHERE [Material code] = \'" + code_name + "\'")
        return c.fetchall()[0][0]

    # get RAG by code
    def get_code_rag(self, code_name):
        db_fullname = self.__class__.db_path + "Master_Data.db"
        filename = "RAG_Report"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        c.execute("SELECT REGLICNO, REGAPDATE, REGEXDATE from " + filename + " WHERE MATNR = \'" + code_name +
                  "\' ORDER by REGAPDATE")
        return c.fetchall()

    # get Phoenix Project Status by code
    def get_code_phoenix_result(self, material_code):
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        filename = "TU_Phoenix_List"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT Month, [Target SKU] FROM " + filename + " WHERE [Exit SKU] = \'" + material_code + "\'"
        c.execute(sql_cmd)
        phoenix_result = c.fetchall()
        phoenix_title = ["Phoenix Status", "Stop Manufacturing Date", "Target SKU"]
        if len(phoenix_result) == 0:
            return [["Phoenix Status"], ["N"]]
        else:
            return [phoenix_title, ["Y"] + list(phoenix_result[0])]
        pass

    # by code的销量数据
    def get_code_sales(self, data_type, code, month_number):
        # 文件名，无后缀
        tbl_name = self.__class__.bu_name + "_" + data_type
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(quantity) from " + tbl_name + " WHERE material = \'" + code \
                  + "\' GROUP BY month ORDER BY month"
        c.execute(str_cmd)
        sales_result = self.data_mapping(c.fetchall(), pb_fnc.get_current_month(), 0 - month_number)
        conn.close()
        return sales_result

    # get inventory data by code
    # inventory_type: "JNJ", "LP", month_number: positive integer
    def get_code_inventory(self, material_code, inventory_type, month_number):
        tbl_name = self.__class__.bu_name + "_" + inventory_type + "_INV"
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        stock_column_name = 'Available_Stock' if inventory_type == 'JNJ' else 'quantity'
        sql_cmd = 'SELECT month, SUM(%s) FROM %s WHERE Material = \"%s\" GROUP BY month ' \
                  'ORDER BY month' % (stock_column_name, tbl_name, material_code)
        c.execute(sql_cmd)
        inventory_result = self.data_mapping(c.fetchall(), pb_fnc.get_current_month(), 0 - month_number)
        return inventory_result

    # calculate inventory month
    @staticmethod
    def get_inventory_month(lst_inv, lst_sales, month_number, blank_type=0):
        # set blank value as None if blank_type is 1, else set zero
        lst_inv_month = []
        # leave previous 6 month in blank
        for i in range(0, 6):
            lst_inv_month.append(0) if blank_type == 0 else lst_inv_month.append(None)
        for i in range(0, month_number-6):
            if sum(lst_sales[i: i+6]) == 0:
                lst_inv_month.append(0) if blank_type == 0 else lst_inv_month.append(None)
            else:
                lst_inv_month.append(round(lst_inv[i+6] / (sum(lst_sales[i: i+6])/6), 1))
        return lst_inv_month

    # Generate month list.
    # The previous month list does not include current month.
    # The future month list include current month.
    @staticmethod
    def get_time_list(start_point, parameter):
        # Get month list in format YYYY-MM (start_point)
        # parameter, the month list we need to generate
        start_year, start_month = int(start_point[0:4]), int(start_point[-2:])
        month_list = []
        lower_limit = parameter if parameter <= 0 else 0
        upper_limit = parameter if parameter > 0 else 0
        for i in range(lower_limit, upper_limit):
            t = (start_year, start_month + i, 14, 3, 6, 3, 6, 0, 0)
            month_list.append(time.strftime("%Y-%m", time.localtime(time.mktime(t))))
        return month_list

    # 将数据与指定月份mapping
    def data_mapping(self, data, start_month, months):
        month_list = self.get_time_list(start_month, months)
        result_value = []
        for item_month in month_list:
            value = 0
            for item_value in data:
                if item_value[0] == item_month:
                    value = item_value[1]
            result_value.append(value)
        return result_value

    # get forecast of single code, set fcst_type as Statistical or Final
    def get_code_forecast(self, code_name, fcst_type, month_quantity):
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_" + fcst_type + "_Forecast.db"
        # get month list and generate blank dataframe
        current_month = time.strftime("%Y-%m", time.localtime())
        month_list = self.get_time_list(current_month, month_quantity)
        df_forecast_final = pd.DataFrame(index=month_list)
        # connect to forecast database
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get the newest table
        c.execute("SELECT name from sqlite_master where type = \"table\" ORDER by name DESC")
        tbl_name = c.fetchone()[0]
        # get pivot table of forecast
        sql_cmd = 'SELECT Month, Quantity FROM %s WHERE Material =\"%s\"' % (tbl_name, code_name)
        df_forecast = pd.read_sql(con=conn, sql=sql_cmd, index_col='Month')
        # join the two dataframe to mapping
        df_forecast_final = df_forecast_final.join(df_forecast)
        df_forecast_final.fillna(0, inplace=True)
        output = [item[0] for item in df_forecast_final.values.tolist()]
        return [month_list, output]

    # get forecast of one hierarchy with pandas, set forecast_type as Statistical or Final
    def get_h5_forecast(self, h5_name, forecast_type, month_quantity):
        # Get future month list
        current_month = time.strftime("%Y-%m", time.localtime())
        month_list = self.get_time_list(current_month, month_quantity)
        df_forecast_result = pd.DataFrame(index=month_list, data=None)
        # get forecast data
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_" + forecast_type + "_Forecast.db"
        conn = sqlite3.connect(db_fullname)
        sql_cmd = 'SELECT name from sqlite_master where type = \"table\" ORDER by name DESC LIMIT 1'
        df_table_list = pd.read_sql(sql=sql_cmd, con=conn)
        table_name = df_table_list.values.tolist().pop().pop()
        # get newest table
        if h5_name.upper() == "ALL":
            sql_cmd = 'SELECT Month, sum(Value_SAP_Price) FROM %s GROUP by Month Order by Month' % (table_name, )
        else:
            sql_cmd = 'SELECT Month, sum(Value_SAP_Price) FROM %s WHERE Hierarchy_5 = \"%s\" ' \
                      'GROUP by Month Order by Month' % (table_name, h5_name)
        df_forecast = pd.read_sql(sql=sql_cmd, con=conn, index_col='Month')
        # get value and change to float
        df_forecast_result = df_forecast_result.join(df_forecast)
        df_forecast_result.fillna(0, inplace=True)
        list_forecast_result = [item[0] * 1.0 for item in df_forecast_result.values.tolist()]
        return list_forecast_result

    # get eso result for one code or one hierarchy_5
    def get_material_eso(self, material_name, eso_type="code", cycle_qty=8):
        print("==  ESO Trend of %s  ==" % material_name)
        eso_file = self.__class__.bu_name + "_ESO"
        db_fullname = self.__class__.db_path + eso_file + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get month count
        c.execute('SELECT count(distinct(Month)) FROM TU_ESO')
        offset_value = c.fetchall()[0][0] - cycle_qty
        # get eso list
        if eso_type == "code":
            sql_cmd = "SELECT Month, Excess_Quantity, Slow_Moving_Quantity, Obsolete_Quantity, Total_ESO_Quantity, " \
                      "Total_ESO_Value FROM %s  WHERE Material = \'%s\' ORDER BY Month LIMIT %s OFFSET %s" \
                      % (eso_file, material_name, str(cycle_qty), str(offset_value))
        else:
            if material_name.upper() != "ALL":
                sql_cmd = "SELECT Month, sum(NPI_Reverse_Value), sum(Total_ESO_Value) FROM %s " \
                          "WHERE Hierarchy_5 = \'%s\' COLLATE NOCASE GROUP by Month, Hierarchy_5 ORDER BY Month " \
                          "LIMIT %S OFFSET %s" % (eso_file, material_name, str(cycle_qty), str(offset_value))
            else:
                sql_cmd = "SELECT Month, sum(NPI_Reverse_Value), sum(Total_ESO_Value) FROM %s GROUP by Month " \
                          "ORDER BY Month LIMIT %s OFFSET %s" % (eso_file, str(cycle_qty), str(offset_value))
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            print("!!Error! No such code, please check your input!")
            return
        eso_result = c.fetchall()
        return eso_result


if __name__ == "__main__":
    info_check = InfoCheck("TU")
    # info_check.generate_abc_ranking()
    # info_check.get_code_phoenix_result("689.893")
    info_check.get_material_eso(material_name='ALL', eso_type='h5')



