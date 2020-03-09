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
        # 设置空数组
        empty_result = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'N', 'NA', 'NA', 0, 0, 'N', None, None, None, 'N']
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT * from " + tbl_name + " WHERE material = \'" + code + "\' "
        c.execute(str_cmd)
        row = c.fetchall()
        if len(row) == 0:
            row = (empty_result,)
        conn.close()
        return list(row[0])

    # 读取全部的master data list
    def get_master_data_list(self):
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        self.str_cmd = "SELECT * from " + self.tbl_name
        self.result = c.execute(self.str_cmd)
        self.row = self.result.fetchall()
        conn.close()
        return list(self.row)

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
    def get_inventory_month(lst_inv, lst_sales, month_number):
        lst_inv_month = []
        # leave previous 6 month in blank
        for i in range(0, 6):
            lst_inv_month.append(0)
        for i in range(0, month_number-6):
            if sum(lst_sales[i: i+6]) == 0:
                lst_inv_month.append(0)
            else:
                lst_inv_month.append(lst_inv[i+6] / (sum(lst_sales[i: i+6])/6))
        return lst_inv_month

    # 返回有效的H5名称
    def get_h5_name(self, h5_name):
        # 文件名，无后缀
        tbl_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT distinct Hierarchy_5 COLLATE NOCASE from " + tbl_name + " WHERE Hierarchy_5 LIKE \'%" + h5_name + "%\'"
        c.execute(str_cmd)
        result = c.fetchall()
        h5_output = [item[0] for item in result]
        # 如果返回是空结果
        if len(h5_output) == 0:
            print("No related H5 name, please check.")
            h5_result = "NULL"
        # 如果返回是单值
        elif len(h5_output) == 1:
            h5_result = h5_output[0]
        # 如果有多个返回值
        else:
            print("More than 1 similar output as below：")
            item = iter(h5_output)
            for i in range(1, len(h5_output) + 1):
                print(i, " - ", next(item))
            index_no = input("Plz input the NO of H5 you need：")
            if index_no.isnumeric() and int(index_no) <= len(h5_output):
                h5_result = h5_output[int(index_no) - 1]
            else:
                print("Wrong No, Please re-input！")
                h5_result = "NULL"
        conn.close()
        return h5_result

    # 获取月份列表
    # 默认输入月份为当前月，则过去月份不包含当月，将来月份包含当月
    def get_time_list(self, start_point, parameter):
        self.para = parameter
        # 获得起始月份
        self.start_year = int(start_point[0:4])
        self.start_month = int(start_point[-2:])
        self.month_list = []
        if self.para <= 0:
            i = self.para
            while i < 0:
                self.t = (self.start_year,self.start_month + i, 14, 3, 6, 3, 6, 0, 0)
                self.sec = time.mktime(self.t)
                self.month_list.append(time.strftime("%Y-%m", time.localtime(self.sec)))
                i = i + 1
        else:
            i = 0
            while i < self.para:
                self.t = (self.start_year,self.start_month + i, 14, 3, 6, 3, 6, 0, 0)
                self.sec = time.mktime(self.t)
                self.month_list.append(time.strftime("%Y-%m", time.localtime(self.sec)))
                i = i + 1
        return self.month_list

    # 将数据与指定月份mapping
    def data_mapping(self, data, start_month, months):
        self.value = data
        self.month_list = self.get_time_list(start_month, months)
        self.result_value = []
        for self.item_month in self.month_list:
            value = 0
            for self.item_value in self.value:
                if self.item_value[0] == self.item_month:
                    value = self.item_value[1]
            self.result_value.append(value)
        return self.result_value

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
            sql_cmd = "SELECT sum(Value_SAP_Price) FROM " + tbl_name + " WHERE Hierarchy_5 = \'" + h5_name + \
                      "\' AND Month = \'" + month_item + "\'"
            c.execute(sql_cmd)
            forecast_result.append(c.fetchall()[0][0])
        conn.commit()
        conn.close()
        return forecast_result

    # 获取单个代码的ESO
    def get_code_eso(self, code_name):
        print("==== < ESO Trend of %s > ====" % code_name)
        filename = self.__class__.bu_name + "_ESO"
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT Month, Excess_Quantity, Slow_Moving_Quantity, Obsolete_Quantity, ESO_Quantity, " \
                  "ESO_Value_Standard_Cost, ESO_Value_SAP_Price FROM " + filename + " WHERE Material = \'" + \
                  code_name + "\' ORDER BY Month"
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            print("!!Error! No such code, please check your input!")
            return
        eso_result = c.fetchall()
        code_eso_result = [["Cycle", ], ["E_Qty", ], ["SM_Qty", ], ["O_Qty", ], ["ESO_Qty", ], ["ESO_Value_Std_Cost", ],
                           ["ESO_Value_SAP_Price", ]]
        for item in eso_result:
            index = 0
            while index < 7:
                code_eso_result[index].append(item[index])
                index += 1
        print(tabulate(code_eso_result, tablefmt="psql", headers="firstrow", floatfmt=",.0f"))


if __name__ == "__main__":
    info_check = InfoCheck("TU")
    # info_check.get_code_phoenix_result("689.893")
    print(info_check.get_code_phoenix_result("689.893"))


