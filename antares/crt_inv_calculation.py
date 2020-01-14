import sqlite3
import pandas as pd
import numpy as np
from tabulate import tabulate
import crt_inv_chart as chart
import time
import os, sys
import calculation
import pandas as pd


class CurrentInventory():
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    
    def __init__(self, bu):
        self.__class__.bu_name = bu

    # 获取最新日期
    def _get_newest_date(self):
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "select name from sqlite_master where type='table' order by name"
        self.c.execute(self.sql_cmd)
        self.result = self.c.fetchall()
        self.lst_date = []
        for self.item in self.result:
            self.lst_date.append(self.item[0])
        self.lst_date.sort(reverse = True)
        self.conn.commit()
        self.conn.close()
        return self.lst_date[0]

    # 检查日期是否存在
    def _check_date_availability(self, name):
        self.tb_input = name
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "select name from sqlite_master where type='table' order by name"
        self.c.execute(self.sql_cmd)
        self.result = self.c.fetchall()
        self.lst_date = []
        for self.item in self.result:
            self.lst_date.append(self.item[0])
        if self.tb_input in self.lst_date:
            self.trigger = True
        else:
            self.trigger = False
        self.conn.commit()
        self.conn.close()
        return self.trigger
    
    # 检查代码是否存在
    def _check_code_availability(self, name):
        self.code_name = name
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        #获取最新表格
        self.sql_cmd = "select name from sqlite_master where type='table' order by name"
        self.c.execute(self.sql_cmd)
        self.result = self.c.fetchall()
        self.tbl_result = self.result[-1][0]
        #判断代码是否存在
        self.sql_cmd = "SELECT count(Material) from " + self.tbl_result + " WHERE Material Like \'" + self.code_name + "\'"
        self.c.execute(self.sql_cmd)
        self.result = self.c.fetchall()
        self.check_result = self.result[0][0]
        if self.check_result == 0:
            return False
        else:
            return True


    # 获取所有表格的列表
    def get_tbl_list(self):
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "select name from sqlite_master where type='table' order by name"
        self.c.execute(self.sql_cmd)
        self.result = self.c.fetchall()
        self.tbl_list = []
        for self.item in self.result:
            self.tbl_list.append(self.item[0])
        self.conn.commit()
        self.conn.close()
        return self.tbl_list

    # 产品代码校验
    def check_code (self, code):
        self.material_code = code
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        self.tbl_name = self.__class__.bu_name + "_Master_Data"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "SELECT count(Material) from " +self.tbl_name + " WHERE Material = \'" + self.material_code + "\'"
        self.c.execute(self.sql_cmd)
        for self. item in self.c.fetchall():
            if self.item[0] == 0:
                self.trigger = False
            else:
                self.trigger = True
        self.conn.commit()
        self.conn.close()
        return self.trigger


    # 获取H5信息
    def _get_h5_list(self, table):
        self.table_name = table
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "select distinct Hierarchy_5 from " + self.table_name
        self.c.execute(self.sql_cmd)
        self.h5_list = []
        for self.item in self.c.fetchall():
            self.h5_list.append(self.item[0])
        self.conn.commit()
        self.conn.close()
        return self.h5_list

    def __remove_inv_tbl(self, db_date):
        self.tbl_name = "INV" + db_date
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "DROP TABLE " + self.tbl_name
        self.c.execute(self.sql_cmd)
        self.conn.commit()
        self.conn.close()
        print (">> Table %s is deleted."%self.tbl_name)

    def insert_inv_table(self, db_date):
        self.str_date = db_date
        self.file_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"+ self.str_date + "\\OneClick_Inventory_Projection_Report _" + self.str_date +".csv"
        #打开文件
        try:
            self.fo = open(self.file_path,"r")
        except FileNotFoundError:
            print ("!!ERROR, file does NOT exist. "+ self.str_date + "import fail.")
            return
        print(">>Start to read ",self.fo.name)
        # 创建数组
        self.lst_data = []
        for self.item in self.fo.readlines():
            self.item = self.item.strip('\n')
            self.lst_temp = self.item.split('|')
            if self.lst_temp[10] == self.__class__.bu_name and self.lst_temp[21]=="Total":
                # 转换。0000格式
                self.lst_data.append(tuple(self.__str_transfer(self.lst_temp)))
        self.fo.close()
        print (">>Read %s successfully."%self.str_date)
        self.__db_insert(self.str_date, self.lst_data)
        

    def __str_transfer(self, str_data):
        self.str_input = str_data
        self.str_result = []
        for self.item in self.str_input:
            if self.item.find('.0000')==0:
                self.str_result.append(0)
            elif self.item.find('.')>0 and self.item.find('00')>0 and self.str_input.index(self.item)>10:
                self.str_result.append(float(self.item))
            else:
                self.str_result.append(self.item)
        return self.str_result

    def __db_insert(self, date, data):
        self.tbl_name =  "INV" + date
        self.str_data = data
        # 连接数据库
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        # 删除重名表格
        self.conn.execute("DROP TABLE IF EXISTS " + self.tbl_name)
        self.c = self.conn.cursor()
        # 创建表格
        self.sql_cmd = '''CREATE TABLE '''+ self.tbl_name +'''
            (Material CHAR(50) NOT NULL,
            Description TEXT  NOT NULL,
            EMG_Description TEXT  NOT NULL,
            Hierarchy_1  TEXT  NOT NULL,
            Hierarchy_2  TEXT  NOT NULL,
            Hierarchy_3  TEXT  NOT NULL,
            Hierarchy_4  TEXT  NOT NULL,
            Hierarchy_5  TEXT  NOT NULL,
            Franchise TEXT  NOT NULL,
            Business_Group  TEXT  NOT NULL,
            Business_Unit  TEXT  NOT NULL,
            Base_UoM   TEXT  NOT NULL,
            Sales_UoM  TEXT  NOT NULL,
            Purchasing_UoM  TEXT  NOT NULL,
            Rate_Base_to_Pur INT  NOT NULL,
            Rate_Base_to_Sales  INT  NOT NULL,
            ESO_Flag  CHAR(5)  NOT NULL,
            Average_Selling_Price  REAL  NOT NULL,
            Standard_Cost  REAL  NOT NULL,
            CSC  CHAR(5)  NOT NULL,
            SS  INT  NOT NULL,
            Loc CHAR(5)  NOT NULL,
            Inventory_OnHand  INT  NOT NULL,
            Available_Stock  INT  NOT NULL,
            Pending_Inventory_Bonded_Total_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_140_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_141_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_142_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_Q_Hold_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_S_Hold_Qty  INT  NOT NULL,
            Pending_Inventory_Bonded_X_Hold_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_Total_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_140_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_141_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_142_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_Q_Hold_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_S_Hold_Qty  INT  NOT NULL,
            Pending_Inventory_NonB_X_Hold_Qty  INT  NOT NULL,
            Open_SO_Regular  INT  NOT NULL,
            Open_SO_Non_Regular  INT  NOT NULL,
            Current_Backorder_Qty  INT  NOT NULL,
            Current_Backorder_Value  REAL  NOT NULL,
            GIT_1_Week  INT  NOT NULL,
            GIT_2_Week  INT  NOT NULL,
            GIT_3_Week  INT  NOT NULL,
            GIT_4_Week  INT  NOT NULL,
            Open_PO  INT  NOT NULL,
            MTD_Val  INT  NOT NULL,
            MTD_NoVal  INT  NOT NULL,
            Last_Month_BackOrder_Qty  INT  NOT NULL,
            Forecast_T  INT  NOT NULL,
            Forecast_T_1  INT NOT NULL,
            Forecast_T_2  INT NOT NULL,
            Forecast_T_3  INT NOT NULL,
            Estimate_Backorder_Qty_Demand  INT  NOT NULL,
            Estimate_Backorder_Value_Demand  REAL  NOT NULL,
            Estimate_Backorder_Qty_Forecast  INT NOT NULL,
            Estimate_Backorder_Value_Forecast  REAL  NOT NULL,
            Estimate_Backorder_Qty_Aggressive  INT  NOT NULL,
            Estimate_Backorder_Value_Aggressive  REAL  NOT NULL,
            Inventory_Qty_Shelflife_3_MTH  INT  NOT NULL,
            Inventory_Qty_Shelflife_6_MTH  INT  NOT NULL,
            Inventory_Qty_Shelflife_12_MTH  INT  NOT NULL,
            Demand_Qty_T  INT  NOT NULL,
            Demand_Qty_T1  INT  NOT NULL,
            Demand_Qty_T2  INT  NOT NULL,
            Demand_Qty_T3  INT  NOT NULL,
            Demand_Qty_T4  INT  NOT NULL,
            Demand_Qty_T5  INT  NOT NULL,
            Demand_Qty_T6  INT  NOT NULL);'''
        self.c.execute(self.sql_cmd)
        print (">>Creat new table successfully!")
        # 开始插入数据
        self.sql_cmd = "INSERT INTO " + self.tbl_name + " VALUES (?"
        self.cnt = 1
        while self.cnt <=69:
            self.sql_cmd += ",?"
            self.cnt += 1
        else:
            self.sql_cmd += ")"
        self.c.executemany (self.sql_cmd, self.str_data)
        self.conn.commit()
        self.conn.close()
        print (">>Import %s successfully"%self.tbl_name)

    # 获取当天库存
    def today_inv(self):
        self.title = "===Current Inventory List by Hierarchy_5==="
        print (self.title)
        # 获取日期
        self.inv_date = input ("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if self.inv_date == "":
            self.tbl_name = self._get_newest_date()
        else:
            self.tbl_name = "INV" + self.inv_date
        print ("===== <Result of %s> ====="%self.tbl_name.lstrip("INV"))
        self.h5_list = self._get_h5_list(self.tbl_name)
        # 基本思路：用sql语句计算所有的结果
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = '''SELECT Hierarchy_5, sum(Available_Stock * Standard_Cost) AS onhand_inv, 
                        sum((GIT_1_Week + GIT_2_Week) * Standard_Cost) AS GIT_inv, 
                        sum(Pending_Inventory_Bonded_Total_Qty * Standard_Cost) AS BD_Pending_Value,
                        sum(Pending_Inventory_NonB_Total_Qty * Standard_Cost) AS NB_Pending_Value from ''' + self.tbl_name + ''' 
                        WHERE (Available_Stock + GIT_1_Week + GIT_2_Week + Pending_Inventory_Bonded_Total_Qty + Pending_Inventory_NonB_Total_Qty) > 0  
                        GROUP BY Hierarchy_5 ORDER BY onhand_inv DESC'''
        self.c.execute(self.sql_cmd)
        self.title = [("Hierarchy_5", "Onhand Inventory", "GIT Inventory", "Bonded Pending", "Non-bonded Pending")]
        self.result = self.title + self.c.fetchall()
        print (tabulate(self.result, headers="firstrow", tablefmt="github", showindex=range(1,len(self.result)), floatfmt=",.0f"))

    # 获取当前BO
    def get_current_bo (self):
        self.title = "===Current Backorder List==="
        print (self.title)
        # 获取日期
        self.inv_date = input ("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if self.inv_date == "":
            self.tbl_name = self._get_newest_date()
        else:
            self.tbl_name = "INV" + self.inv_date
        print ("===== <Result of %s> ====="%self.tbl_name.lstrip("INV"))
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = '''select Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty,
                        (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                        GIT_4_Week, Open_PO from ''' + self.tbl_name + ''' 
                        WHERE Current_Backorder_Qty > 0 ORDER by CSC DESC, bo_value DESC'''
        self.c.execute(self.sql_cmd)
        self.bo_result = self.c.fetchall()
        # 输出总数
        self.bo_qty_sum, self.bo_value_sum = 0 , 0
        for self.item in self.bo_result:
            self.bo_qty_sum += self.item[4]
            self.bo_value_sum += self.item[5]
        print("=== Current Backorder Quantity %s, Value RMB %s ==="%(self.bo_qty_sum, format(self.bo_value_sum,",.0f")))
        # 输入表格
        self.title = [('Material', 'Decription', 'Hierarchy_5', 'CSC', 'Qty', 'Value', 'GIT_1', 'GIT_2', 'GIT_3',
                       'GIT_4', 'Open_PO')]
        self.result = self.title + self.bo_result
        print (tabulate(self.result, headers="firstrow", tablefmt="github", showindex=range(1,len(self.result)), floatfmt=",.0f"))
        self.conn.commit()
        self.conn.close()

    # 导出backorder给平台
    def export_backorder_data(self):
        # print title
        print("===Export Backorder Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        sql_cmd = '''SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty,
                    (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                    (GIT_4_Week + Open_PO) AS not_delivered_qty FROM ''' + table_name + ''' 
                    WHERE Current_Backorder_Qty > 0 ORDER by bo_value DESC'''
        df = pd.read_sql(sql=sql_cmd, con=conn)
        df.drop(columns=["bo_value", ])
        backorder_file = self.__class__.backorder_path + "Backorder_" + table_name[3:] +".xlsx"
        df.to_excel(backorder_file, index=False)

    # Pending库存趋势分析
    def get_pending_trend(self):
        self.title = "===Single Code Inventory==="
        print (self.title)
        self.pending_result = []
        # 链接数据库
        self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.conn = sqlite3.connect(self.db_name)
        self.c = self.conn.cursor()
        self.sql_cmd = "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        self.c.execute(self.sql_cmd)
        self.tbl_list = self.c.fetchall()
        for self.tbl_name in self.tbl_list:
            self.sql_cmd = '''SELECT sum(Pending_Inventory_Bonded_Total_Qty), sum(Pending_Inventory_NonB_Total_Qty), 
                                sum((Standard_Cost * Pending_Inventory_Bonded_Total_Qty)) As Pending_BD_Value, 
                                sum((Standard_Cost * Pending_Inventory_NonB_Total_Qty)) As Pending_NB_Value from ''' + self.tbl_name[0]
            self.c.execute(self.sql_cmd)
            self.tmp_result = self.c.fetchall()
            self.pending_result.append (self.tbl_name + self.tmp_result[0])
        self.tbl_title = [["Date", "Bonded_Pending_QTY", "Nonboned_Pending_Qty","Bonded_Pending_Value", "Nonboned_Pending_Value"]]
        self.pending_output = self.tbl_title + self.pending_result
        print (tabulate(self.pending_output, headers="firstrow", tablefmt="github", showindex=range(1,len(self.pending_output)), floatfmt=",.0f"))

    # 查询单个代码
    def get_code_inv (self):
        self.title = "===Single Code Inventory==="
        print (self.title)
        # 获取日期
        self.code_name = input ("Input Material Code: ")
        while self._check_code_availability(self.code_name) == False:
            self.code_name = input ("Wrong code, please re-input: ")
        if self.check_code(self.code_name) :
            self.data_ready = True
            self.str_input = input ("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
            if self.str_input == "":
                self.tbl_name = self._get_newest_date()
            else:
                self.tbl_name = "INV" + self.str_input
                if self._check_date_availability(self.tbl_name) == False:
                    print ("!!Error - Wrong date, Please re-input! ")
                    self.data_ready = False
            if self.data_ready:
                print ("===== <Result of %s> ====="%self.tbl_name.lstrip("INV"))
                self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
                self.conn = sqlite3.connect(self.db_name)
                self.c = self.conn.cursor()
                self.sql_cmd = '''SELECT Material, Description, Hierarchy_5, Available_Stock, Pending_Inventory_Bonded_Total_Qty, 
                                    Pending_Inventory_NonB_Total_Qty, CSC, GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, 
                                    Standard_Cost, Average_Selling_Price from ''' + self.tbl_name + ' where Material = \"' + self.code_name + '\"'
                self.c.execute(self.sql_cmd)
                self.result = self.c.fetchall()[0]
                self.title = ["Material","Descritpion","Hierarachy_5","Available_Stock","Pending_Qty_BD", "Pending_Qty_NB", "CSC", "GIT_1_Qty", "GIT_2_Qty","GIT_3_Qty", "GIT_4_Qty", "Std Cost", "AVG Selling Price"]
                self.index = 0
                self.code_inv_output = [["Item", "Value"]]
                while self.index < len(self.result):
                    self.code_inv_output.append([self.title[self.index], self.result[self.index]])
                    self.index += 1
                print (tabulate(self.code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="grid"))
        else:
            print ("!!Error - This Material Code does NOT exist, Please re-input! ")
    
    # 查询单个代码可用库存趋势
    def code_inv_trend(self):
        title = "===Single Code Available Stock Trend==="
        print(title)
        # 获取日期
        code_name = input("Input Material Code : ")
        if self.check_code(code_name):
            # 获取日期清单
            tbl_list = self.get_tbl_list()
            db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
            conn = sqlite3.connect(db_name)
            c = conn.cursor()
            inv_result = []
            for tbl_item in tbl_list:
                sql_cmd = "SELECT Available_Stock from " + tbl_item + " WHERE Material = \'" + code_name + "\'"
                c.execute(sql_cmd)
                result = c.fetchone()
                if not result:
                    inv_result.append(0)
                else:
                    inv_result.append(result[0])
            print(inv_result)
        else:
            print("!!Error - This Material Code does NOT exist, Please re-input! ")
        conn.commit()
        conn.close()
        # print charter
        x_value = [item[-4:] for item in tbl_list]
        chart.line_chart(code_name, x_value, inv_result, "Date", "INV Qty", "Inventory Trend of " + code_name)

    # 查询H5库存趋势
    def h5_inv_trend(self):
        print("===Hierarchy_5 Available Stock Trend===")
        # 获取H5名称
        h5_input = input("Input Hierarchy_5 Name : ")
        if h5_input == "" or h5_input.upper() == "ALL":
            h5_result = "ALL"
        else:
            h5_temp = calculation.InfoCheck(self.__class__.bu_name)
            h5_result = h5_temp.get_h5_name(h5_input)
        # if not right h5 name, return
        if h5_result == "NULL":
            return
        # 获取日期清单
        tbl_list = self.get_tbl_list()
        # 连接数据库
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        h5_inv_result = []
        for tbl_item in tbl_list:
            if h5_result == "ALL":
                sql_cmd = "SELECT sum(Available_Stock * Standard_Cost) AS inv_value FROM " + tbl_item
            else:
                sql_cmd = "SELECT sum(Available_Stock * Standard_Cost) AS inv_value FROM " + tbl_item + \
                          " WHERE Hierarchy_5 = \"" + h5_result.upper() + "\""
            c.execute(sql_cmd)
            result = c.fetchone()
            if not result[0]:
                h5_inv_result.append(0)
            else:
                h5_inv_result.append(int(result[0]))
        # print charter
        x_value = [item[-4:] for item in tbl_list]
        chart.line_chart(h5_result, x_value, h5_inv_result, "Date", "Value", "Value by Std. Cost of " + h5_result)
    
    # 数据同步
    def inv_data_sync(self, days):
        self.sync_days = days
        self.title = "===Sync Current Inventory Data from Oneclick==="
        print(self.title)
        # 设置例外清单
        self.lst_xcpt = ['20190118',]
        self.onclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
        self.lst_folder_temp=[]
        # 读取oneclick目录下文件夹清单
        for self.file_name in os.listdir(self.onclick_path):
            self.lst_folder_temp.append(self.file_name)
        # 读取后N天, lst_folder为共享盘上数据
        self.lst_folder = self.lst_folder_temp[0-self.sync_days:]
        # 读取现有数据
        self.lst_db_date = self.get_tbl_list()
        # crt_list为现有数据
        self.crt_list = []
        for self.item in self.lst_db_date:
            self.crt_list.append(self.item.lstrip("INV"))
        # 开始对比数据
        # 删除过期数据
        for self.item in self.crt_list:
            if self.item not in self.lst_folder:
                self.__remove_inv_tbl(self.item)
                self.crt_list.remove(self.item)
        # 导入新的数据
        for self.item in self.lst_folder:
            if (self.item not in self.crt_list) and (self.item not in self.lst_xcpt):
                self.insert_inv_table(self.item)
        print (">> Synchronization sucess!")


if __name__ == "__main__":
    test = CurrentInventory("TU")
    test.export_backorder_data()
    # test.inv_data_sync(50)
