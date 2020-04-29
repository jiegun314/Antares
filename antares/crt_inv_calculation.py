import sqlite3
# import pandas as pd
# import numpy as np
from tabulate import tabulate
import draw_chart as chart
import os
import public_function as pb_func
import pandas as pd


class CurrentInventoryCalculation:
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    currency_rate = 7.0842

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # 获取最新日期
    def get_newest_date(self):
        conn = sqlite3.connect(self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db")
        c = conn.cursor()
        c.execute("select name from sqlite_master where type='table' order by name")
        lst_date = [item[0] for item in c.fetchall()]
        # lst_date.sort(reverse=True)
        conn.commit()
        conn.close()
        return lst_date[-1]

    # 检查日期是否存在
    def check_date_availability(self, table_name):
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

    # import oneclick inventory data into database
    def oneclick_inventory_import(self, str_date):
        data_file_fullname = self.oneclick_path + str_date + "\\OneClick_Inventory_Projection_Report _" \
                             + str_date + ".csv"
        try:
            df = pd.read_csv(data_file_fullname, sep='|', encoding='gb18030')
        except FileNotFoundError:
            return -1
        df_single_bu = df.loc[(df['Business_Unit'] == self.__class__.bu_name) & (df['Loc'] == "Total")]
        database_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(database_name)
        df_single_bu.to_sql("INV" + str_date, con=conn, if_exists="replace", index=False)
        return 1

    # calculate current inventory, return detail list and summary result
    def get_current_inventory(self, table_name):
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
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            inventory_output = [(0, 0, 0, 0, 0, 0)]
        else:
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
        return [result, [total_available_stock_value, total_useful_stock_value, total_stock_value]]

    # 获取当前BO
    def get_current_bo(self, table_name):
        title = [('Material', 'Description', 'Hierarchy_5', 'CSC', 'Qty', 'Value', 'GIT_1', 'GIT_2', 'GIT_3', 'GIT_4',
                  'Open_PO')]
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = '''select Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty, 
                        (Current_Backorder_Qty * Standard_Cost) as bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                        GIT_4_Week, Open_PO from ''' + table_name + ''' 
                        WHERE Current_Backorder_Qty > 0 ORDER by CSC DESC, bo_value DESC'''
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            return title + [tuple(["-", "-", "-", "Total", 0, 0, 0, 0, 0, 0])]
        else:
            bo_output = c.fetchall()
        # 连接master data数据库
        master_data_db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        master_data_table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(master_data_db_name)
        c = conn.cursor()
        # create list for final total
        # format - [ttl_qty, ttl_value, git1_fulfill, git2_fulfill, git3_fulfill, git4_fulfill, oo_fulfill]
        backorder_summary_list = [0, 0, 0, 0, 0, 0, 0]
        # 读取SAP Price并计算价格
        bo_result = []
        for bo_item in bo_output:
            bo_material, bo_qty, git1_fulfill_qty, git2_fulfill_qty, git3_fulfill_qty, git4_fulfill_qty, oo_fulfill_qty \
                = bo_item[0], bo_item[4], bo_item[6], bo_item[7], bo_item[8], bo_item[9], bo_item[10]
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
            # calculate total
            backorder_summary_list[0] += bo_qty
            backorder_summary_list[1] += bo_item_list[5]
            # git1 fulfill
            backorder_summary_list[2] += min([bo_qty, git1_fulfill_qty]) * bo_price
            # git2 fulfill
            backorder_summary_list[3] += min([max(bo_qty - git1_fulfill_qty, 0), git2_fulfill_qty]) * bo_price
            # git3 fulfill
            backorder_summary_list[4] += min(
                [max(bo_qty - git1_fulfill_qty - git2_fulfill_qty, 0), git3_fulfill_qty]) * bo_price
            # git4 fulfill
            backorder_summary_list[5] += min(
                [max(bo_qty - git1_fulfill_qty - git2_fulfill_qty - git3_fulfill_qty, 0), git4_fulfill_qty]) * bo_price
            # open order fulfill
            backorder_summary_list[6] += min(
                [max(bo_qty - git1_fulfill_qty - git2_fulfill_qty - git3_fulfill_qty - git4_fulfill_qty, 0),
                 oo_fulfill_qty]) * bo_price

        conn.commit()
        conn.close()
        return title + bo_result + [tuple(["-", "-", "-", "Total"] + backorder_summary_list)]

    # 导出backorder给平台
    def export_backorder_data(self, table_name):
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        sql_cmd = '''SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty,
                    (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                    (GIT_4_Week + Open_PO) AS not_delivered_qty FROM ''' + table_name + ''' 
                    WHERE Current_Backorder_Qty > 0 ORDER by bo_value DESC'''
        try:
            df = pd.read_sql(sql=sql_cmd, con=conn)
        except pd.io.sql.DatabaseError:
            return 0
        else:
            df = df.drop(columns=["bo_value", ])
            df = df.rename(columns={"Material": "代码", "Description": "英文描述", "Hierarchy_5": "产品分类",
                                    "Current_Backorder_Qty": "缺货数量", "GIT_1_Week": "2周左右", "GIT_2_Week": "3-4周",
                                    "GIT_3_Week": "6-8周", "not_delivered_qty": "已下订单"})

            return df

    # export inventory file
    def export_inventory_data(self, table_name):
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        if self.__class__.bu_name == "TU":
            sql_cmd = '''SELECT Material, Description, Available_Stock FROM ''' + table_name + \
                      ''' WHERE Available_Stock !=0'''
        else:
            sql_cmd = '''SELECT Material, Description, Available_Stock, Pending_Inventory_Bonded_Total_Qty, 
            GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_3_Week, Open_PO FROM ''' + table_name + \
                      ''' WHERE Available_Stock !=0'''
        try:
            df = pd.read_sql(sql=sql_cmd, con=conn)
        except pd.io.sql.DatabaseError:
            return 0
        else:
            if self.__class__.bu_name == "TU":
                df = df.rename(columns={"Material": "代码", "Description": "英文描述", "Available_Stock": "可用数量"})
            return df

    # display backorder value trend by day
    def generate_backorder_trend(self):
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
        # chart.backorder_trend_chart(date_list, backorder_value_summary)
        chart.backorder_trend_line_chart(date_list, backorder_value_summary)

    # calculate long aging backorders
    def calculate_aging_backorder(self, exception_list):
        # get table list
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name DESC")
        table_list = [item[0] for item in c.fetchall()]
        current_day_table = table_list.pop(0)
        # get newest backorder
        sql_cmd = "SELECT Material FROM " + current_day_table + " WHERE Current_Backorder_Qty > 0"
        c.execute(sql_cmd)
        backorder_code_list = [item[0] for item in c.fetchall()]
        # set up tracing list with code, backorder days, open_status
        # print("---Start to map backorder historical data---")
        backorder_tracing_list = []
        for item in backorder_code_list:
            backorder_tracing_list.append([item, 1, "Y"])
        # trace back for backorder
        for table_item in table_list:
            if table_item in exception_list:
                continue
            for code_item in backorder_tracing_list:
                if code_item[2] == "Y":
                    sql_cmd = "SELECT Current_Backorder_Qty FROM " + table_item + " WHERE Material = \'" \
                              + code_item[0] + "\'"
                    c.execute(sql_cmd)
                    backorder_result = c.fetchall()
                    backorder_qty = backorder_result[0][0] if backorder_result else 0
                    # if the backorder qty is positive, just add count for days, else remove from counting list
                    if backorder_qty > 0:
                        code_item[1] += 1
                    else:
                        code_item[2] = "N"
            # print("Backorder mapping of %s - Done." % table_item)
            print(">", end="", flush=True)
        backorder_tracing_list.sort(key=self.take_quantity, reverse=True)
        print("")
        # get current day information
        backorder_output = []
        for backorder_item in backorder_tracing_list:
            sql_cmd = "SELECT Description, Hierarchy_5, CSC, Current_Backorder_Qty, " \
                      "sum(GIT_1_Week + GIT_2_Week + GIT_3_Week + GIT_4_Week) as GIT_Qty, Open_PO FROM " + \
                      current_day_table + " WHERE Material = \'" + backorder_item[0] + "\'"
            c.execute(sql_cmd)
            result_temp = list(c.fetchall()[0])
            # add alert trigger based on GIT and Open Order quantity
            if result_temp[3] > (result_temp[4] + result_temp[5]) and result_temp[2] == "IND":
                alert_trigger = "***"
            elif result_temp[3] > (result_temp[4] + result_temp[5]) and result_temp[2] == "ROP":
                alert_trigger = "###"
            elif result_temp[3] > result_temp[4]:
                alert_trigger = "---"
            else:
                alert_trigger = " "
            backorder_output.append([backorder_item[1], alert_trigger, backorder_item[0]] + result_temp)
        # print out
        list_header = [
            ["BO Days", "Alert", "Material", "Description", "Hierarchy_5", "CSC", "BO Qty", "GIT Qty", "Open PO"], ]
        aging_backorder_list = list_header + backorder_output
        return [aging_backorder_list, len(table_list)]

    @staticmethod
    def take_quantity(elem):
        return elem[1]

    # Daily pending inventory trend display
    def generate_pending_trend(self, data_type="value"):
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
    def get_code_inv(self, code_name, table_name):
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Description, Hierarchy_5, Available_Stock, Pending_Inventory_Bonded_Total_Qty, " \
                  "Pending_Inventory_NonB_Total_Qty, CSC, GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, Open_PO, " \
                  "Standard_Cost FROM " + table_name + " WHERE Material = \'" + code_name + "\'"
        c.execute(sql_cmd)
        result = c.fetchall()[0]
        title = ["Material", "Description", "Hierarchy_5", "Available_Stock", "Pending_Qty_BD",
                 "Pending_Qty_NB", "CSC", "GIT_1_Qty", "GIT_2_Qty", "GIT_3_Qty", "GIT_4_Qty", "Open_PO", "Std Cost"]
        code_inv_output = [["Item", "Value"]]
        for i in range(len(result)):
            if isinstance(result[i], str):
                code_inv_output.append([title[i], result[i]])
            elif result[i] is None:
                code_inv_output.append([title[i], "None"])
            else:
                code_inv_output.append([title[i], int(result[i])])
        return code_inv_output

    # 查询单个代码可用库存趋势
    def generate_code_inv_trend(self, code_name):
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

    # 查询H5库存趋势
    def generate_h5_inventory_trend(self, h5_result):
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
    def get_h5_inv_detail(self, h5_name, table_name):
        # generate title
        table_title = [("Material", "Description", "CSC", "Available Stock", "Onhand_INV_Value", "Bonded Pending",
                        "GIT_1_Week", "GIT_2_Week", "GIT_3_Week", "GIT_4_Week"), ]
        # Connect to database
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Description, CSC, Available_Stock, (Standard_Cost * Inventory_OnHand) as " \
                  "Onhand_INV_Value, Pending_Inventory_Bonded_Total_Qty, GIT_1_Week, GIT_2_Week, GIT_3_Week, " \
                  "GIT_4_Week FROM " + table_name + " WHERE Hierarchy_5 = \"" + h5_name.upper() + \
                  "\" AND Available_Stock != 0 ORDER by Material"
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            result = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
        else:
            result = c.fetchall()
        # calculate total inventory value
        total_inv_value = 0
        for item in result:
            total_inv_value += item[4]
        # return value
        return [table_title + result, total_inv_value]

    # display alert for those key codes with low stock
    def get_low_inventory_alert(self, alert_month=1):
        # get ranking A, B code list
        master_data_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        inventory_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_CRT_INV.db'
        conn = sqlite3.connect(master_data_db_fullname)
        c = conn.cursor()
        c.execute('SELECT Material, IMS_Quantity FROM Ranking WHERE Ranking in (\"A\", \"B\") ')
        ranking_ab_list = c.fetchall()
        # get inventory and judge if low stock
        conn = sqlite3.connect(inventory_db_fullname)
        c = conn.cursor()
        table_name = self.get_newest_date()
        inventory_list_title = ['Material', 'Description', 'H5', 'Available_Stock', 'GIT_Quantity', 'Stock_Month',
                                'Total_Stock_Month']
        inventory_alert_list, inventory_alert_result = [], []
        for item in ranking_ab_list:
            material_name, ims_quantity = item[0], item[1]
            sql_cmd = 'SELECT Material, Description, Hierarchy_5, Available_Stock, (GIT_1_Week + GIT_2_Week + ' \
                      'GIT_3_Week + GIT_4_Week) as GIT_Quantity FROM ' + table_name + ' WHERE Material = \"' + \
                      material_name + '\"'
            c.execute(sql_cmd)
            inventory_result = list(c.fetchall()[0])
            inventory_result.append(inventory_result[3] * 6 / ims_quantity)
            inventory_result.append(inventory_result[4] * 6 / ims_quantity)
            if inventory_result[-2] <= alert_month:
                inventory_alert_list.append(inventory_result)
        if self.__class__.bu_name != "TU":
            inventory_alert_result.insert(0, inventory_list_title)
            return inventory_alert_list
        else:
            # remove phoenix codes from list
            conn = sqlite3.connect(master_data_db_fullname)
            c = conn.cursor()
            for item in inventory_alert_list:
                material_name = item[0]
                sql_cmd = 'SELECT count(*) FROM TU_Phoenix_List WHERE [Exit SKU] = \"' + material_name + '\"'
                c.execute(sql_cmd)
                # if material code found in phoenix list
                if c.fetchall()[0][0] == 0:
                    inventory_alert_result.append(item)
            inventory_alert_result.insert(0, inventory_list_title)
            return inventory_alert_result

    # data mapping for a list of codes
    def inventory_mapping(self, code_list, table_name):
        # connect to database and get the inventory data
        inventory_result = [["Material", "Description", "Hierarchy_5", "CSC", "Available_Stock", "Pending_Qty_BD",
                             "Pending_Qty_NB", "GIT_1_Qty", "GIT_2_Qty", "GIT_3_Qty", "GIT_4_Qty", "Open_PO"], ]
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = "SELECT Material, Description, Hierarchy_5, CSC, Available_Stock, " \
                      "Pending_Inventory_Bonded_Total_Qty, Pending_Inventory_NonB_Total_Qty, GIT_1_Week, GIT_2_Week, " \
                      "GIT_3_Week, GIT_4_Week, Open_PO FROM " + table_name + " WHERE Material = \'" + code_item.upper() + "\'"
            try:
                c.execute(sql_cmd)
            except sqlite3.OperationalError:
                result = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
            else:
                result = c.fetchall()
            if result:
                inventory_result.append(result[0])
            else:
                inventory_result.append([code_item, ])
        conn.commit()
        conn.close()
        # fill material code with blank
        return inventory_result

    # 数据同步
    def inv_data_sync(self, sync_days, lst_xcpt):
        onclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
        lst_folder_temp = []
        import_success_count, import_fail_count = 0, 0
        # 读取oneclick目录下文件夹清单
        try:
            for file_name in os.listdir(onclick_path):
                if os.path.isdir(onclick_path + file_name):
                    lst_folder_temp.append(file_name)
        except FileNotFoundError:
            return "ERROR"
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
                import_result = self.oneclick_inventory_import(item)
                if import_result == 1:
                    import_success_count += 1
                else:
                    import_fail_count += 1
        most_updated_table = self.get_tbl_list()[-1]
        return [import_success_count, import_fail_count, most_updated_table]


if __name__ == "__main__":
    test = CurrentInventoryCalculation("TU")
    test.get_code_inv('04.210.116TS', 'INV20200428')
    # test.inv_data_sync(50)
