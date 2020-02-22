import sqlite3
from datetime import datetime 
import time
import data_import
import math
from openpyxl import Workbook
from tabulate import tabulate


class InfoCheck:
    bu_name = ""
    db_path = "../data/_DB/"

    def __init__ (self, bu):
        self.__class__.bu_name = bu

    # 读取单个代码全部的master data
    def get_master_data(self, material):
        self.code = material
        # 设置空数组
        self.empty_result = ['NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', 'N', 'NA', 'NA', 0, 0, 'N', None, None, None, 'N']
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        self.str_cmd = "SELECT * from " + self.tbl_name + " WHERE material = \'" + self.code + "\' "
        self.result = c.execute(self.str_cmd)
        self.row = self.result.fetchall()
        if len(self.row) == 0:
            self.row = (self.empty_result,)
        conn.close()
        return list(self.row[0])

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
            str_cmd = "SELECT month, sum(Value_Standard_Cost) from " + tbl_name + " WHERE Hierarchy_5 = '" + \
                      hierarchy + "\' GROUP BY month ORDER BY month"
        else:
            str_cmd = "SELECT month, sum(Value_SAP_Price) from " + tbl_name + " WHERE Hierarchy_5 = \'" + \
                      hierarchy + "\' GROUP BY month ORDER BY month"
        result = c.execute(str_cmd)
        lst_result = []
        for item in result:
            lst_result.append(item)
        conn.close()
        return lst_result
    
    def get_H5_hstr_inv(self, type, price, name):
        self.inv_type = type
        self.price_type = price
        self.h5_name = name
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_" +self.inv_type + "_INV"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        self.str_cmd = "SELECT month, SUM(Value_" + self.price_type + ") from " + self.tbl_name + " WHERE Hierarchy_5 = \'" + self.h5_name + "\' GROUP BY month"
        self.h5_inv_result = c.execute(self.str_cmd).fetchall()
        return self.h5_inv_result

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

    # by code的销量数据
    def get_code_sales(self, type, material):
        self.code = material
        self.data_type = type
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_" + self.data_type
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(quantity) from " + self.tbl_name + " WHERE material = \'" + self.code + "\' GROUP BY month ORDER BY month"
        result = c.execute(str_cmd)
        self.lst_result = []
        for item in result:
            self.lst_result.append(item)
        conn.close()
        return self.lst_result

    # 返回销量数据总表 - 方法2
    def get_code_sales_list(self, type):
        self.data_type = type
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_" + self.data_type
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT material, month, SUM(quantity) from " + self.tbl_name + " GROUP BY material, month ORDER BY month"
        self.result = c.execute(str_cmd).fetchall()
        conn.close()
        return self.result

    # 返回库存数据表总表
    def get_code_inv_list(self, type):
        self.data_type = type
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_" +self.data_type
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        if type == "JNJ_INV":
            str_cmd = "SELECT material, month, SUM(Inventory_Onhand) from " + self.tbl_name + " GROUP BY material, month ORDER BY month"
        else:
            str_cmd = "SELECT material, month, SUM(quantity) from " + self.tbl_name + " GROUP BY material, month ORDER BY month"
        self.result = c.execute(str_cmd).fetchall()
        return self.result

    #获取单个代码的LP库存
    def get_code_lp_inv(self, material):
        self.code = material
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_LP_INV"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(quantity) from " + self.tbl_name + " WHERE Material = \'" + self.code + "\' GROUP BY month ORDER BY month"
        result = c.execute(str_cmd)
        self.lst_result = []
        for item in result:
            self.lst_result.append(item)
        conn.close()
        return self.lst_result

    #获取单个代码的JNJ库存
    def get_code_jnj_inv(self, material):
        self.code = material
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_JNJ_INV"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT month, SUM(Available_Stock) from " + self.tbl_name + " WHERE Material = \'" + self.code + "\' GROUP BY month ORDER BY month"
        result = c.execute(str_cmd)
        self.lst_result = []
        for item in result:
            self.lst_result.append(item)
        conn.close()
        return self.lst_result

    # 返回有效的H5名称
    def get_h5_name(self, name):
        self.h5_name = name
        # 文件名，无后缀
        self.file_name = self.__class__.bu_name + "_Master_Data"
        # 数据库完整路径加名称
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        # 表格名称，等于文件名称
        self.tbl_name = self.file_name
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT distinct Hierarchy_5 from " + self.tbl_name + " WHERE Hierarchy_5 LIKE \'%" + self.h5_name + "%\'"
        result = c.execute(str_cmd)
        self.h5_output = []
        for item in result:
            self.h5_output.append(item[0])
        # 如果返回是空结果
        if len(self.h5_output) == 0:
            print("No related H5 name, please check.")
            self.h5_result = "NULL"
        # 如果返回是单值
        elif len(self.h5_output) == 1:
            self.h5_result = self.h5_output[0]
        #如果有多个返回值
        else:
            print("More than 1 similiar output as below：")
            self.item = iter(self.h5_output)
            for self.i in range(1,len(self.h5_output)):
                print(self.i," - ", next(self.item))
            self.index_no = input("Plz input the NO of H5 you need：")
            if int(self.index_no) < len(self.h5_output):
                self.h5_result = self.h5_output[int(self.index_no) - 1]
            else:
                print("Wrong No, Please re-input！")
                self.h5_result = "NULL"
        conn.close()
        return self.h5_result

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

    # 获取by code的详细信息
    def generate_code_detail(self):
        # 获取代码列表
        self.code_generate = data_import.DataInput("TU")
        self.code_list = self.code_generate.get_active_codes()
        self.final_result = []
        #开始计时
        print ("开始读取数据")
        start_time = datetime.now()
        #获取总数
        bar_length = len(self.code_list)
        #进度条触发器
        index = 0
        # 进度逢5显示
        num = 5
        #开始读取数据
        for self.code in self.code_list:
            self.code_result = []
            info_result = info_check.get_master_data(self.code)
            self.code_result.append(info_result)
            gts_result = info_check.data_mapping(info_check.get_code_sales("GTS",self.code), "2019-06", -24)
            self.code_result.append(gts_result)
            lpsales_result = info_check.data_mapping(info_check.get_code_sales("LPSales",self.code), "2019-06", -24)
            self.code_result.append(lpsales_result)
            ims_result = info_check.data_mapping(info_check.get_code_sales("IMS",self.code), "2019-06", -24)
            self.code_result.append(ims_result)
            jnj_inv_result = info_check.data_mapping(info_check.get_code_jnj_inv(self.code), "2019-06", -24)
            self.code_result.append(jnj_inv_result)
            lp_inv_result = info_check.data_mapping(info_check.get_code_lp_inv(self.code), "2019-06", -24)
            self.code_result.append(lp_inv_result)
            self.final_result.append(self.code_result)
            # 画进度条
            index = index + 1
            if (math.floor((index/bar_length)*20) > math.floor(((index - 1)/bar_length)*20)):
                print (" -->",num,"%",end="",flush=True)
                num += 5
        # 计时结束
        print ("")
        print ("共读取%s个数据"%len(self.final_result))
        stop_time = datetime.now()
        print ("数据读取完成，耗时%s秒"%(stop_time-start_time).seconds)
        return self.final_result
    
    # 采用方法二获取代码的详细信息
    def generate_code_detail_v2(self):
        # 获取代码列表
        print ("V2开始运算")
        self.code_generate = data_import.DataInput(self.__class__.bu_name)
        self.code_list = self.code_generate.get_active_codes()
        print ("代码获取完毕，共计%s个"%len(self.code_list))
        # 获取master data
        self.master_data = self.get_master_data_list()
        # 获取销量表格
        self.gts_list = self.get_code_sales_list("GTS")
        self.lpsales_list = self.get_code_sales_list("LPSales")
        self.ims_list = self.get_code_sales_list("IMS")
        # 获取库存表格
        self.jnj_inv_list = self.get_code_inv_list("JNJ_INV")
        self.lp_inv_list = self.get_code_inv_list("LP_INV")
        print ("销量库存获取完毕，开始运算。")
        self.final_result = []
        #开始计时
        self.start_time = datetime.now()
        #获取总数
        bar_length = len(self.code_list)
        #进度条触发器
        index = 0
        # 进度逢5显示
        num = 5
        # 开始计算
        for self.code in self.code_list:
            self.code_result = []
            
            # 获取基础信息
            self.mm_temp = []
            for self.mm_item in self.master_data:
                if self.mm_item[0] == self.code:
                    self.mm_temp = self.mm_item
            self.code_result.append(list(self.mm_temp))
            # 获取GTS
            self.gts_temp =[]
            for self.gts_item in self.gts_list:
                if self.gts_item[0] == self.code:
                    self.gts_temp.append((self.gts_item[1],self.gts_item[2]))
            gts_result = info_check.data_mapping(self.gts_temp, "2019-06", -24)
            self.code_result.append(gts_result)
            # 获取lpsales
            self.lpsales_temp =[]
            for self.lpsales_item in self.lpsales_list:
                if self.lpsales_item[0] == self.code:
                    self.lpsales_temp.append((self.lpsales_item[1],self.lpsales_item[2]))
            lpsales_result = info_check.data_mapping(self.lpsales_temp, "2019-06", -24)
            self.code_result.append(lpsales_result)
            # 获取IMS
            self.ims_temp =[]
            for self.ims_item in self.ims_list:
                if self.ims_item[0] == self.code:
                    self.ims_temp.append((self.ims_item[1],self.ims_item[2]))
            ims_result = info_check.data_mapping(self.ims_temp, "2019-06", -24)
            self.code_result.append(ims_result)
            # 获取JNJ_INV
            self.jnj_inv_temp = []
            for self.jnj_inv_item in self.jnj_inv_list:
                if self.jnj_inv_item[0] == self.code:
                    self.jnj_inv_temp.append((self.jnj_inv_item[1],self.jnj_inv_item[2]))
            self.jnj_inv_result = info_check.data_mapping(self.jnj_inv_temp, "2019-06", -24)
            self.code_result.append(self.jnj_inv_result)
            # 获取LP_INV
            self.lp_inv_temp = []
            for self.lp_inv_item in self.lp_inv_list:
                if self.lp_inv_item[0] == self.code:
                    self.lp_inv_temp.append((self.lp_inv_item[1],self.lp_inv_item[2]))
            self.lp_inv_result = info_check.data_mapping(self.lp_inv_temp, "2019-06", -24)
            self.code_result.append(self.lp_inv_result)
            # 添加单条数据
            self.final_result.append(self.code_result)
            # 画进度条
            index = index + 1
            if (math.floor((index/bar_length)*20) > math.floor(((index - 1)/bar_length)*20)):
                print (" -->",num,"%",end="",flush=True)
                num += 5
        # 计时结束
        print ("")
        print ("共读取%s个数据"%len(self.final_result))
        self.stop_time = datetime.now()
        print ("数据读取完成，耗时%s秒"%(self.stop_time - self.start_time).seconds)
        return self.final_result

    # 获取 H5的详细信息
    def generate_H5_detail(self):
        self.h5_generate = data_import.DataInput(self.__class__.bu_name)
        self.h5_list = self.h5_generate.get_H5_list()
        self.h5_output = []
        #开始计时
        print ("开始读取数据")
        self.start_time = datetime.now()

        for self.h5_code in self.h5_list:
            self.h5_line = []
            self.h5_line.append(self.h5_code)
            # 获取固定月份的GTS数字
            self.h5_gts_result = self.data_mapping(self.get_H5_sales("GTS", "SAP Price", self.h5_code),"2019-06", -24)
            self.h5_line.append(self.h5_gts_result)
            self.h5_output.append(self.h5_line)
        self.stop_time = datetime.now()
        print ("数据读取完成，耗时%s秒"%(self.stop_time - self.start_time).seconds)
        return self.h5_output

    def export_to_excel(self, input):
        self.data = input
        # print(self.data)
        self.lst = []
        for self.item in self.data:
            self.lst_item = []
            for self.detail in self.item:
                self.lst_item += self.detail
            self.lst.append(self.lst_item)
        self.workbook = Workbook()
        print ("开始写入excel文件")
        self.booksheet = self.workbook.active
        for self.item in self.lst:
            self.booksheet.append(self.item)
        self.workbook.save("_Output\\text.xlsx")
        print ("文件写入完毕")

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

    # 读取某个h5的代码和销售价格
    def get_h5_code_price_list(self, h5_name):
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        tbl_name = self.__class__.bu_name + "_Master_Data"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # 获取某个h5的代码和销售价格
        c.execute("SELECT Material, SAP_Price from " + tbl_name + " WHERE Hierarchy_5 = \'" + h5_name + "\'")
        result = c.fetchall()
        return result

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
    result = info_check.get_code_gtin("440.834")
    print(result)
    # 方法2获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail_v2()
    # info_check.export_to_excel(result)
    # 方法1获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail()
    # info_check.export_to_excel(result)

