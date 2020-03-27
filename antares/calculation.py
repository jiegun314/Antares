import sqlite3
import time
from tabulate import tabulate


class InfoCheck:
    bu_name = ""
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

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

    # get master data for code list
    def get_master_data_for_list(self, code_list, master_data_name):
        file_name = self.__class__.bu_name + "_Master_Data" if master_data_name == "SAP_Price" else "Master_Data"
        db_fullname = self.__class__.db_path + file_name + ".db"
        table_name = self.__class__.bu_name + "_SAP_Price" if master_data_name == "SAP_Price" else "MATERIAL_MASTER"
        master_data_result = []
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        for code_name in code_list:
            if master_data_name == "SAP_Price":
                sql_cmd = "SELECT Price FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
            else:
                sql_cmd = "SELECT " + master_data_name + " FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
            c.execute(sql_cmd)
            master_data_output = c.fetchall()
            if master_data_output:
                master_data_result.append(master_data_output[0][0])
            else:
                master_data_result.append(0)
        return master_data_result

    # get single column from bu master data
    def get_bu_master_data(self, code, column_name):
        file_name = self.__class__.bu_name + "_Master_Data"
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT " + column_name + " FROM " + file_name + " WHERE Material = \'" + code + "\'"
        c.execute(sql_cmd)
        md_result = c.fetchall()
        if md_result:
            return md_result[0][0]
        else:
            return ""

    # by H5的销量数据
    def get_H5_sales(self, data_type, price_type, hierarchy):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_" + data_type
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
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
        result = c.fetchall()
        return result
    
    def get_H5_hstr_inv(self, inv_type, price_type, h5_name):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_" + inv_type + "_INV"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        if h5_name == "ALL":
            str_cmd = "SELECT month, SUM(Value_" + price_type + ") from " + tbl_name + " GROUP BY month "
        else:
            str_cmd = "SELECT month, SUM(Value_" + price_type + ") from " + tbl_name + " WHERE Hierarchy_5 = \'" \
                  + h5_name + "\' COLLATE NOCASE GROUP BY month "
        h5_inv_result = c.execute(str_cmd).fetchall()
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
        if len(phoenix_result) ==0:
            return ["Non-Phoenix Product", "None", "None"]
        else:
            return ["Phoenix Product", ] + list(phoenix_result[0])
        pass

    # by code的销量数据
    def get_code_sales(self, data_type, code):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_" + data_type
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(quantity) from " + tbl_name + " WHERE material = \'" + code \
                  + "\' GROUP BY month ORDER BY month"
        c.execute(str_cmd)
        result = c.fetchall()
        conn.close()
        return result

    # 获取单个代码的LP库存
    def get_code_lp_inv(self, code):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_LP_INV"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(quantity) from " + tbl_name + " WHERE Material = \'" + code \
                  + "\' GROUP BY month ORDER BY month"
        c.execute(str_cmd)
        result = c.fetchall()
        conn.close()
        return result

    # 获取单个代码的JNJ库存
    def get_code_jnj_inv(self, code):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_JNJ_INV"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(Available_Stock) from " + tbl_name + " WHERE Material = \'" + code \
                  + "\' GROUP BY month ORDER BY month"
        c.execute(str_cmd)
        result = c.fetchall()
        conn.close()
        return result

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
    def get_time_list(self, start_point, parameter):
        # Get month list in format YYYYMM (start_point)
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
        # filename = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast"
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_" + fcst_type + "_Forecast.db"
        # get month list
        current_month = time.strftime("%Y-%m", time.localtime())
        month_list = self.get_time_list(current_month, month_quantity)
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # 获取所有列表中最新的一个
        c.execute("SELECT name from sqlite_master where type = \"table\" ORDER by name DESC")
        tbl_name = c.fetchone()[0]
        forecast_result = []
        for month_item in month_list:
            sql_cmd = "SELECT Quantity FROM " + tbl_name + " WHERE Material = \'" + code_name + \
                      "\' AND Month = \'" + month_item + "\'"
            c.execute(sql_cmd)
            try:
                forecast_result.append(c.fetchall()[0][0])
            except IndexError:
                forecast_result.append(0)
        return [month_list, forecast_result]

    # get forecast of one hierarchy, set fcst_type as Statistical or Final
    def get_h5_forecast(self, h5_name, fcst_type, month_quantity):
        # Get future month list
        current_month = time.strftime("%Y-%m", time.localtime())
        month_list = self.get_time_list(current_month, month_quantity)
        # get forecast data
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_" + fcst_type + "_Forecast.db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # Get the newest table
        c.execute("SELECT name from sqlite_master where type = \"table\" ORDER by name DESC")
        tbl_name = c.fetchone()[0]
        forecast_result = []
        for month_item in month_list:
            if h5_name.upper() == "ALL":
                sql_cmd = "SELECT sum(Value_SAP_Price) FROM " + tbl_name + " WHERE Month = \'" + month_item + "\'"
            else:
                sql_cmd = "SELECT sum(Value_SAP_Price) FROM " + tbl_name + " WHERE Hierarchy_5 = \'" + h5_name + \
                      "\' COLLATE NOCASE AND Month = \'" + month_item + "\'"
            c.execute(sql_cmd)
            # if not setting, make value 0
            result = c.fetchall()
            forecast_output = result[0][0] if result[0][0] else 0
            # change format from integer to float
            forecast_result.append(forecast_output * 1.0)
        conn.commit()
        conn.close()
        return forecast_result

    # get eso result for one code or one hierarchy_5
    def get_material_eso(self, material_name, eso_type="code"):
        print("==== < ESO Trend of %s > ====" % material_name)
        filename = self.__class__.bu_name + "_ESO"
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        if eso_type == "code":
            sql_cmd = "SELECT Month, Excess_Quantity, Slow_Moving_Quantity, Obsolete_Quantity, ESO_Quantity, " \
                  "ESO_Value_Standard_Cost, ESO_Value_SAP_Price FROM " + filename + " WHERE Material = \'" + \
                  material_name + "\' ORDER BY Month"
        else:
            if material_name.upper() != "ALL":
                sql_cmd = "SELECT Month, sum(ESO_Value_Standard_Cost), sum(ESO_Value_SAP_Price) FROM " + filename + \
                      " WHERE Hierarchy_5 = \'" + material_name + "\' GROUP by Month, Hierarchy_5 ORDER BY Month"
            else:
                sql_cmd = "SELECT Month, sum(ESO_Value_Standard_Cost), sum(ESO_Value_SAP_Price) FROM " + filename + \
                          " GROUP by Month ORDER BY Month"
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            print("!!Error! No such code, please check your input!")
            return
        eso_result = c.fetchall()
        return eso_result


if __name__ == "__main__":
    info_check = InfoCheck("TU")
    result = info_check.get_material_eso("VA Ankle", eso_type="H5")
    print(result)
    # info_check.get_code_phoenix_result("689.893")



