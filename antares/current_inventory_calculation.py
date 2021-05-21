import sqlite3
import numpy as np
import draw_chart as chart
import os
import pandas as pd


class CurrentInventoryCalculation:
    oneclick_path = '//jnjcnckapdfs11.ap.jnj.com/jnjcnmpdfsroot/COMPASS/Oneclick Inventory Report/Output/'
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    update_file_path = "../data/_Update/"
    oneclick_database = db_path + 'dps_oneclick_inventory.db'
    currency_rate = 6.9233
    _sync_days = 0
    _exception_list = []

    def __int__(self):
        pass

    @property
    def bu_name(self):
        return self._bu_name

    @bu_name.setter
    def bu_name(self, bu_name_input):
        self._bu_name = bu_name_input

    @property
    def sync_days(self):
        return self._sync_days

    @sync_days.setter
    def sync_days(self, sync_days_input):
        self._sync_days = sync_days_input

    @property
    def exception_list(self):
        return self._exception_list

    @exception_list.setter
    def exception_list(self, exception_list_input):
        self._exception_list = exception_list_input

    # import all dps inventory data to database
    def import_dps_oneclick_inventory(self, str_date):
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
        sql_cmd = 'SELECT Material, Local_Hierarchy FROM JT_Local_Hierarchy'
        _conn = sqlite3.connect(self.db_path + 'JT_Master_Data.db')
        df_local_hierarchy = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Material')
        df_dps = df_dps.join(df_local_hierarchy)
        df_dps.loc[df_dps['Local_Hierarchy'].notnull(), 'Hierarchy_5'] = df_dps['Local_Hierarchy']
        df_dps.drop(columns=['Local_Hierarchy'], inplace=True)
        df_dps.reset_index(inplace=True)
        # add date to first column
        df_dps.insert(0, 'Date', str_date)
        # export to database
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        df_dps.to_sql('oneclick_inventory', con=_conn, if_exists="append", index=False)
        print('%s was imported.' % str_date)
        return 1

    # synchronize inventory data with oneclick
    def start_synchronize(self) -> list:
        lst_folder_temp = []
        import_success_count, import_fail_count = 0, 0
        # read folder list in share folder
        try:
            for file_name in os.listdir(self.oneclick_path):
                if os.path.isdir(self.oneclick_path + file_name):
                    lst_folder_temp.append(file_name)
        except FileNotFoundError:
            return 0
        lst_folder_temp.sort()
        lst_folder_sharepoint = lst_folder_temp[0 - self._sync_days:]
        # get local data
        lst_current_database = self.get_local_inventory_date_list()
        # start to sync
        # delete outdated data
        for item in lst_current_database:
            if item not in lst_folder_sharepoint:
                self.delete_local_inventory_item(item)
                lst_current_database.remove(item)
        # import new data
        for item in lst_folder_sharepoint:
            if (item not in lst_current_database) and (item not in self._exception_list):
                import_result = self.import_dps_oneclick_inventory(item)
                if import_result == 1:
                    import_success_count += 1
                else:
                    import_fail_count += 1
        most_updated_table = self.get_local_inventory_date_list()[-1][0]
        return [import_success_count, import_fail_count, most_updated_table]

    def get_local_inventory_date_list(self) -> list:
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        c = _conn.cursor()
        c.execute('SELECT DISTINCT(Date) FROM oneclick_inventory ORDER BY Date')
        result = c.fetchall()
        date_list = [item[0] for item in result]
        return date_list

    # inventory_data: YYYYMMDD
    def delete_local_inventory_item(self, inventory_date):
        _conn = sqlite3.connect(self.db_path + 'oneclick_dps_inventory.db')
        c = _conn.cursor()
        sql_cmd = 'DELETE FROM oneclick_inventory WHERE Date = \"%s\"' % inventory_date
        c.execute(sql_cmd)
        _conn.commit()
        _conn.close()
        print('Inventory of %s has been deleted.' % inventory_date)

    # check if this date exist (date format YYYYMMDD)
    def check_date_availability(self, str_date_input):
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        c.execute('SELECT count(Material) FROM oneclick_inventory WHERE Date = \"%s\"' % str_date_input)
        result = c.fetchone()[0]
        return True if result else False

    # get inventory summary for single day
    def get_current_inventory(self, str_date_input) -> list:
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return []
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = 'SELECT Hierarchy_5, sum(Available_Stock * Standard_Cost) AS Available_Stock, ' \
                  'sum((GIT_1_Week + GIT_2_Week + GIT_3_Week + GIT_4_Week) * Standard_Cost) AS GIT_Inventory, ' \
                  'sum(Open_PO * Standard_Cost) As Open_PO_Value, ' \
                  'sum(Pending_Inventory_Bonded_Total_Qty * Standard_Cost) AS Bonding_Pending, ' \
                  'sum(Pending_Inventory_NonB_Total_Qty * Standard_Cost) AS Non_bonded_Pending FROM oneclick_inventory ' \
                  'WHERE Business_Unit =\"%s\" AND Date = \"%s\" GROUP BY Hierarchy_5 ' \
                  'ORDER BY Available_Stock DESC' % (self._bu_name, str_date_input)
        df_current_inventory = pd.read_sql(sql=sql_cmd, con=_conn)
        total_available_stock_value = df_current_inventory['Available_Stock'].sum()
        total_useful_stock_value = total_available_stock_value + df_current_inventory['GIT_Inventory'].sum() + df_current_inventory['Bonding_Pending'].sum()
        total_stock_value = total_useful_stock_value = df_current_inventory['Non_bonded_Pending'].sum() + df_current_inventory['Open_PO_Value'].sum()
        lst_result = [df_current_inventory.columns.tolist()] + df_current_inventory.values.tolist()
        return [lst_result, [total_available_stock_value, total_useful_stock_value, total_stock_value]]

    # get backorder summary for single day
    def get_current_bo(self, str_date_input) -> list:
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return []
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, CSC, Current_Backorder_Qty, Average_Selling_Price, ' \
                  '(Current_Backorder_Qty * Average_Selling_Price) as Backorder_Value, GIT_1_Week, GIT_2_Week, ' \
                  'GIT_3_Week, GIT_4_Week, Open_PO FROM oneclick_inventory WHERE Business_Unit=\"%s\" AND ' \
                  'Current_Backorder_Qty > 0 AND Date = \"%s\" ORDER by CSC DESC, Backorder_Value DESC' \
                  % (self._bu_name, str_date_input)
        df_backorder = pd.read_sql(sql=sql_cmd, con=_conn)
        # calculate GIT fulfillment
        df_backorder['GIT_1_Fulfill'] = df_backorder[['Current_Backorder_Qty', 'GIT_1_Week']].min(axis=1)
        df_backorder['GIT_1_Fulfill_Value'] = df_backorder['GIT_1_Fulfill'] * df_backorder['Average_Selling_Price']
        df_backorder['GIT_1_Remain'] = df_backorder['Current_Backorder_Qty'] - df_backorder['GIT_1_Fulfill']
        df_backorder['GIT_2_Fulfill'] = df_backorder[['GIT_1_Remain', 'GIT_2_Week']].min(axis=1)
        df_backorder['GIT_2_Fulfill_Value'] = df_backorder['GIT_2_Fulfill'] * df_backorder['Average_Selling_Price']
        df_backorder['GIT_2_Remain'] = df_backorder['GIT_1_Remain'] - df_backorder['GIT_2_Fulfill']
        df_backorder['GIT_3_Fulfill'] = df_backorder[['GIT_2_Remain', 'GIT_3_Week']].min(axis=1)
        df_backorder['GIT_3_Fulfill_Value'] = df_backorder['GIT_3_Fulfill'] * df_backorder['Average_Selling_Price']
        df_backorder['GIT_3_Remain'] = df_backorder['GIT_2_Remain'] - df_backorder['GIT_3_Fulfill']
        df_backorder['GIT_4_Fulfill'] = df_backorder[['GIT_3_Remain', 'GIT_4_Week']].min(axis=1)
        df_backorder['GIT_4_Fulfill_Value'] = df_backorder['GIT_4_Fulfill'] * df_backorder['Average_Selling_Price']
        df_backorder['GIT_4_Remain'] = df_backorder['GIT_3_Remain'] - df_backorder['GIT_4_Fulfill']
        df_backorder['Open_PO_Fulfill'] = df_backorder[['GIT_4_Remain', 'Open_PO']].min(axis=1)
        df_backorder['Open_PO_Fulfill_Value'] = df_backorder['Open_PO_Fulfill'] * df_backorder['Average_Selling_Price']
        lst_summary = ["-", "-", "-", "Total", df_backorder['Current_Backorder_Qty'].sum(),
                       df_backorder['Backorder_Value'].sum(), df_backorder['GIT_1_Fulfill_Value'].sum(),
                       df_backorder['GIT_2_Fulfill_Value'].sum(), df_backorder['GIT_3_Fulfill_Value'].sum(),
                       df_backorder['GIT_4_Fulfill_Value'].sum(), df_backorder['Open_PO_Fulfill_Value'].sum()]
        # remove additional column
        lst_title = ['Material', 'Description', 'Hierarchy_5', 'CSC', 'Current_Backorder_Qty', 'Backorder_Value',
                     'GIT_1_Week', 'GIT_2_Week', 'GIT_3_Week', 'GIT_4_Week', 'Open_PO']
        df_backorder_final = df_backorder[lst_title]
        final_output_list = df_backorder_final.values.tolist()
        final_output_list.insert(0, lst_title)
        final_output_list.append(lst_summary)
        return final_output_list

    # export backorder list
    def export_backorder_data(self, str_date_input) -> pd.DataFrame:
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = 'SELECT Material, Description, Hierarchy_5, Current_Backorder_Qty, ' \
                  '(Current_Backorder_Qty * Average_Selling_Price) AS bo_value, GIT_1_Week, GIT_2_Week, GIT_3_Week, ' \
                  'GIT_4_Week, Open_PO FROM oneclick_inventory WHERE Business_Unit=\"%s\" AND ' \
                  'Current_Backorder_Qty > 0 ORDER by bo_value DESC' % self._bu_name
        df_backorder = pd.read_sql(sql=sql_cmd, con=_conn)
        df_backorder.drop(columns=['bo_value'], inplace=True)
        if self._bu_name == 'TU':
            df_backorder.rename(columns={"Material": "代码", "Description": "英文描述", "Hierarchy_5": "产品分类",
                                         "Current_Backorder_Qty": "缺货数量", "GIT_1_Week": "2周左右",
                                         "GIT_2_Week": "3-4周", "GIT_3_Week": "4-6周", "GIT_4_Week": "6-8周",
                                         "Open_PO": "已下订单"},
                                inplace=True)
        return df_backorder

    # export inventory list to customer
    def export_inventory_data(self, str_date_input) ->pd.DataFrame:
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        _conn = sqlite3.connect(self.oneclick_database)
        if self._bu_name == 'TU':
            sql_cmd = 'SELECT Material, Description, Available_Stock FROM oneclick_inventory ' \
                      'WHERE Available_Stock !=0 AND Business_Unit = \"%s\" AND Date=\"%s\"' % (self._bu_name, str_date_input)
        else:
            sql_cmd = 'SELECT Material, Description, CSC, Available_Stock, Pending_Inventory_Bonded_Total_Qty, ' \
                      'GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, Open_PO FROM oneclick_inventory WHERE ' \
                      'Business_Unit = \"%s\" AND Date=\"%s\"' % (self._bu_name, str_date_input)
        df_inventory = pd.read_sql(sql=sql_cmd, con=_conn)
        if self._bu_name == "TU":
            df_inventory.rename(columns={"Material": "代码", "Description": "英文描述",
                                         "Available_Stock": "可用数量"}, inplace=True)
        return df_inventory

    # display backorder value trend by day
    def generate_backorder_trend(self) -> list:
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = 'SELECT Date, CSC, sum(Current_Backorder_Qty * Average_Selling_Price) as Backorder_Value ' \
                  'FROM oneclick_inventory WHERE Business_Unit=\"%s\" GROUP BY Date, CSC ORDER by Date' % self._bu_name
        df_backorder_detail = pd.read_sql(sql=sql_cmd, con=_conn)
        df_backorder_detail.fillna('ND', inplace=True)
        df_backorder_detail = df_backorder_detail.astype({'Backorder_Value': 'int32'})
        df_backorder_summary = pd.pivot_table(df_backorder_detail, values='Backorder_Value', index='CSC',
                                              columns='Date').reindex(['IND', 'ROP', 'ND'])
        return [df_backorder_summary.columns.tolist(), df_backorder_summary.values.tolist()]

    # generate aging backorder list by pandas
    # return the list of information by row including title and the length of data
    def generate_aging_backorder_list(self, exception_list=[]) -> list:

        pass

    # Daily pending inventory trend display
    def generate_pending_trend(self, data_type="value"):
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = 'SELECT Date, sum(Pending_Inventory_Bonded_Total_Qty) as Pending_BD_Qty, ' \
                  'sum(Pending_Inventory_NonB_Total_Qty) as Pending_NB_Qty, ' \
                  'sum((Standard_Cost * Pending_Inventory_Bonded_Total_Qty)) As Pending_BD_Value, ' \
                  'sum((Standard_Cost * Pending_Inventory_NonB_Total_Qty)) As Pending_NB_Value FROM oneclick_inventory ' \
                  'WHERE Business_Unit=\"%s\" GROUP by Date ORDER by Date' % self._bu_name
        df_pending_detail = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Date').astype('int32')
        date_list = df_pending_detail.index.tolist()
        if data_type == "value":
            lst_pending_value = [df_pending_detail['Pending_BD_Value'].tolist(),
                                 df_pending_detail['Pending_NB_Value'].tolist()]
            chart_title = "Pending Inventory Trend of " + self._bu_name + " (Value in RMB)"
        else:
            lst_pending_value = [df_pending_detail['Pending_BD_Qty'].tolist(),
                                 df_pending_detail['Pending_NB_Qty'].tolist()]
            chart_title = "Pending Inventory Trend of " + self._bu_name + " (by Quantity)"
        chart.pending_inventory_trend_chart(date_list, lst_pending_value, chart_title)
        pass

    # check inventory of single code, str_date_input = YYYYMMDD
    def get_code_inv(self, code_name, str_date_input):
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        sql_cmd = "SELECT Material, Description, Hierarchy_5, Available_Stock, Pending_Inventory_Bonded_Total_Qty, " \
                  "Pending_Inventory_NonB_Total_Qty, CSC, GIT_1_Week, GIT_2_Week, GIT_3_Week, GIT_4_Week, Open_PO, " \
                  "Standard_Cost FROM oneclick_inventory WHERE Material = \"%s\" AND Date=\"%s\"" % (code_name, str_date_input)
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

    # check inventory quantity trend for single code
    def generate_code_inv_trend(self, code_name):
        _conn = sqlite3.connect(self.oneclick_database)
        # get to date list
        sql_cmd = 'SELECT DISTINCT(Date) FROM oneclick_inventory'
        c = _conn.cursor()
        c.execute(sql_cmd)
        result = c.fetchall()
        date_list = [item[0] for item in result]
        df_inventory = pd.DataFrame(index=date_list)
        # get inventory data
        sql_cmd = 'SELECT Date, Available_Stock FROM oneclick_inventory WHERE Material=\"%s\"' % code_name
        df_code_result = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Date').astype('int32')
        df_inventory = df_inventory.join(df_code_result)
        df_inventory.fillna(0, inplace=True)
        chart_title = 'Inventory Trend of %s' % code_name
        chart.line_chart(code_name, date_list, df_inventory.values.tolist(), "Date", "INV Qty", chart_title)
        pass

    # display inventory trend by hierarchy_5
    def generate_h5_inventory_trend(self, h5_input):
        _conn = sqlite3.connect(self.oneclick_database)
        # get to date list
        sql_cmd = 'SELECT DISTINCT(Date) FROM oneclick_inventory'
        c = _conn.cursor()
        c.execute(sql_cmd)
        result = c.fetchall()
        date_list = [item[0] for item in result]
        df_inventory = pd.DataFrame(index=date_list)
        # get inventory data
        if h5_input.upper() == 'ALL':
            sql_cmd = 'SELECT Date, sum(Available_Stock* Standard_Cost) as Stock_Value FROM oneclick_inventory ' \
                      'WHERE Business_Unit = \"%s\" GROUP BY Business_Unit, Date ORDER BY Date' % self._bu_name
        else:
            sql_cmd = 'SELECT Date, sum(Available_Stock* Standard_Cost) as Stock_Value FROM oneclick_inventory ' \
                        'WHERE Hierarchy_5 = \"%s\" GROUP BY Date, Hierarchy_5 ORDER BY Date' % h5_input
        df_h5_result = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Date').astype('int32')
        df_inventory = df_inventory.join(df_h5_result)
        df_inventory.fillna(0, inplace=True)
        chart_title = 'Inventory Trend of %s' % h5_input
        chart.line_chart(h5_input, date_list, df_inventory.values.tolist(), "Date", "Value", chart_title)

    # display inventory of h5 of both qty and value
    def generate_h5_inventory_trend_two_dimension(self, h5_input):
        _conn = sqlite3.connect(self.oneclick_database)
        # get to date list
        sql_cmd = 'SELECT DISTINCT(Date) FROM oneclick_inventory'
        c = _conn.cursor()
        c.execute(sql_cmd)
        result = c.fetchall()
        date_list = [item[0] for item in result]
        df_inventory = pd.DataFrame(index=date_list)
        # get inventory data
        if h5_input.upper() == 'ALL':
            sql_cmd = 'SELECT Date, sum(Available_Stock) as Stock_Qty, sum(Available_Stock* Standard_Cost) ' \
                      'as Stock_Value FROM oneclick_inventory WHERE Business_Unit = \"%s\" ' \
                      'GROUP BY Business_Unit, Date ORDER BY Date' % self._bu_name
        else:
            sql_cmd = 'SELECT Date, sum(Available_Stock) as Stock_Qty, sum(Available_Stock* Standard_Cost) ' \
                      'as Stock_Value FROM oneclick_inventory WHERE Hierarchy_5 = \"%s\" ' \
                      'GROUP BY Date, Hierarchy_5 ORDER BY Date' % h5_input
        df_h5_result = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Date').astype('int32')
        df_inventory = df_inventory.join(df_h5_result)
        df_inventory.fillna(0, inplace=True)
        chart_title = 'Inventory Trend of %s (Two Dimension)' % h5_input
        chart.double_line_chart(h5_input, date_list, df_inventory['Stock_Qty'].values.tolist(),
                                df_inventory['Stock_Value'].values.tolist(), 'Date', 'Qty', 'Value', chart_title)
        pass

    # show inventory detail of one hierarchy_5
    def get_h5_inv_detail(self, h5_input, str_date_input):
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        # generate title
        table_title = [("Material", "Description", "CSC", "Available Stock", "Onhand_INV_Value", "Bonded Pending",
                        "GIT_1_Week", "GIT_2_Week", "GIT_3_Week", "GIT_4_Week", "Open_PO"), ]
        # Connect to database
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        sql_cmd = "SELECT Material, Description, CSC, Available_Stock, (Standard_Cost * Inventory_OnHand) as " \
                  "Onhand_INV_Value, Pending_Inventory_Bonded_Total_Qty, GIT_1_Week, GIT_2_Week, GIT_3_Week, " \
                  "GIT_4_Week, Open_PO FROM oneclick_inventory WHERE Hierarchy_5 = \"%s\" COLLATE NOCASE " \
                  "AND Date = \"%s\" ORDER by Material" % (h5_input.upper(), str_date_input)
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

    # data mapping for a list of codes
    def inventory_mapping(self, code_list, str_date_input) -> list:
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        df_inventory = pd.DataFrame(index=code_list)
        # get inventory list
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = "SELECT Material, Description, Hierarchy_5, CSC, Available_Stock, " \
                  "Pending_Inventory_Bonded_Total_Qty, Pending_Inventory_NonB_Total_Qty, GIT_1_Week, GIT_2_Week, " \
                  "GIT_3_Week, GIT_4_Week, Open_PO FROM oneclick_inventory WHERE Date = \"%s\"" % str_date_input
        df_inventory_detail = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Material')
        df_inventory = df_inventory.join(df_inventory_detail)
        df_inventory.fillna(0, inplace=True)
        df_inventory.reset_index(inplace=True)
        df_inventory.rename(columns={'index': 'Material'}, inplace=True)
        lst_inventory_result = df_inventory.values.tolist()
        lst_inventory_result.insert(0, df_inventory.columns.tolist())
        return lst_inventory_result

    # data mapping with ned inventory for list of codes
    def inventory_mapping_with_ned_inv(self, code_list, str_date_input):
        str_date_input = self.get_newest_date() if str_date_input == 'newest' else str_date_input
        # judge if this code exist
        if not self.check_date_availability(str_date_input):
            return 0
        df_inventory = pd.DataFrame(index=code_list)
        # get inventory list
        _conn = sqlite3.connect(self.oneclick_database)
        sql_cmd = "SELECT Material, Description, Hierarchy_5, CSC, Available_Stock, " \
                  "Pending_Inventory_Bonded_Total_Qty, Pending_Inventory_NonB_Total_Qty, GIT_1_Week, GIT_2_Week, " \
                  "GIT_3_Week, GIT_4_Week, Open_PO FROM oneclick_inventory WHERE Date = \"%s\"" % str_date_input
        df_inventory_detail = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Material')
        df_inventory = df_inventory.join(df_inventory_detail)
        # get ned inventory
        df_ned_inventory = self._get_lp_inventory_quantity_list(month='newest')
        # combine total inventory
        df_total_inventory = df_inventory.join(df_ned_inventory)
        # get output
        lst_columns = df_total_inventory.columns.values.tolist()
        lst_value = df_total_inventory.values.tolist()
        lst_value.insert(0, lst_columns)
        return lst_value

    # get lp inventory
    def _get_lp_inventory_quantity_list(self, month='newest') -> pd.DataFrame:
        lp_inventory_db_fullname = self.__class__.db_path + self._bu_name + '_LP_CRT_INV.db'
        _conn = sqlite3.connect(lp_inventory_db_fullname)
        str_date = self.get_newest_date() if month == 'newest' else month
        sql_cmd = 'SELECT Material, Quantity as NED_INV FROM ned_current_inventory WHERE Date=\"%s\"' % str_date
        df_lp_inv = pd.read_sql(sql=sql_cmd, con=_conn, index_col='Material')
        return df_lp_inv

    def get_newest_date(self) -> str:
        _conn = sqlite3.connect(self.oneclick_database)
        c = _conn.cursor()
        c.execute('SELECT Date FROM oneclick_inventory ORDER BY Date DESC LIMIT 1')
        str_newest_date = c.fetchone()[0]
        return str_newest_date

    # check code availability
    def check_code(self, material_code) -> bool:
        conn = sqlite3.connect(self.__class__.db_path + "Master_Data.db")
        c = conn.cursor()
        sql_cmd = 'SELECT count(Material) FROM MATERIAL_MASTER WHERE Business_Unit=\"%s\" ' \
                  'AND Material = \"%s\"' % (self.__class__.bu_name, material_code)
        c.execute(sql_cmd)
        result = c.fetchall()[0]
        trigger = False if result == 0 else True
        return trigger


# calculation module for Trauma
class TraumaCurrentInventoryCalculation(CurrentInventoryCalculation):

    def __init__(self):
        self._bu_name = 'TU'
        super.__init__()
        pass

    # sync NED real time inventory
    def sync_ned_inventory(self) -> bool:
        source_file_path = self.__class__.update_file_path + 'NED_INV/'
        # get file under that folder
        filename_list = []
        try:
            for file_name in os.listdir(source_file_path):
                filename_list.append(file_name)
        except FileNotFoundError:
            return False
        # get date list in file
        ned_inv_file_list = [item[8:16] for item in filename_list]
        # get table list in database
        database_name = self.__class__.db_path + self.bu_name + '_LP_CRT_INV.db'
        conn = sqlite3.connect(database_name)
        c = conn.cursor()
        try:
            c.execute('SELECT DISTINCT(Date) FROM ned_current_inventory')
            result = c.fetchall()
            ned_inv_db_list = [item[0] for item in result]
        except sqlite3.OperationalError:
            ned_inv_db_list = []
        # import data if file not in database
        for inventory_date in ned_inv_file_list:
            if inventory_date not in ned_inv_db_list:
                self.import_ned_current_inventory(inventory_date)
            else:
                pass
        return True

    # import ned weekly update data
    def import_ned_current_inventory(self, inventory_date):
        source_file_path = self.__class__.update_file_path + 'NED_INV/'
        database_name = self.__class__.db_path + self.bu_name + '_LP_CRT_INV.db'
        master_data_table_name = self.bu_name + '_Master_Data'
        master_data_database_name = self.__class__.db_path + self.bu_name + '_Master_Data.db'
        data_filename = 'NED_INV_%s.xlsx' % inventory_date
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
        df_lp_inv.insert(0, 'Date', inventory_date)
        # write into database
        conn = sqlite3.connect(database_name)
        df_lp_inv.to_sql(con=conn, name='ned_current_inventory', if_exists='append', index=None)
        print('NED Inventory of %s Imported' % inventory_date)


if __name__ == "__main__":
    sync_test = TraumaCurrentInventoryCalculation()
    # sync_test.bu_name = 'TU'
    sync_test.sync_days = 90
    sync_test.exception_list = []
    print(sync_test.check_code('440.834'))
    pass
