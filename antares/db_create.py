import sqlite3


class DatabaseSetup:
    # 创建bu_name这个类属性
    bu_name = ""
    # 数据库路径
    db_root = "../data/_DB/"

    def __init__(self, name):
        # 获得bu_name
        self.__class__.bu_name = name
        pass

    def create_db_sales(self, type):
        self.cal_type = type
        self.file_name = self.__class__.bu_name + "_" + self.cal_type
        self.file_fullname = self.__class__.db_root + self.file_name + ".db"
        conn = sqlite3.connect(self.file_fullname)
        c = conn.cursor()
        c.execute(''' CREATE TABLE ''' + self.file_name +'''
            (Material CHAR(20) NOT NULL,
            Month   CHAR(10) NOT NULL,
            Quantity    INT NOT NULL,
            Value_Standard_Cost REAL   NOT NULL,
            Value_SAP_Price REAL    NOT NULL,
            Business_Unit   CHAR(10)    NOT NULL,
            Hierarchy_4 CHAR(50)    NOT NULL,
            Hierarchy_5 CHAR(100)   NOT NULL);''')
        conn.commit()
        conn.close()
        pass

    # 平台库存的数据表格
    def create_db_lp_inv(self):
        self.file_name = self.__class__.bu_name + "_LP_INV"
        self.file_fullname = self.__class__.db_root + self.file_name + ".db"
        conn = sqlite3.connect(self.file_fullname)
        c = conn.cursor()
        c.execute(''' CREATE TABLE ''' + self.file_name +'''
            (Material CHAR(20) NOT NULL,
            Month   CHAR(10) NOT NULL,
            Quantity    INT NOT NULL,
            Value_Standard_Cost REAL   NOT NULL,
            Value_SAP_Price REAL    NOT NULL,
            Business_Unit   CHAR(10)    NOT NULL,
            Hierarchy_4 CHAR(50)    NOT NULL,
            Hierarchy_5 CHAR(100)   NOT NULL,
            Suzhou CHAR(1)  NOT NULL,
            Phoenix CHAR(1) NOT NULL);''')
        conn.commit()
        conn.close()

    # JNJ库存的数据表格
    def create_db_jnj_inv(self):
        self.file_name = self.__class__.bu_name + "_JNJ_INV"
        self.file_fullname = self.__class__.db_root + self.file_name + ".db"
        conn = sqlite3.connect(self.file_fullname)
        c = conn.cursor()
        c.execute(''' CREATE TABLE ''' + self.file_name +'''
            (Month      CHAR(10)    NOT NULL,
            Material    CHAR(20)    NOT NULL,
            Inventory_Onhand INT    NOT NULL,
            Available_Stock     INT NOT NULL,
            Pending_Inventory_Bonded_Total_Qty  INT NOT NULL,
            Pending_Inventory_Bonded_Q_Hold_Qty INT NOT NULL,
            Pending_Inventory_NonB_Total_Qty    INT NOT NULL,
            Safety_Stock    INT,
            Value_Standard_Cost     REAL    NOT NULL,
            Value_SAP_Price         REAL    NOT NULL,
            Pending_NB_Std_Cost     REAL    NOT NULL,
            Pending_NB_SAP_Price    REAL    NOT NULL,
            Pending_B_Std_Cost      REAL    NOT NULL,
            Pending_B_SAP_Price     REAL    NOT NULL,
            Total_Inventory         INT     NOT NULL,
            Total_Inventroy_Std_Cost REAL   NOT NULL,
            Total_Inventory_SAP_Price REAL  NOT NULL,
            Hierarchy_4             CHAR(50)    NOT NULL,
            Hierarchy_5             CHAR(100)   NOT NULL,
            PM                      CHAR(50)    NOT NULL,
            Instrument              CHAR(1)     NOT NULL,
            Suzhou  CHAR(1)     NOT NULL,
            Phoenix CHAR(1)     NOT NULL);''')
        conn.commit()
        conn.close()

    # 创建Master Data数据表格
    def create_master_data(self):
        file_name = self.__class__.bu_name + "_Master_Data"
        file_fullname = self.__class__.db_root + file_name + ".db"
        conn = sqlite3.connect(file_fullname)
        c = conn.cursor()
        c.execute(''' CREATE TABLE ''' + file_name + '''
            (Material CHAR(20) NOT NULL,
            Description   CHAR(150),
            CN_Description   CHAR(150),
            Hierarchy_3   CHAR(50),
            Hierarchy_4   CHAR(50),
            Hierarchy_5   CHAR(150),
            PM   CHAR(50) NOT NULL,
            Suzhou   CHAR(2) NOT NULL,
            Sales_Status   CHAR(10),
            Purchase_Status   CHAR(10),
            Standard_Cost   REAL,
            SAP_Price   REAL,
            Phoenix CHAR(2) NOT NULL,
            Phoenix_Wave CHAR(100),
            Phoenix_Stop_MNFC_Date  CHAR(30),
            Phoenix_Target_SKU CHAR(30),
            Instrument CHAR(2));''')
        conn.commit()
        conn.close()


if __name__ == "__main__":
    # 实例化销量输入类
    db_setup = DatabaseSetup("MT")
    db_setup.create_master_data()
    # cmd = int(input("选择需要创建的数据库，1 - GTS，2 - LP Sales， 3 - IMS， 4 - LP_INV: "))
    # if cmd == 1:
    #     db_setup.create_db_sales ("GTS")
    # elif cmd == 2:
    #     db_setup.create_db_sales ("LPSales")
    # elif cmd == 3:
    #     db_setup.create_db_sales ("IMS")
    # elif cmd == 4:
    #     db_setup.create_db_lp_inv ()
    # else:
    #     print ("命令错误")
