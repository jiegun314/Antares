import pandas as pd
import sqlite3
# import time
import numpy as np
import db_create as db
from datetime import datetime 


class DataInput:
    bu_name = ""
    file_path = "../data/_Source_Data/"
    update_path = "../data/_Update/"
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def sales_input(self, inv_type, model="Overwrite"):
        # Update模式写了没用啊，是直接从表格中导入的。。。。。。
        self.cal_type = inv_type
        # 如果更新则不删除原有数据
        if model == "Update":
            self.route_path = self.__class__.update_path
        # 如果刷新则删除原有数据
        else:
            self.route_path = self.__class__.file_path

        self.file_name = self.__class__.bu_name + "_" + self.cal_type
        self.file_fullname = self.route_path + self.file_name + ".xlsx"
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        print("开始读取文件")
        start_time = datetime.now()
        dataframe = pd.read_excel(self.file_fullname)
        data = dataframe.values
        stop_time = datetime.now()
        print ("文件读取完成，耗时%s秒"%(stop_time-start_time).seconds)
        # 写入数据库
        conn = sqlite3.connect(self.db_fullname)
        # 刷新状态时删除原有数据库
        if model == "Overwrite":
            conn.execute("DROP TABLE IF EXISTS " + self.file_name)
            self.new_tbl = db.DatabaseSetup(self.__class__.bu_name)
            self.new_tbl.create_db_sales(self.cal_type)
        conn.executemany("INSERT INTO " + self.file_name + " values (?,?,?,?,?,?,?,?)",data)
        conn.commit()
        conn.close()

    def lp_inv_input(self):
        self.file_name = self.__class__.bu_name + "_LP_INV"
        self.file_fullname = self.__class__.file_path + self.file_name + ".xlsx"
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        print ("开始读取文件")
        start_time = datetime.now()
        dataframe = pd.read_excel(self.file_fullname)
        data = dataframe.values
        stop_time = datetime.now()
        print ("文件读取完成，耗时%s秒"%(stop_time-start_time).seconds)
        index = 1
        if index == 1:
            # 写入数据库
            conn = sqlite3.connect(self.db_fullname)
            conn.executemany("INSERT INTO " + self.file_name + " values (?,?,?,?,?,?,?,?,?,?)",data)
            conn.commit()
            conn.close()

    def jnj_inv_input(self):
        self.file_name = self.__class__.bu_name + "_JNJ_INV"
        self.file_fullname = self.__class__.file_path + self.file_name + ".xlsx"
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        print ("开始读取文件")
        start_time = datetime.now()
        dataframe = pd.read_excel(self.file_fullname)
        data = dataframe.values
        stop_time = datetime.now()
        print ("文件读取完成，耗时%s秒"%(stop_time-start_time).seconds)
        index = 1
        if index ==1:
            # 写入数据库
            conn = sqlite3.connect(self.db_fullname)
            conn.executemany("INSERT INTO " + self.file_name + " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",data)
            conn.commit()
            conn.close()

    def eso_input(self):
        # 29 个元素
        file_name = self.__class__.bu_name + "_ESO"
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
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
        print("ESO File is imported")
    
    def get_active_codes(self):
        file_name = self.__class__.bu_name + "_Active_Codes"
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
        print("开始读取Code清单")
        df = pd.read_excel(file_fullname, dtype=object)
        # 读取所有元素
        data = df.values
        code_list = []
        for item in data:
            code_list.append(str(item[0]))
        # 测试阶段返回N个数字
        return code_list

    # import BU base master data
    def import_master_data(self, data_type):
        # for TU. data_type = {"Master_Data", "SAP_Price", "Phoenix_List"}
        file_name = self.__class__.bu_name + "_" + data_type
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        print("~ Start to read the data file %s" %file_name)
        start_time = datetime.now()
        if data_type == "Master_Data":
            df = pd.read_excel(file_fullname, na_values="0", dtype={'SAP_Price': np.float64})
        else:
            df = pd.read_excel(file_fullname, na_values="0")
        # data = df.values
        stop_time = datetime.now()
        print("~ File reading complete，with time of %s seconds" % (stop_time-start_time).seconds)
        # 写入数据库
        # conn = sqlite3.connect(db_fullname)
        # conn.execute("DROP TABLE IF EXISTS " + file_name)
        # new_tbl = db.DatabaseSetup(self.__class__.bu_name)
        # new_tbl.create_master_data()
        # conn.executemany("INSERT INTO " + file_name + " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", data)
        # conn.commit()
        # conn.close()
        conn = sqlite3.connect(db_fullname)
        df.to_sql(name=file_name, con=conn, if_exists='replace', index=False)
        print("%s is imported" % data_type)
        pass

    def import_public_master_data(self):
        # print title
        print("==Import General Master Data==")
        print("Please Choose Master Data Type (1 - Material Master, 2 - RAG Report, 3 - GTIN)")
        # define source data route
        master_data_path = self.__class__.update_path + "Public/"
        # define file name list
        master_data_filename_list = ["", "MATERIAL_MASTER", "RAG_Report", "GTIN"]
        cmd_code = input("cmd >> master_data >> ")
        if cmd_code == "exit":
            return
        if cmd_code not in ["1", "2", "3"]:
            print("Wrong Code. Please Try Again.")
            return
        master_data_filename = master_data_filename_list[int(cmd_code)]
        master_data_file = master_data_path + master_data_filename + ".xlsx"
        print("!Make sure you have put file %s in %s" % (master_data_filename, master_data_path))
        # start to read file
        print("Start to read data file.")
        if cmd_code == "2":
            df = pd.read_excel(master_data_file, sheet_name="REPORT")
        else:
            df = pd.read_excel(master_data_file)
        print("Start to import into database.")
        database_name = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_name)
        df.to_sql(name=master_data_filename, con=conn, if_exists='replace', index=False)
        print("%s imported" % master_data_filename)
        pass
    
    def get_H5_list(self):
        self.file_name = self.__class__.bu_name + "_Master_Data"
        self.db_fullname = self.__class__.db_path + self.file_name + ".db"
        conn = sqlite3.connect(self.db_fullname)
        c = conn.cursor()
        result = c.execute("SELECT DISTINCT Hierarchy_5 from " + self.file_name)
        self.list = []
        for self.item in result:
            self.list.append(self.item[0])
        return (self.list)


if __name__ == "__main__":
    data_input = DataInput("TU")
    data_input.import_master_data("Master_Data")
    # cmd = int(input("选择需要导入的数据，1 - GTS，2 - LP Sales， 3 - IMS, 4 - LP_INV: "))
    # if cmd == 1:
    #     data_input.sales_input ("GTS")
    # elif cmd == 2:
    #     data_input.sales_input ("LPSales")
    # elif cmd == 3:
    #     data_input.sales_input ("IMS")
    # elif cmd == 4:
    #     data_input.lp_inv_input()
    # else:
    #     print ("命令错误")