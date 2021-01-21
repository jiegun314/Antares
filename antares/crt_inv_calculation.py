import sqlite3
import numpy as np
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
    update_file_path = "../data/_Update/"
    # oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    oneclick_path = '//jnjcnckapdfs11.ap.jnj.com/jnjcnmpdfsroot/COMPASS/Oneclick Inventory Report/Output/'
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
        sql_cmd = 'SELECT count(Material) FROM %s WHERE Business_Unit=\"%s\" ' \
                  'AND Material = \"%s\"' % (table_name, self.__class__.bu_name, material_code)
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
    def import_oneclick_inventory(self, str_date):
        data_file_fullname = self.oneclick_path + str_date + "\\OneClick_Inventory_Projection_Report _" \
                             + str_date + ".csv"
        try:
            df = pd.read_csv(data_file_fullname, sep='|', encoding='latin1')
        except FileNotFoundError:
            return -1
        # combine dps spine and synthes spine
        df.loc[df['Business_Unit'] == 'SP', 'Business_Unit'] = 'Spine'
        df.loc[df['Business_Unit'] == 'SPINE', 'Business_Unit'] = 'Spine'
        df_single_bu = df.loc[(df['Business_Unit'] == self.__class__.bu_name) & (df['Loc'] == "Total")]
        # mapping local Hierarchy
        if self.__class__.bu_name == 'JT':
            df_single_bu = self.map_local_hierarchy(df_single_bu)
        database_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(database_name)
        df_single_bu.to_sql("INV" + str_date, con=conn, if_exists="replace", index=False)
        return 1

    # import all dps inventory data to database
    def import_all_dps_oneclick_inventory(self, str_date):
        data_file_fullname = self.oneclick_path + str_date + "\\OneClick_Inventory_Projection_Report _" \
                             + str_date + ".csv"
        try:
            df = pd.read_csv(data_file_fullname, sep='|', encoding='gbk', index_col='Material')
        except FileNotFoundError:
            return -1
        # combine dps spine and synthes spine
        df.loc[df['Business_Unit'] == 'SP', 'Business_Unit'] = 'Spine'
        df.loc[df['Business_Unit'] == 'SPINE', 'Business_Unit'] = 'Spine'
        # select dps products
        df_dps = df.loc[(df['Business_Group'] == 'Orthopedics') & (df['Loc'] == "Total")]
        # map with JT local Hierarchy
        database_jt = self.__class__.db_path + 'JT_Master_Data.db'
        local_hierarchy_datasheet = 'JT_Local_Hierarchy'
        conn = sqlite3.connect(database_jt)
        sql_cmd = 'SELECT Material, Local_Hierarchy FROM ' + local_hierarchy_datasheet
        df_local_hierarchy = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        df_dps = df_dps.join(df_local_hierarchy)
        df_dps.loc[df_dps['Local_Hierarchy'].notnull(), 'Hierarchy_5'] = df_dps['Local_Hierarchy']
        df_dps.drop(columns=['Local_Hierarchy'], inplace=True)
        df_dps.reset_index(inplace=True)
        # export to database
        database_output = self.__class__.db_path + "oneclick_inventory_dps.db"
        conn = sqlite3.connect(database_output)
        df_dps.to_sql("INV" + str_date, con=conn, if_exists="replace", index=False)
        return 1

    # mapping local hierarchy
    def map_local_hierarchy(self, df_input):
        # get local hierarchy
        df_input.set_index('Material', inplace=True)
        database_name = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        local_hierarchy_datasheet = self.__class__.bu_name + '_Local_Hierarchy'
        conn = sqlite3.connect(database_name)
        sql_cmd = 'SELECT Material, Local_Hierarchy FROM ' + local_hierarchy_datasheet
        df_local_hierarchy = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # join the local hierarchy and replace current h5
        df_output = df_input.join(df_local_hierarchy)
        df_output.loc[df_output['Local_Hierarchy'].notnull(), 'Hierarchy_5'] = df_output['Local_Hierarchy']
        df_output.drop(columns=['Local_Hierarchy'], inplace=True)
        df_output.reset_index(inplace=True)
        # print(df_output.head())
        return df_output

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
        if self.__class__.bu_name == 'TU':
            sql_cmd = '''SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty,
                        (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, 
                        (GIT_4_Week + Open_PO) AS not_delivered_qty FROM ''' + table_name + ''' 
                        WHERE Current_Backorder_Qty > 0 ORDER by bo_value DESC'''
        else:
            sql_cmd = '''SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty, 
            (Current_Backorder_Qty * Standard_Cost) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, 
            Open_PO FROM ''' + table_name + ''' WHERE Current_Backorder_Qty > 0 ORDER by bo_value DESC'''
        try:
            df = pd.read_sql(sql=sql_cmd, con=conn)
        except pd.io.sql.DatabaseError:
            return 0
        else:
            df = df.drop(columns=["bo_value", ])
            if self.__class__.bu_name == 'TU':
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
            sql_cmd = '''SELECT Material, Description, CSC, Available_Stock, Pending_Inventory_Bonded_Total_Qty, 
            GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, Open_PO FROM ''' + table_name
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
        return [date_list, backorder_value_summary]
        # chart.backorder_trend_line_chart(date_list, backorder_value_summary, self.__class__.bu_name)

    # generate aging backorder list by pandas
    # return the list of information by row including title and the length of data
    def generate_aging_backorder_list(self, exception_list=[]) -> list:
        # get table list
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name DESC")
        table_list = [item[0] for item in c.fetchall()]
        # get most fresh day as base
        current_day_table = table_list.pop(0)
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty, ' \
                  '(GIT_1_Week + GIT_2_Week + GIT_3_Week + GIT_4_Week) as GIT_Qty, Open_PO ' \
                  'FROM %s WHERE Current_Backorder_Qty > 0' % current_day_table
        df_aging_list = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        # add column for counting
        df_aging_list['BO Days'] = 1
        # start to loop by iterator
        for table_item in table_list:
            if table_item in exception_list:
                continue
            sql_cmd = 'SELECT Material, Current_Backorder_Qty as Ongoing_Backorder FROM %s ' \
                      'WHERE Current_Backorder_Qty > 0' % table_item
            df_temp_list = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
            # join and map with current dataframe
            df_aging_list = df_aging_list.join(df_temp_list)
            df_aging_list.fillna(0, inplace=True)
            # judge and add the count
            df_aging_list.loc[df_aging_list['Ongoing_Backorder'] > 0, 'BO Days'] = df_aging_list['BO Days'] + 1
            # drop the temp column
            df_aging_list.drop(columns='Ongoing_Backorder', inplace=True)
        # Add alert column
        df_aging_list['Alert'] = ''
        df_aging_list.loc[df_aging_list['Current_Backorder_Qty'] > df_aging_list['GIT_Qty'], 'Alert'] = '***'
        df_aging_list.loc[df_aging_list['Current_Backorder_Qty'] > (
                df_aging_list['GIT_Qty'] + df_aging_list['Open_PO']), 'Alert'] = '###'
        # sort by backorder days
        df_aging_list.sort_values(by=['BO Days'], ascending=False, inplace=True)
        # remove index and generate list
        df_aging_list.reset_index(inplace=True)
        # reset sequence by column name
        lst_new_column = ["BO Days", "Alert", "Material", "Description", "Hierarchy_5", "CSC", "Current_Backorder_Qty", "GIT_Qty", "Open_PO"]
        df_final = df_aging_list[lst_new_column]
        lst_result = [lst_new_column, ] + df_final.values.tolist()
        return [lst_result, len(table_list)]

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
            chart_title = "Pending Inventory Trend of " + self.__class__.bu_name + " (Value in RMB)"
            chart.pending_inventory_trend_chart(date_list,
                                                [pending_summary_bonded_value, pending_summary_nonbonded_value],
                                                chart_title)
        else:
            chart_title = "Pending Inventory Trend of " + self.__class__.bu_name + " (by Quantity)"
            chart.pending_inventory_trend_chart(date_list,
                                                [pending_summary_bonded_qty, pending_summary_nonbonded_qty],
                                                chart_title)

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

    # check single code inventory with END most updated inventory
    def get_code_inv_with_ned(self, code_name, table_name):
        # get jnj inventory
        lst_jnj_inventory = self.get_code_inv(code_name, table_name)
        # get ned inventory
        df_ned_inventory = self._get_lp_inventory_quantity_list(month='newest')
        try:
            ned_inventory = df_ned_inventory.loc[code_name, 'NED_INV']
        except KeyError:
            ned_inventory = 0
        lst_jnj_inventory.insert(-1, ['NED_INV', ned_inventory])
        return lst_jnj_inventory

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
        chart_title = "Value by Std. Cost of All " + self.__class__.bu_name if h5_result == "ALL" \
            else "Value by Std. Cost of " + h5_result
        chart.line_chart(h5_result, x_value, h5_inv_result, "Date", "Value", chart_title)

    # calculate linear regression
    def get_linear_regression(self, list_data):
        x = np.arange(1, len(list_data) + 1)
        [para_slope, para_intercept] = np.polyfit(x, list_data, 1)
        return [item * para_slope + para_intercept for item in x]

    # display inventory of h5 of both qty and value
    def generate_h5_inventory_trend_two_dimension(self, h5_result):
        # get date list
        table_list = self.get_tbl_list()
        # link to database
        db_name = self.__class__.db_path + self.__class__.bu_name + '_CRT_INV.db'
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        h5_inv_result = []
        for table_item in table_list:
            if h5_result == 'ALL':
                sql_cmd = 'SELECT sum(Available_Stock) AS inv_qty, sum(Available_Stock * Standard_Cost) AS inv_value ' \
                          'FROM ' + table_item
            else:
                sql_cmd = 'SELECT sum(Available_Stock) AS inv_qty, sum(Available_Stock * Standard_Cost) AS inv_value ' \
                          'FROM ' + table_item + ' WHERE Hierarchy_5 = \"' + h5_result.upper() + '\" COLLATE NOCASE'
            c.execute(sql_cmd)
            result = c.fetchone()
            if not result[0]:
                h5_inv_result.append([0, 0])
            else:
                h5_inv_result.append([int(result[0]), int(result[1])])
        x_value = [item[-4:] for item in table_list]
        qty_result = [item[0] for item in h5_inv_result]
        value_result = [item[1] for item in h5_inv_result]
        chart_title = "Qty & Value (by Std. Cost) of All " + self.__class__.bu_name if h5_result == "ALL" \
            else "Qty & Value (by Std. Cost) of " + h5_result
        chart.double_line_chart(h5_result, x_value, qty_result, value_result, 'Date', 'Qty', 'Value', chart_title)

    # 显示某个H5的库存明细
    def get_h5_inv_detail(self, h5_name, table_name):
        # generate title
        table_title = [("Material", "Description", "CSC", "Available Stock", "Onhand_INV_Value", "Bonded Pending",
                        "GIT_1_Week", "GIT_2_Week", "GIT_3_Week", "GIT_4_Week", "Open_PO"), ]
        # Connect to database
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        sql_cmd = "SELECT Material, Description, CSC, Available_Stock, (Standard_Cost * Inventory_OnHand) as " \
                  "Onhand_INV_Value, Pending_Inventory_Bonded_Total_Qty, GIT_1_Week, GIT_2_Week, GIT_3_Week, " \
                  "GIT_4_Week, Open_PO FROM " + table_name + " WHERE Hierarchy_5 = \"" + h5_name.upper() + \
                  "\" COLLATE NOCASE ORDER by Material"
        try:
            c.execute(sql_cmd)
        except sqlite3.OperationalError:
            result = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]
        else:
            result = c.fetchall()
        # calculate total inventory value
        total_inv_value = 0
        for item in result:
            total_inv_value += item[4]
        # return value
        return [table_title + result, total_inv_value]

    # display alert for those key codes with low stock
    def get_low_inventory_alert(self, alert_month=1, inv_month=12):
        # get ranking A, B code list
        master_data_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        master_data_table_name = self.__class__.bu_name + '_Master_Data'
        inventory_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_CRT_INV.db'
        conn = sqlite3.connect(master_data_db_fullname)
        # get AB list
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, Ranking FROM ' + master_data_table_name +\
                  ' WHERE Ranking in (\"A\", \"B\") '
        df_ab_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # get IMS quantity list
        sql_cmd = 'SELECT Material, (IMS_Quantity / %s) as AVG_IMS FROM Ranking WHERE Ranking in (\"A\", \"B\")' % inv_month
        df_ims_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        df_ab_list = df_ab_list.join(df_ims_list)
        # get current update inventory list
        conn = sqlite3.connect(inventory_db_fullname)
        table_name = self.get_newest_date()
        sql_cmd = 'SELECT Material, Available_Stock, (Pending_Inventory_Bonded_Total_Qty + GIT_1_Week + ' \
                  'GIT_2_Week + GIT_3_Week + GIT_4_Week) as GIT_Quantity, Open_PO FROM ' + table_name
        df_inventory_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # Join two list to get inventory of
        df_ab_list = df_ab_list.join(df_inventory_list)
        df_ab_list['CRT_INV_Mth'] = df_ab_list['Available_Stock'] / df_ab_list['AVG_IMS']
        # move column of inventory month after available stock
        col_inv_month = df_ab_list.pop('CRT_INV_Mth')
        df_ab_list.insert(5, 'CRT_INV_Mth', col_inv_month)
        # mapping with lp inventory
        df_lp_inv = self._get_lp_inventory_quantity_list(month='newest')
        df_ab_list = df_ab_list.join(df_lp_inv)
        df_ab_list.fillna(0, inplace=True)
        # calculate total inventory
        df_ab_list['JNJ_Actual_INV'] = df_ab_list['Available_Stock']
        df_ab_list.loc[df_ab_list['Available_Stock'] < 0, 'JNJ_Actual_INV'] = 0
        df_ab_list['Total_INV'] = df_ab_list['JNJ_Actual_INV'] + df_ab_list['NED_INV']
        # delete unuseful column
        df_ab_list = df_ab_list.drop(['AVG_IMS', 'JNJ_Actual_INV'], axis=1)
        # filter and sort
        df_low_inventory = df_ab_list.loc[df_ab_list['CRT_INV_Mth'] < alert_month].sort_values(by=['Ranking','CRT_INV_Mth'])
        return df_low_inventory

    # get lp inventory
    def _get_lp_inventory_quantity_list(self, month='newest') -> pd.DataFrame:
        lp_inventory_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_LP_CRT_INV.db'
        conn = sqlite3.connect(lp_inventory_db_fullname)
        c = conn.cursor()
        if month == 'newest':
            sql_cmd = 'SELECT name FROM Sqlite_master WHERE type=\'table\' ORDER by name DESC LIMIT 1'
            c.execute(sql_cmd)
            table_name = c.fetchall()[0][0]
        else:
            table_name = 'NED_INV_' + month
        sql_cmd = 'SELECT Material, Quantity as NED_INV FROM ' + table_name
        df_lp_inv = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        return df_lp_inv

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

    # data mapping with ned inventory for list of codes
    def inventory_mapping_with_ned_inv(self, code_list, table_name):
        jnj_inventory_database = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        # get jnj inventory
        conn = sqlite3.connect(jnj_inventory_database)
        sql_cmd = "SELECT Material, Description, Hierarchy_5, CSC, Available_Stock, " \
                  "Pending_Inventory_Bonded_Total_Qty as PD_BD_Qty, Pending_Inventory_NonB_Total_Qty as PD_NB_Qty, " \
                  "GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, Open_PO FROM " + table_name
        df_jnj_inventory = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # get ned inventory
        df_ned_inventory = self._get_lp_inventory_quantity_list(month='newest')
        # combine total inventory
        df_total_inventory = df_jnj_inventory.join(df_ned_inventory)
        # mapping with code list
        df_total_inventory = df_total_inventory.reindex(code_list)
        df_total_inventory.fillna(0, inplace=True)
        df_total_inventory.reset_index(inplace=True)
        # get output
        lst_columns = df_total_inventory.columns.values.tolist()
        lst_value = df_total_inventory.values.tolist()
        lst_value.insert(0, lst_columns)
        return lst_value

    # 数据同步
    def inv_data_sync(self, sync_days, lst_xcpt):
        lst_folder_temp = []
        import_success_count, import_fail_count = 0, 0
        # 读取oneclick目录下文件夹清单
        try:
            for file_name in os.listdir(self.oneclick_path):
                if os.path.isdir(self.oneclick_path + file_name):
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
                import_result = self.import_oneclick_inventory(item)
                if import_result == 1:
                    import_success_count += 1
                else:
                    import_fail_count += 1
        most_updated_table = self.get_tbl_list()[-1]
        return [import_success_count, import_fail_count, most_updated_table]

    # sync NED real time inventory
    def sync_ned_inventory(self):
        source_file_path = self.__class__.update_file_path + 'NED_INV/'
        # get file under that folder
        filename_list = []
        try:
            for file_name in os.listdir(source_file_path):
                filename_list.append(file_name)
        except FileNotFoundError:
            return 0
        # get date list in file
        ned_inv_file_list = [item[0:16] for item in filename_list]
        # get table list in database
        database_name = self.__class__.db_path + self.bu_name + '_LP_CRT_INV.db'
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        c.execute('SELECT name FROM sqlite_master WHERE TYPE=\'table\'')
        result = c.fetchall()
        ned_inv_db_list = [item[0] for item in result]
        # import data if file not in database
        for file_name in ned_inv_file_list:
            if file_name not in ned_inv_db_list:
                self.import_ned_current_inventory(file_name)
            else:
                pass
        return 1

    # import ned weekly update data
    def import_ned_current_inventory(self, file_name):
        source_file_path = self.__class__.update_file_path + 'NED_INV/'
        database_name = self.__class__.db_path + self.bu_name + '_LP_CRT_INV.db'
        master_data_table_name = self.bu_name + '_Master_Data'
        master_data_database_name = self.__class__.db_path + self.bu_name + '_Master_Data.db'
        data_filename = file_name + '.xlsx'
        df_lp_inv = pd.read_excel(source_file_path + data_filename, engine='openpyxl').rename(columns={'型号': 'Material', '数量': 'Quantity'})
        df_lp_inv.dropna(inplace=True)
        df_lp_inv.set_index('Material', inplace=True)
        # mapping with master data
        conn = sqlite3.connect(master_data_database_name)
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, Phoenix_Status, Standard_Cost, SAP_Price FROM ' + \
                  master_data_table_name
        df_master_data = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        df_lp_inv = df_lp_inv.join(df_master_data)
        df_lp_inv['Value_Standard_Cost'] = df_lp_inv['Quantity'] * df_lp_inv['Standard_Cost']
        df_lp_inv['Value_SAP_Price'] = df_lp_inv['Quantity'] * df_lp_inv['SAP_Price']
        df_lp_inv.reset_index(inplace=True)
        # reset column sequence
        cols_new = ['Material', 'Description', 'Hierarchy_5', 'Phoenix_Status', 'Standard_Cost', 'SAP_Price',
                    'Quantity', 'Value_Standard_Cost', 'Value_SAP_Price']
        df_lp_inv = df_lp_inv[cols_new]
        # write into database
        conn = sqlite3.connect(database_name)
        df_lp_inv.to_sql(con=conn, name=file_name, if_exists='replace', index=None)
        print(file_name, ' Imported')


# calculation module for Trauma
class TraumaCurrentInventoryCalculation(CurrentInventoryCalculation):

    def __init__(self):
        CurrentInventoryCalculation.__init__(self, 'TU')
        pass

    # get the backorder list of backorder information
    def get_current_bo(self, table_name) -> list:
        lst_title = ['Material', 'Description', 'Hierarchy_5', 'CSC', 'Qty', 'Value', 'GIT_1', 'GIT_2',
                     'GIT_3', 'GIT_4', 'Open_PO', 'NED_INV']
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty as Qty, ' \
                  'GIT_1_Week as GIT_1, GIT_2_Week as GIT_2, ' \
                  'GIT_3_Week as GIT_3, GIT_4_Week as GIT_4, Open_PO from %s WHERE Qty > 0 ' \
                  'ORDER by CSC DESC' % table_name
        df_backorder = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # get sap price
        master_data_db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        master_data_table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(master_data_db_name)
        sql_cmd = 'SELECT Material, Price FROM %s' % master_data_table_name
        df_sap_price = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # combine and calculate the price
        df_backorder = df_backorder.join(df_sap_price)
        df_backorder.fillna(0, inplace=True)
        df_backorder['Value'] = df_backorder['Qty'] * df_backorder['Price']
        # combine with NED inventory
        df_lp_inv_quantity = self._get_lp_inventory_quantity_list()
        df_lp_inv_quantity.rename(columns={'Quantity': 'NED_INV'}, inplace=True)
        df_backorder = df_backorder.join(df_lp_inv_quantity)
        df_backorder.fillna(0, inplace=True)
        # calculate the GIT value
        # get fulfill Qty
        df_backorder['GIT1_Fill'] = df_backorder[['GIT_1', 'Qty']].min(axis=1)
        df_backorder['Qty_Remain'] = df_backorder['Qty'] - df_backorder['GIT1_Fill']
        df_backorder['GIT2_Fill'] = df_backorder[['GIT_2', 'Qty_Remain']].min(axis=1)
        df_backorder['Qty_Remain'] = df_backorder['Qty_Remain'] - df_backorder['GIT2_Fill']
        df_backorder['GIT3_Fill'] = df_backorder[['GIT_3', 'Qty_Remain']].min(axis=1)
        df_backorder['Qty_Remain'] = df_backorder['Qty_Remain'] - df_backorder['GIT3_Fill']
        df_backorder['GIT4_Fill'] = df_backorder[['GIT_4', 'Qty_Remain']].min(axis=1)
        df_backorder['Qty_Remain'] = df_backorder['Qty_Remain'] - df_backorder['GIT4_Fill']
        df_backorder['Open_PO_Fill'] = df_backorder[['Open_PO', 'Qty_Remain']].min(axis=1)
        # generate summary line
        lst_summary = ["-", "-", "-", "Total", df_backorder['Qty'].sum(), df_backorder['Value'].sum()]
        lst_git_title = ['GIT1_Fill', 'GIT2_Fill', 'GIT3_Fill', 'GIT4_Fill', 'Open_PO_Fill']
        for git_item in lst_git_title:
            lst_summary.append((df_backorder['Price'] * df_backorder[git_item]).sum())
        # choose the output with selected columns
        df_backorder.reset_index(inplace=True)
        df_backorder.sort_values(by=['CSC', 'Value'], ascending=False, inplace=True)
        df_backorder_output = df_backorder[lst_title]
        return [lst_title, ] + df_backorder_output.values.tolist() + [lst_summary, ]

    def generate_backorder_trend(self):
        # get the material price list
        db_name = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_table_name = self.__class__.bu_name + "_SAP_Price"
        conn = sqlite3.connect(db_name)
        sql_cmd = 'SELECT Material, Price FROM %s' % data_table_name
        df_sap_price = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # get current inventory backorder list
        # get table list
        db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name")
        table_list = [item[0] for item in c.fetchall()]
        date_list = [item[-6:] for item in table_list]
        # generate blank dataframe
        df_bo_value_summary = pd.DataFrame(index=['IND', 'ROP', 'None'])
        # get backorder data
        for table_item in table_list:
            sql_cmd = "SELECT Material, CSC, Current_Backorder_Qty FROM %s WHERE Current_Backorder_Qty > 0" % table_item
            df_bo_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
            df_bo_list = df_bo_list.join(df_sap_price)
            df_bo_list['Backorder_Value'] = df_bo_list['Current_Backorder_Qty'] * df_bo_list['Price']
            df_bo_value = pd.pivot_table(df_bo_list, values='Backorder_Value', index='CSC', aggfunc=np.sum)
            df_bo_value.rename(columns={'Backorder_Value': table_item[-4:]}, inplace=True)
            df_bo_value_summary = df_bo_value_summary.join(df_bo_value)
        df_bo_value_summary.fillna(0, inplace=True)
        df_bo_value_summary = df_bo_value_summary.astype('int32', copy=True)
        return [date_list, df_bo_value_summary.values.tolist()]


if __name__ == "__main__":
    test = CurrentInventoryCalculation('TU')
    lst_date = ['20210104', '20210105', '20210106', '20210107', '20210108', '20210112', '20210113', '20210114', '20210115', '20210118']
    for item_date in lst_date:
        print(test.import_all_dps_oneclick_inventory(item_date))
        print('%s done' % item_date)
    # test.inv_data_sync(50)
