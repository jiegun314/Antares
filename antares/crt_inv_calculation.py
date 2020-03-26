import sqlite3
# import pandas as pd
# import numpy as np
from tabulate import tabulate
import draw_chart as chart
import os
import calculation
import pandas as pd


class CurrentInventory:
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    currency_rate = 7.0842
    
    def __init__(self, bu):
        self.__class__.bu_name = bu

    # 获取最新日期
    def _get_newest_date(self):
        conn = sqlite3.connect(self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db")
        c = conn.cursor()
        c.execute("select name from sqlite_master where type='table' order by name")
        lst_date = [item[0] for item in c.fetchall()]
        # lst_date.sort(reverse=True)
        conn.commit()
        conn.close()
        return lst_date[-1]

    # 检查日期是否存在
    def _check_date_availability(self, table_name):
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("select name from sqlite_master where type='table' order by name")
        result = c.fetchall()
        lst_date = [item[0] for item in result]
        trigger = True if table_name in lst_date else False
        conn.commit()
        conn.close()
        return trigger

    # 获取所有表格的列表
    def get_tbl_list(self):
        conn = sqlite3.connect(self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db")
        c = conn.cursor()
        c.execute("select name from sqlite_master where type='table' order by name")
        tbl_list = [item[0] for item in c.fetchall()]
        conn.commit()
        conn.close()
        return tbl_list

    # 产品代码校验
    def check_code(self, material_code):
        table_name = "Material_Master"
        conn = sqlite3.connect(self.__class__.db_path + "Master_Data.db")
        c = conn.cursor()
        sql_cmd = "SELECT count(Material) from " + table_name + " WHERE Business_Unit = \'" + self.__class__.bu_name \
                  + "\' AND Material = \'" + material_code + "\'"
        c.execute(sql_cmd)
        result = c.fetchall()[0][0]
        trigger = False if result == 0 else True
        conn.commit()
        conn.close()
        return trigger

    def __remove_inv_tbl(self, db_date):
        table_name = "INV" + db_date
        conn = sqlite3.connect(self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db")
        c = conn.cursor()
        sql_cmd = "DROP TABLE " + table_name
        c.execute(sql_cmd)
        conn.commit()
        conn.close()
        print(">> Table %s is deleted." % table_name)

    # import oneclick inventory data into database
    def oneclick_inventory_import(self, str_date):
        data_file_fullname = self.oneclick_path + str_date + "\\OneClick_Inventory_Projection_Report _" \
                             + str_date + ".csv"
        try:
            df = pd.read_csv(data_file_fullname, sep='|', encoding='gb18030')
        except FileNotFoundError:
            print("INV%s reading fail. " % str_date)
            return
        df_single_bu = df.loc[(df['Business_Unit'] == self.__class__.bu_name) & (df['Loc'] == "Total")]
        database_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(database_name)
        df_single_bu.to_sql("INV" + str_date, con=conn, if_exists="replace", index=False)
        print(">>INV%s was imported. " % str_date)
        pass

    # 获取当天库存
    def today_inv(self):
        print("===Current Inventory List by Hierarchy_5===")
        # 获取日期
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = '''SELECT Hierarchy_5, sum(Available_Stock * Standard_Cost) AS onhand_inv, 
                        sum((GIT_1_Week + GIT_2_Week + GIT_3_Week + GIT_4_Week) * Standard_Cost) AS GIT_inv,
                        sum(Open_PO * Standard_Cost) As Open_PO_inv, 
                        sum(Pending_Inventory_Bonded_Total_Qty * Standard_Cost) AS BD_Pending_Value,
                        sum(Pending_Inventory_NonB_Total_Qty * Standard_Cost) AS NB_Pending_Value from ''' + table_name + ''' 
                        WHERE (Available_Stock + GIT_1_Week + GIT_2_Week + Pending_Inventory_Bonded_Total_Qty + Pending_Inventory_NonB_Total_Qty) > 0  
                        GROUP BY Hierarchy_5 ORDER BY onhand_inv DESC'''
        c.execute(sql_cmd)
        inventory_output = c.fetchall()
        # calculate inventory total value.
        total_available_stock_value, total_useful_stock_value, total_stock_value = 0, 0, 0
        for item in inventory_output:
            total_available_stock_value += item[1]
            total_useful_stock_value += item[1] + item[2]
            total_stock_value += item[1] + item[2] + item[4] + item[5]
        title = [("Hierarchy_5", "Available Stock", "GIT Inventory", "Open PO Value", "Bonded Pending",
                  "Non-bonded Pending")]
        result = title + inventory_output
        print(tabulate(result, headers="firstrow", tablefmt="psql", showindex=range(1, len(result)), floatfmt=",.0f"))
        print("Total Available Stock Value: RMB - %s, USD - %s"
              % (format(total_available_stock_value, ",.0f"),
                 format(total_available_stock_value / self.__class__.currency_rate, ",.0f")))
        print("Total Useful Stock Value: RMB - %s, USD - %s"
              % (format(total_useful_stock_value, ',.0f'),
                 format(total_useful_stock_value / self.__class__.currency_rate, ',.0f')))
        print("Total Stock Value: RMB - %s, USD - %s"
              % (format(total_stock_value, ',.0f'), format(total_stock_value / self.__class__.currency_rate, ',.0f')))

    # 获取当前BO
    def get_current_bo(self):
        print("===Current Backorder List===")
        # 获取日期
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = '''select Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty, 
                        (Current_Backorder_Qty * Standard_Cost) as bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                        GIT_4_Week, Open_PO from ''' + table_name + ''' 
                        WHERE Current_Backorder_Qty > 0 ORDER by CSC DESC, bo_value DESC'''
        c.execute(sql_cmd)
        bo_output = c.fetchall()
        # 连接master data数据库
        master_data_db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        master_data_table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(master_data_db_name)
        c = conn.cursor()
        # 读取SAP Price并计算价格
        bo_result = []
        for bo_item in bo_output:
            bo_material = bo_item[0]
            sql_cmd = "SELECT Price from " + master_data_table_name + " WHERE Material = \'" + bo_material + "\'"
            c.execute(sql_cmd)
            result = c.fetchall()
            try:
                bo_price = result[0][0]
            except IndexError:
                bo_price = 0
            bo_item_list = list(bo_item)
            bo_item_list[5] = bo_item_list[4] * bo_price
            bo_result.append(tuple(bo_item_list))
        # 输出总数
        bo_qty_sum, bo_value_sum = 0, 0
        for item in bo_result:
            bo_qty_sum += item[4]
            bo_value_sum += item[5]
        print("=== Current Backorder Quantity %s, Value RMB %s ===" % (int(bo_qty_sum), format(bo_value_sum, ",.0f")))
        # 输入表格
        title = [('Material', 'Description', 'Hierarchy_5', 'CSC', 'Qty', 'Value', 'GIT_1', 'GIT_2', 'GIT_3', 'GIT_4',
                  'Open_PO')]
        final_result = title + bo_result
        print(tabulate(final_result, headers="firstrow", tablefmt="github", showindex=range(1, len(final_result)), floatfmt=",.0f"))
        conn.commit()
        conn.close()

    # 导出backorder给平台
    def export_backorder_data(self):
        # print title
        print("===Export Backorder Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = self._get_newest_date() if inventory_date == "" else "INV" + inventory_date
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        sql_cmd = '''SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty,
                    (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                    (GIT_4_Week + Open_PO) AS not_delivered_qty FROM ''' + table_name + ''' 
                    WHERE Current_Backorder_Qty > 0 ORDER by bo_value DESC'''
        df = pd.read_sql(sql=sql_cmd, con=conn)
        df = df.drop(columns=["bo_value", ])
        df = df.rename(columns={"Material": "代码", "Description": "英文描述", "Hierarchy_5": "产品分类",
                                "Current_Backorder_Qty": "缺货数量", "GIT_1_Week": "2周左右", "GIT_2_Week": "3-4周",
                                "GIT_3_Week": "6-8周", "not_delivered_qty": "已下订单"})
        backorder_file = self.__class__.backorder_path + "Backorder_" + table_name[3:] + ".xlsx"
        df.to_excel(backorder_file, index=False)
        print("Backorder detail exported to " + backorder_file)

    # export inventory file
    def export_inventory_data(self):
        # print title
        print("===Export Inventory Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        sql_cmd = '''SELECT Material, Description, Available_Stock FROM ''' + table_name + ''' WHERE Available_Stock !=0'''
        df = pd.read_sql(sql=sql_cmd, con=conn)
        df = df.rename(columns={"Material": "代码", "Description": "英文描述", "Available_Stock": "可用数量"})
        inventory_file = self.__class__.inventory_path + "Inventory_" + table_name[3:] + ".xlsx"
        df.to_excel(inventory_file, index=False)
        print("Inventory detail exported to " + inventory_file)
        pass

    # display backorder value trend by day
    def display_backorder_trend(self):
        # print title
        print("===Display Backorder Trend===")
        # get table list
        print("---Get Backorder Data---")
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name")
        table_list = [item[0] for item in c.fetchall()]
        date_list = [item[-4:] for item in table_list]
        # generate backorder summary data from every table
        daily_backorder_summary = []
        for table_name in table_list:
            sql_cmd = "SELECT Material, CSC, Current_Backorder_Qty FROM " + table_name + \
                      " WHERE Current_Backorder_Qty > 0"
            c.execute(sql_cmd)
            daily_backorder_summary.append(c.fetchall())
        conn.close()
        # get selling price
        # generate final list for backorder value
        backorder_value_summary = [[], [], []]
        print("---Generate Value with Selling Price---")
        db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        for item_day in daily_backorder_summary:
            # initiate daily backorder value summary dict
            daily_backorder_total_value = {'ROP': 0, 'IND': 0, 'ND': 0}
            for item_code in item_day:
                material_code = item_code[0]
                sql_cmd = "SELECT Price FROM " + data_table_name + " WHERE Material = \"" + material_code + "\""
                c.execute(sql_cmd)
                try:
                    item_backorder_value = int(c.fetchall()[0][0] * item_code[2])
                # if cannot find price
                except IndexError:
                    item_backorder_value = 0
                # sum up backorder value based on CSC
                if item_code[1] == "IND":
                    daily_backorder_total_value['IND'] += item_backorder_value
                elif item_code[1] == "ROP":
                    daily_backorder_total_value['ROP'] += item_backorder_value
                else:
                    daily_backorder_total_value['ND'] += item_backorder_value
            # sum up to summary list with daily value
            backorder_value_summary[0].append(daily_backorder_total_value['IND'])
            backorder_value_summary[1].append(daily_backorder_total_value['ROP'])
            backorder_value_summary[2].append(daily_backorder_total_value['ND'])
        chart.backorder_trend_chart(date_list, backorder_value_summary)

    # Daily pending inventory trend display
    def get_pending_trend(self, data_type="value"):
        print("===Display Pending Inventory Trend===")
        pending_result = []
        # 链接数据库
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")
        tbl_list = c.fetchall()
        # generate date list in MMDD format for following chart display
        date_list = [item[0][-4:] for item in tbl_list]
        for table_name in tbl_list:
            sql_cmd = '''SELECT sum(Pending_Inventory_Bonded_Total_Qty), sum(Pending_Inventory_NonB_Total_Qty), 
            sum((Standard_Cost * Pending_Inventory_Bonded_Total_Qty)) As Pending_BD_Value, 
            sum((Standard_Cost * Pending_Inventory_NonB_Total_Qty)) As Pending_NB_Value from ''' + table_name[0]
            c.execute(sql_cmd)
            pending_result.append(c.fetchall()[0])
        # group data with different category
        pending_summary_bonded_qty = [item[0] for item in pending_result]
        pending_summary_nonbonded_qty = [item[1] for item in pending_result]
        pending_summary_bonded_value = [int(item[2]) for item in pending_result]
        pending_summary_nonbonded_value = [int(item[3]) for item in pending_result]
        # call chart
        if data_type == "value":
            chart.pending_inventory_trend_chart(date_list,
                                                [pending_summary_bonded_value, pending_summary_nonbonded_value],
                                                "Pending Inventory Trend (Value in RMB)")
        else:
            chart.pending_inventory_trend_chart(date_list,
                                                [pending_summary_bonded_qty, pending_summary_nonbonded_qty],
                                                "Pending Inventory Trend (by Quantity)")

    # 查询单个代码
    def get_code_inv(self):
        print("===Single Code Inventory===")
        # 获取日期
        code_name = input("Input Material Code: ").upper()
        # check if this code exist in material master
        while not self.check_code(code_name):
            code_name = input("Wrong code, please re-input: ").upper()
        # start to get inventory data from oneclick database
        str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        table_name = self._get_newest_date() if str_input == "" else "INV" + str_input
        # check if this date exist in newest oneclick file
        while not self._check_date_availability(table_name):
            print("!!Error - Wrong date, Please re-input! ")
            str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
            table_name = self._get_newest_date() if str_input == "" else "INV" + str_input
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Description, Hierarchy_5, Available_Stock, Pending_Inventory_Bonded_Total_Qty, " \
                  "Pending_Inventory_NonB_Total_Qty, CSC, GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, " \
                  "Standard_Cost, Average_Selling_Price FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
        c.execute(sql_cmd)
        result = c.fetchall()[0]
        title = ["Material", "Description", "Hierarchy_5", "Available_Stock", "Pending_Qty_BD",
                 "Pending_Qty_NB", "CSC", "GIT_1_Qty", "GIT_2_Qty", "GIT_3_Qty", "GIT_4_Qty", "Std Cost",
                 "AVG Selling Price"]
        code_inv_output = [["Item", "Value"]]
        for i in range(len(result)):
            if isinstance(result[i], str):
                code_inv_output.append([title[i], result[i]])
            else:
                code_inv_output.append([title[i], int(result[i])])
        print(tabulate(code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="github"))
    
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
            conn.commit()
            conn.close()
            # print charter
            x_value = [item[-4:] for item in tbl_list]
            chart.line_chart(code_name, x_value, inv_result, "Date", "INV Qty", "Inventory Trend of " + code_name)
        else:
            print("!!Error - This Material Code does NOT exist, Please re-input! ")

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
            print("!!Error, No such Hierarchy_5 name. Please try again!")
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

    # 显示某个H5的库存明细
    def display_h5_inv_detail(self):
        print("===Hierarchy_5 Inventory Detail List===")
        # Get H5 Name
        h5_input = input("Input Hierarchy_5 Name : ")
        h5_infocheck = calculation.InfoCheck(self.__class__.bu_name)
        h5_name = h5_infocheck.get_h5_name(h5_input)
        # if not right h5 name, return
        if h5_name == "NULL":
            print("No such Hierarchy_5 name and please try again!~")
            return
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        # generate title
        table_title = [("Material", "Description", "CSC", "Available Stock", "Onhand_INV_Value", "Bonded Pending",
                        "GIT_1_Week", "GIT_2_Week", "GIT_3_Week", "GIT_4_Week"),]
        # Connect to database
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Description, CSC, Available_Stock, (Standard_Cost * Inventory_OnHand) as " \
                  "Onhand_INV_Value, Pending_Inventory_Bonded_Total_Qty, GIT_1_Week, GIT_2_Week, GIT_3_Week, " \
                  "GIT_4_Week FROM " + table_name + " WHERE Hierarchy_5 = \"" + h5_name.upper() + \
                  "\" AND Available_Stock != 0 ORDER by Material"
        c.execute(sql_cmd)
        result = c.fetchall()
        # calculate total inventory value
        total_inv_value = 0
        for item in result:
            total_inv_value += item[4]
        print("Total Inventory Value of " + h5_name + " is %s" % (format(total_inv_value, ",.0f")))
        # print the list
        result_to_print = table_title + result
        print(tabulate(result_to_print, headers="firstrow", tablefmt="github", showindex=range(1, len(result_to_print)),
                       floatfmt=",.0f"))

    # data mapping for a list of codes
    def inventory_mapping(self):
        print("===Inventory Status Mapping with Lists===")
        # read code list
        file_fullname = "../data/_Source_Data/Data_Mapping.txt"
        try:
            fo = open(file_fullname, "r")
        except FileNotFoundError:
            print("!Error, please make sure you have put Data_Mapping.txt under _Source_Data folder")
            return
        code_list = [item.strip() for item in fo.readlines()]
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = self._get_newest_date()
        else:
            table_name = "INV" + inventory_date
        if not self._check_date_availability(table_name):
            print("!Error, please make sure you input the correct date.")
            return
        # connect to database and get the inventory data
        inventory_result = [["Material", "Description", "Hierarchy_5", "CSC", "Available_Stock", "Pending_Qty_BD",
                             "Pending_Qty_NB", "GIT_1_Qty", "GIT_2_Qty", "GIT_3_Qty", "GIT_4_Qty", "Open_PO"], ]
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = "SELECT Material, Description, Hierarchy_5, CSC, Available_Stock, " \
                      "Pending_Inventory_Bonded_Total_Qty, Pending_Inventory_NonB_Total_Qty, GIT_1_Week, GIT_2_Week, " \
                      "GIT_3_Week, GIT_4_Week, Open_PO FROM " + table_name + " WHERE Material = \'" + code_item + "\'"
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                inventory_result.append(result[0])
            else:
                inventory_result.append([code_item, ])
        conn.commit()
        conn.close()
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result)), floatfmt=",.0f"))

    # 数据同步
    def inv_data_sync(self, sync_days):
        print("===Sync Current Inventory Data from Oneclick===")
        # 设置例外清单
        lst_xcpt = ['20190118', ]
        onclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
        lst_folder_temp = []
        # 读取oneclick目录下文件夹清单
        try:
            for file_name in os.listdir(onclick_path):
                if os.path.isdir(onclick_path + file_name):
                    lst_folder_temp.append(file_name)
        except FileNotFoundError:
            print("!Error, the sharefolder cannot be opened. Make sure you've connected to JNJ network and try again.")
            return
        # 排序
        lst_folder_temp.sort()
        # 读取后N天, lst_folder为共享盘上数据
        lst_folder_sharepoint = lst_folder_temp[0 - sync_days:]
        # 读取现有数据
        lst_db_date = self.get_tbl_list()
        # crt_list为现有数据
        lst_current_database = [item.lstrip("INV") for item in lst_db_date]
        # 开始对比数据
        # 删除过期数据
        for item in lst_current_database:
            if item not in lst_folder_sharepoint:
                self.__remove_inv_tbl(item)
                lst_current_database.remove(item)
        # 导入新的数据
        for item in lst_folder_sharepoint:
            if (item not in lst_current_database) and (item not in lst_xcpt):
                self.oneclick_inventory_import(item)
        print(">> Synchronization succeed!")

    # Display command list
    @staticmethod
    def show_command_list():
        import public_function
        public_function.display_command_list("current_inventory_command")


if __name__ == "__main__":
    test = CurrentInventory("TU")
    test.inventory_mapping()
    # test.inv_data_sync(50)
