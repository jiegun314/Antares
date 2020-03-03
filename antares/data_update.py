# import os, sys
import sqlite3
import pandas as pd
import calculation as cclt
# import math
# import data_import as dtimp
import numpy as np
from datetime import datetime


class MonthlyUpdate:
    bu_name = ""
    update_path = "../data/_Update/"
    db_path = "../data/_DB/"

    def __init__ (self, bu):
        self.__class__.bu_name = bu

    def update_sales(self, inv_type):
        self.inv_type = inv_type
        print("==" + self.inv_type + " Import==")
        # 输入Y确认进行导入
        print("!Warning - Please make sure data is correctly named and put in _Update folder.")
        cmd_key = input("Ready to continue? (Y/N): ")
        if cmd_key.upper() != "Y":
            return
        # 读取excel文件
        print("==Start to read the data==")
        self.file_name = self.__class__.update_path + "Update_" + self.__class__.bu_name + "_" +self.inv_type + ".xlsx"
        self.df = pd.read_excel(self.file_name, dtype={'Month': object})
        # 转换成二位列表
        self.lst_material = np.array(self.df).tolist()
        # 实例化一个查询对象
        self.mm_result =[]
        self.info_check = cclt.InfoCheck(self.__class__.bu_name)
        for self.item_2 in self.lst_material:
            self.mm_result.append(self.info_check.get_master_data(self.item_2[0]))
        # 数据整合
        self.index = 0
        for self.item_3 in self.lst_material:
            # 插入std cost价格
            if self.mm_result[self.index][10] == None:
                self.item_3.append(0)
            else:
                self.item_3.append(self.mm_result[self.index][10]*self.item_3[2])
            # 插入sap价格
            if self.mm_result[self.index][11] == None:
                self.item_3.append(0)
            else:
                self.item_3.append(self.mm_result[self.index][11]*self.item_3[2])
            # 插入BU
            self.item_3.append(self.__class__.bu_name)
            # 插入H4
            self.item_3.append(self.mm_result[self.index][4])
            # 插入H5
            self.item_3.append(self.mm_result[self.index][5])
            self.index += 1
        # 插入数据库
        print("==Reading complete, start importing to database==")
        self.file_name = self.__class__.bu_name + "_" + self.inv_type
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        self.conn = sqlite3.connect(self.db_fullname)
        self.conn.executemany("INSERT INTO " + self.file_name + " values (?,?,?,?,?,?,?,?)", self.lst_material)
        self.conn.commit()
        self.conn.close()
        print("===== <%s Import Successfully!> ====="%self.inv_type)
    
    def update_lp_inv(self):
        print("==LP_Sales Import==")
        print("---!Warning - Please make sure data is correctly name and put in _Update folder.---")
        # 输入Y确认进行导入
        cmd_key = input("Ready to continue? (Y/N):")
        if cmd_key.upper() != "Y":
            return
        print("==Start to read the data==")
        file_name = self.__class__.update_path + "Update_" + self.__class__.bu_name + "_LP_INV.xlsx"
        df = pd.read_excel(file_name, dtype={'Month': object})
        # 转换成二位列表
        lst_lp_inv = np.array(df).tolist()
        # 实例化一个查询对象
        mm_result = []
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        for self.item_2 in lst_lp_inv:
            mm_result.append(info_check.get_master_data(self.item_2[0]))
        # 数据整合
        index = 0
        for item_3 in lst_lp_inv:
            # 插入std cost价格
            if mm_result[index][10] is None:
                item_3.append(0)
            else:
                item_3.append(mm_result[index][10] * item_3[2])
            # 插入SAP Price价格
            if mm_result[index][11] is None:
                item_3.append(0)
            else:
                item_3.append(mm_result[index][11] * item_3[2])
            # 插入BU
            item_3.append(self.__class__.bu_name)
            # 插入H4
            item_3.append(mm_result[index][4])
            # 插入H5
            item_3.append(mm_result[index][5])
            # 插入Suzhou属性
            item_3.append(mm_result[index][7])
            # 插入Phoenix属性
            item_3.append(mm_result[index][12])
            index += 1
        # 插入数据库
        print("==Reading complete, start importing to database==")
        tbl_name = self.__class__.bu_name + "_LP_INV"
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        conn.executemany("INSERT INTO " + tbl_name + " values (?,?,?,?,?,?,?,?,?,?)", lst_lp_inv)
        conn.commit()
        conn.close()
        print("===== <LP Inventory Import Successfully!> =====")

    def update_jnj_inv(self):
        print("==JNJ Inventory Import==")
        import_date = input("Please input the date your want to import (YYYYMMDD): ")
        # 获取月份
        str_month = import_date[0:4] + "-" + import_date[4:6]
        import_tbl_name = "INV" + import_date
        db_fullname = self.__class__.db_path + "TU_CRT_INV.db"
        # 读取Oneclick数据
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT count(*) FROM sqlite_master where type = \'table\' and name = \'" + import_tbl_name + "\'"
        c.execute(sql_cmd)
        tbl_result = c.fetchone()[0]
        if tbl_result == 0:
            print("!Error. Wrong date input, please re-input. ")
            return
        sql_cmd = '''SELECT Material, Inventory_OnHand, Available_Stock, Pending_Inventory_Bonded_Total_Qty, 
                    Pending_Inventory_Bonded_Q_Hold_Qty, Pending_Inventory_NonB_Total_Qty, SS FROM '''
        c.execute(sql_cmd + import_tbl_name + " Order by Available_Stock DESC")
        lst_jnj_inv = []
        inv_output = c.fetchall()
        # 转成列表，插入月份
        for item in inv_output:
            item_jnj_inv = list(item)
            item_jnj_inv.insert(0, str_month)
            lst_jnj_inv.append(item_jnj_inv)
        # 实例化一个查询对象
        mm_result = []
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        # 计数变量
        counter = 0
        list_length = len(lst_jnj_inv)
        list_show = []
        gap_show = int(list_length / 20)
        for i in range(1, 21):
            list_show.append(i * gap_show)
        num = 5
        # 开始读取material master
        for self.item in lst_jnj_inv:
            mm_result.append(info_check.get_master_data(self.item[1]))
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        # 数据整合
        index = 0
        for item in lst_jnj_inv:
            # 设定价格
            if mm_result[index][10] is None:
                item_std_cost = 0
            else:
                item_std_cost = mm_result[index][10]
            if mm_result[index][11] is None:
                item_sap_price = 0
            else:
                item_sap_price = mm_result[index][11]
            # 插入Value_Standard_Cost
            item.append(item_std_cost * item[3])
            # 插入Value_SAP_Price
            item.append(item_sap_price * item[3])
            # 插入Pending_NB_Std_Cost
            item.append(item_std_cost * item[6])
            # 插入Pending_NB_SAP_Price
            item.append(item_sap_price * item[6])
            # 插入Pending_B_Std_Cost
            item.append(item_std_cost * item[4])
            # 插入Pending_B_SAP_Price
            item.append(item_sap_price * item[4])
            # 插入 Total_Inventory, Total_Inventory_Std_Cost, Total_Inventory_SAP_Price
            total_inv_qty = item[3] + item[4] + item[6]
            item.extend([total_inv_qty, total_inv_qty * item_std_cost, total_inv_qty * item_sap_price])
            # 插入 h4, h5, pm, instrument, suzhou, phoenix六个特殊属性
            item.extend([mm_result[index][4], mm_result[index][5], mm_result[index][6], mm_result[index][16], mm_result[index][7], mm_result[index][12]])
            index += 1
        # 插入数据库
        print(" ")
        print("==Reading complete, start importing to database==")
        tbl_name = self.__class__.bu_name + "_JNJ_INV"
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        conn.executemany("INSERT INTO " + tbl_name + " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lst_jnj_inv)
        conn.commit()
        conn.close()
        print("===== <JNJ Inventory Import Successfully!> =====")

    def update_eso(self):
        # 29 个元素
        file_name = self.__class__.bu_name + "_ESO"
        file_fullname = self.__class__.update_path + "Update_" + file_name + ".xlsx"
        db_fullname = self.__class__.db_path + file_name + ".db"
        print("Start to read the Excel file")
        start_time = datetime.now()
        df_eso = pd.read_excel(file_fullname)
        eso_data = df_eso.values
        stop_time = datetime.now()
        print("FIle is read by using %s seconds" % (stop_time - start_time).seconds)
        conn = sqlite3.connect(db_fullname)
        sql_cmd = "INSERT INTO " + file_name + " values("
        for i in range(28):
            sql_cmd = sql_cmd + "?,"
        sql_cmd = sql_cmd + "?)"
        conn.executemany(sql_cmd, eso_data)
        conn.commit()
        conn.close()
        print("ESO File is updated")
        pass

    def data_update_entrance(self, cmd):
        if cmd == "901":
            self.update_sales("GTS")
        elif cmd == "902":
            self.update_sales("LPSales")
        elif cmd == "903":
            self.update_sales("IMS")
        elif cmd == '905':
            self.update_jnj_inv()
        elif cmd == "906":
            self.update_lp_inv()
        elif cmd == "909":
            self.update_eso()
        else:
            pass


if __name__ == "__main__":
    data_import = MonthlyUpdate("TU")
    data_import.data_update_entrance("909")
    pass
