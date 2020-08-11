# Use dict to get general information on code level

import sqlite3
import pandas as pd
import calculation as cclt
import numpy as np
import time


def generate_str_month_list(month_list):
    str_month_list = ''
    for month_item in month_list:
        str_month_list += '\"' + month_item + '\",'
    str_month_list = str_month_list.rstrip(',')
    return str_month_list
    pass


class SNOPCodeExport:

    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"
    file_path = "../data/_Source_Data/"
    file_fullname = ""

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # Get active code list
    def get_active_codes(self):
        file_name = self.__class__.bu_name + "_Active_Codes"
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
        print("Start get the active code list")
        df = pd.read_excel(file_fullname, dtype=object)
        # 读取所有元素
        data = df.values
        code_list = []
        for item in data:
            code_list.append(item[0])
        # 测试阶段返回N个数字
        return code_list

    def get_all_master_data(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        # datasheet_name = self.__class__.bu_name + '_Master_Data_Demo'
        datasheet_name = self.__class__.bu_name + '_Master_Data'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = "SELECT Material, Description, Chinese_Description, Hierarchy_4, Hierarchy_5, PM, Sales_Status, " \
                  "Purchase_Status, Standard_Cost, SAP_Price, Ranking, MRP_Type, Reorder_Point, Phoenix_Status, " \
                  "Phoenix_Target_SKU, Phoenix_Discontinuation_Date, Phoenix_Obsolescence_Date, GTIN FROM " + datasheet_name
        df = pd.read_sql(sql=sql_cmd, con=conn)
        # code_list = df['Material'].values.tolist()
        return df

    # generate str_month_list for sql cmd with month list for calculation

    # Return all the sales data
    def get_code_sales_list(self, sales_type, month_list):
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item + '\",'
        str_month_list = str_month_list.rstrip(',')
        file_name = self.__class__.bu_name + "_" + sales_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        sql_cmd = "SELECT Material, Month, Quantity, Value_Standard_Cost, Value_SAP_Price from " + file_name + \
                  " WHERE Month IN (" + str_month_list + ") GROUP by Material, Month Order by Month"
        df = pd.read_sql(sql=sql_cmd, con=conn)
        conn.commit()
        conn.close()
        return df

    # Return all the Inventory Data
    def get_code_inventory_list(self, inv_type, month_list):
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item + '\",'
        str_month_list = str_month_list.rstrip(',')
        file_name = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        if inv_type == "JNJ_INV":
            sql_cmd = "SELECT Material, Month, sum(Available_Stock) as Quantity, " \
                      "sum(Value_Standard_Cost) as Value_Standard_Cost, sum(Value_SAP_Price) as Value_SAP_Price FROM " \
                      + file_name + " WHERE Month IN (" + str_month_list + ") GROUP BY Material, Month ORDER BY Month"
        else:
            sql_cmd = "SELECT Material, Month, sum(Quantity) as Quantity, " \
                      "sum(Value_Standard_Cost) as Value_Standard_Cost, sum(Value_SAP_Price) as Value_SAP_Price from " \
                      + file_name + " WHERE Month IN (" + str_month_list + ") GROUP BY Material, Month ORDER BY Month"
        df = pd.read_sql(sql=sql_cmd, con=conn)
        conn.commit()
        conn.close()
        return df

    # Return Forecast
    def get_forecast_list(self, month_list, forecast_type):
        str_month_list = generate_str_month_list(month_list)
        database_name = self.__class__.db_path + self.__class__.bu_name + '_' + forecast_type + '_Forecast.db'
        conn = sqlite3.connect(database_name)
        # get the newest version of statistical forecast
        c = conn.cursor()
        c.execute('SELECT name FROM sqlite_master WHERE type = "table" ORDER by name')
        table_name = c.fetchall()[-1][0]
        sql_cmd = 'SELECT Material, Month, Quantity, Value_SAP_Price FROM ' + table_name + ' WHERE Month IN (' \
                  + str_month_list + ') ORDER by Month'
        df = pd.read_sql(sql=sql_cmd, con=conn)
        conn.commit()
        conn.close()
        return df

    # Return recent ESO result of 2 cycle.
    def get_code_eso_list(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_ESO.db'
        datasheet_name = self.__class__.bu_name + '_ESO'
        # get recent 2 cycle.
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 2'
        c = conn.cursor()
        c.execute(sql_cmd)
        month_list = c.fetchall()
        str_month_list = ''
        for month_item in month_list:
            str_month_list += '\"' + month_item[0] + '\",'
        str_month_list = str_month_list.rstrip(',')
        # get ESO result of most recent 2 cycles.
        sql_cmd = 'SELECT * FROM ' + datasheet_name + ' WHERE Month IN (' + str_month_list + ")"
        df_eso = pd.read_sql(sql=sql_cmd, con=conn)
        df_eso_result = pd.pivot_table(df_eso, index='Material',
                                       values=['Excess_Quantity', 'Slow_Moving_Quantity', 'Obsolete_Quantity',
                                               'Total_ESO_Quantity', 'NPI_Reverse_Value', 'Total_ESO_Value'],
                                       columns="Month", fill_value=0)
        return df_eso_result

    def generate_code_onesheet(self):
        # Get Month list
        time_start = time.time()
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -24)
        # initiate column name list
        # Get active code list
        df_material_master = self.get_all_master_data()
        lst_column_name = list(df_material_master)
        list_material_master = df_material_master.values.tolist()
        active_code_list = df_material_master['Material'].values.tolist()
        print("Data Length:", len(active_code_list))
        # Get eso_result
        df_eso_result = self.get_code_eso_list()
        lst_column_name += [item[0] + "_" + item[1] for item in list(df_eso_result)]
        # Generate sales type list
        sales_type = ["GTS", "LPSales", "IMS"]
        lst_sales_df = []
        for sales_type_item in sales_type:
            df = self.get_code_sales_list(sales_type_item, month_list)
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            # print(len(list(pivot_result)))
            # print(sales_type_item, " is ready!")
            lst_column_name += [sales_type_item + "_" + item[0] + "_" + item[1] for item in list(pivot_result)]
            lst_sales_df.append(pivot_result)
        # Generate inventory type list
        inventory_type = ["JNJ_INV", "LP_INV"]
        lst_inv_df = []
        for inv_type_item in inventory_type:
            df = self.get_code_inventory_list(inv_type_item, month_list)
            # Generate pivot_table
            pivot_result = pd.pivot_table(df, index="Material",
                                          values=["Quantity", "Value_Standard_Cost", "Value_SAP_Price"],
                                          columns="Month", fill_value=0)
            # print(inv_type_item, " is ready!")
            lst_column_name += [inv_type_item + "_" + item[0] + "_" + item[1] for item in list(pivot_result)]
            lst_inv_df.append(pivot_result)
        # Generate forecast pivot list
        forecast_type = ['Statistical', 'Final']
        forecast_month_list = info_check.get_time_list(current_month, 24)
        lst_forecast_df = []
        for forecast_type_item in forecast_type:
            df = self.get_forecast_list(forecast_month_list, forecast_type_item)
            # Generate pivot_table
            pivot_result = pd.pivot_table(df, index='Material', values=['Quantity', 'Value_SAP_Price'],
                                          columns='Month', fill_value=0)
            # print(forecast_type_item, " Forecast is ready!")
            lst_column_name += [forecast_type_item + "_Forecast_" + item[0] + "_" + item[1] for item in list(pivot_result)]
            lst_forecast_df.append(pivot_result)
        # Get sales result of single code
        snop_result = []
        # start count
        print('Start to generate code list')
        counter, num = 0, 5
        list_show = list(range(int(len(list_material_master) / 20), len(list_material_master) + 1,
                               int(len(list_material_master) / 20)))
        # start mapping
        for code_item in list_material_master:
            # initiate blank list
            code_name = code_item[0]
            # load master data
            code_output = code_item
            # load eso
            try:
                code_eso_result = df_eso_result.loc[code_name]
            except KeyError:
                code_output.extend([x * 0 for x in range(0, len(df_eso_result.columns))])
            else:
                code_output.extend(code_eso_result.values.tolist())
            # Load sales data
            for sales_item_df in lst_sales_df:
                try:
                    code_result = sales_item_df.loc[code_name]
                except KeyError:
                    code_output.extend([x * 0 for x in range(0, len(sales_item_df.columns))])
                else:
                    code_output.extend(code_result.values.tolist())
            # Load inventory data
            for inv_item_df in lst_inv_df:
                try:
                    code_result = inv_item_df.loc[code_name]
                except KeyError:
                    # Alert! the zero input should be same quantity as available inventory month
                    code_output.extend([x * 0 for x in range(0, len(inv_item_df.columns))])
                else:
                    code_output.extend(code_result.values.tolist())
            # Load Forecast data
            for forecast_item_df in lst_forecast_df:
                try:
                    code_result = forecast_item_df.loc[code_name]
                except KeyError:
                    code_output.extend([x * 0 for x in range(0, len(forecast_item_df.columns))])
                else:
                    code_output.extend(code_result.values.tolist())
            snop_result.append(code_output)
            # count
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        # get end time
        time_end = time.time()
        print('')
        print('Time cost: ', int(time_end - time_start), 's')
        # Transfer to array
        array_output = np.array(snop_result)
        df_code = pd.DataFrame(array_output)
        return [df_code, lst_column_name]
        # Export to Excel
        # current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        # file_name = self.__class__.bu_name + "_SNOP_" + current_time + ".xlsx"
        # self.__class__.file_fullname = self.__class__.export_path + file_name
        # df.to_excel(self.__class__.file_fullname, sheet_name="Code", index=False,
        #             header=lst_column_name, freeze_panes=(1, 1))
        # print('Done~')

    def read_file_fullname(self):
        return self.__class__.file_fullname


class SNOPSummaryExport:
    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def get_top_sales_v2(self, sales_type, num=20):
        # link to db
        datasheet_name = self.__class__.bu_name + "_" + sales_type
        database_fullname = self.__class__.db_path + datasheet_name + ".db"
        # get current month and pre-year month
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        c.execute('SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER BY Month DESC')
        month_result = c.fetchall()
        month_list = [item[0] for item in month_result]
        current_month, pre_year_month = month_list[0], month_list[12]
        # get sales of current month
        title = sales_type + '_' + current_month.replace('-', '')
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_SAP_Price) AS ' + title + ' FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + current_month + '\" GROUP by Hierarchy_5 ORDER BY ' + title + ' DESC'
        df_sales = pd.read_sql(sql=sql_cmd, con=conn, index_col='Hierarchy_5')
        df_sales['Ratio'] = df_sales[title]/df_sales[title].sum()
        # get sales of last month
        title = sales_type + '_' + pre_year_month.replace('-', '')
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_SAP_Price) AS ' + title + ' FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + pre_year_month + '\" GROUP by Hierarchy_5 ORDER BY ' + title + ' DESC'
        df_sales_last_year = pd.read_sql(sql=sql_cmd, con=conn)
        df_sales_last_year['Hierarchy_5'] = df_sales_last_year['Hierarchy_5'].str.upper()
        df_sales_last_year = df_sales_last_year.set_index('Hierarchy_5')
        df_sales = df_sales.join(df_sales_last_year).join(self.get_pm())
        # return top
        return df_sales.head(num)

    def get_top_inv_v2(self, inv_type, num=20):
        # link to db
        datasheet_name = self.__class__.bu_name + "_" + inv_type
        database_fullname = self.__class__.db_path + datasheet_name + ".db"
        conn = sqlite3.connect(database_fullname)
        # get current month and pre-year month
        c = conn.cursor()
        c.execute('SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER BY Month DESC')
        month_result = c.fetchall()
        month_list = [item[0] for item in month_result]
        current_month, pre_year_month = month_list[0], month_list[12]
        # get current inv
        crt_title = inv_type + '_' + current_month.replace('-', '')
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_Standard_Cost) as ' + crt_title + ' FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + current_month + \
                  '\" AND Suzhou =\"N\" AND Phoenix = \"N\" GROUP by Hierarchy_5'
        df_inv = pd.read_sql(sql=sql_cmd, con=conn, index_col='Hierarchy_5')
        df_inv['Ratio'] = df_inv[crt_title] / df_inv[crt_title].sum()
        # get last year inv
        pre_title = inv_type + '_' + pre_year_month.replace('-', '')
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_Standard_Cost) as ' + pre_title + ' FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + pre_year_month + \
                  '\" AND Suzhou =\"N\" AND Phoenix = \"N\" GROUP by Hierarchy_5'
        df_inv_last_year = pd.read_sql(sql=sql_cmd, con=conn)
        df_inv_last_year['Hierarchy_5'] = df_inv_last_year['Hierarchy_5'].str.upper()
        df_inv_last_year = df_inv_last_year.set_index('Hierarchy_5')
        # sort and return top
        df_inv = df_inv.join(df_inv_last_year).join(self.get_pm()).sort_values([crt_title], ascending=False)
        return df_inv.head(num)

    # get dataframe for PM list
    def get_pm(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        datasheet_name = self.__class__.bu_name + '_PM_List'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT * FROM ' + datasheet_name
        df = pd.read_sql(con=conn, sql=sql_cmd, index_col='Hierarchy_5')
        return df

    # get monthly inventory of recent 6 months
    def get_monthly_inventory_list(self, inv_type, month_qty=6):
        # link to database
        datasheet_name = self.__class__.bu_name + "_" + inv_type
        database_fullname = self.__class__.db_path + datasheet_name + ".db"
        conn = sqlite3.connect(database_fullname)
        # get normal inventory
        sql_cmd_normal = "SELECT Month, sum(Value_Standard_Cost) AS Normal FROM " + datasheet_name + \
                         " WHERE Suzhou =\'N\' AND Phoenix = \'N\' GROUP BY Month ORDER BY Month"
        df_inv_normal = pd.read_sql(sql=sql_cmd_normal, con=conn, index_col='Month')
        # print(df_inv_normal.head(10))
        # get suzhou inventory
        sql_cmd_suzhou = "SELECT Month, sum(Value_Standard_Cost) AS Suzhou FROM " + datasheet_name + \
                         " WHERE Suzhou =\'Y\' GROUP BY Month ORDER BY Month"
        df_inv_suzhou = pd.read_sql(sql=sql_cmd_suzhou, con=conn, index_col='Month')
        # print(df_inv_suzhou.head(10))
        # get phoenix inventory
        sql_cmd_phoenix = "SELECT Month, sum(Value_Standard_Cost) AS Phoenix FROM " + datasheet_name + \
                          " WHERE Suzhou =\'N\' AND Phoenix = \'Y\' GROUP BY Month ORDER BY Month"
        df_inv_phoenix = pd.read_sql(sql=sql_cmd_phoenix, con=conn, index_col='Month')
        # get total inventory
        sql_cmd_total = "SELECT Month, sum(Value_Standard_Cost) AS Total FROM " + datasheet_name + \
                        " GROUP BY Month ORDER BY Month"
        df_inv_total = pd.read_sql(sql=sql_cmd_total, con=conn, index_col='Month')
        # print(df_inv_phoenix.head(10))
        df_inv = df_inv_normal.join(df_inv_phoenix)
        df_inv = df_inv.join(df_inv_suzhou)
        df_inv = df_inv.join(df_inv_total).tail(month_qty)
        return df_inv.stack().unstack(0)

    # get total inv and inventory month by IMS
    def get_total_inv_month(self):
        # get inventory
        df_jnj_inv = self._get_inventory_by_sap_price('JNJ_INV')
        df_lp_inv = self._get_inventory_by_sap_price('LP_INV')
        df_total_inv = df_jnj_inv.join(df_lp_inv)
        df_total_inv['Total_INV'] = df_total_inv['JNJ_INV'] + df_total_inv['LP_INV']
        df_total_inv['AVG_IMS'] = self._get_6m_avg_ims_sap_price()
        df_total_inv['Total_INV_Month'] = df_total_inv['Total_INV'] / df_total_inv['AVG_IMS']
        df_total_inv = df_total_inv.drop(columns=['AVG_IMS'], axis=1)
        # resort the list with data increase
        list_index = list(df_total_inv.index)
        list_index.reverse()
        df_total_inv = df_total_inv.reindex(index=list_index)
        return df_total_inv.stack().unstack(0)

    # get inventory value by sap price
    def _get_inventory_by_sap_price(self, inv_type):
        # link to database
        datasheet_name = self.__class__.bu_name + '_' + inv_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        # get normal inventory
        sql_cmd_normal = 'SELECT Month, sum(Value_SAP_Price) AS ' + inv_type + ' FROM ' + datasheet_name + \
                         ' WHERE Suzhou =\'N\' AND Phoenix = \'N\' GROUP BY Month ORDER BY Month DESC LIMIT 6'
        df_inv_normal = pd.read_sql(sql=sql_cmd_normal, con=conn, index_col='Month')
        return df_inv_normal

    # get recent avg ims data
    # month_qty; cycle numbers need to calculalte
    # avg_month_qty: months in cycle while calculating AVG
    def _get_6m_avg_ims_sap_price(self, month_qty=6, avg_month_qty=6):
        # link to database
        datasheet_name = self.__class__.bu_name + '_IMS'
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT Month, sum(Value_SAP_Price) as IMS FROM ' + datasheet_name + \
                  ' GROUP BY Month ORDER BY Month DESC'
        c = conn.cursor()
        c.execute(sql_cmd)
        ims_result = c.fetchall()
        # calculate AVG IMS
        list_avg_ims = []
        for i in range(month_qty):
            ims_6m_sum = 0
            for j in range(i, i+avg_month_qty):
                ims_6m_sum += ims_result[j][1]
            list_avg_ims.append(ims_6m_sum/6)
        return list_avg_ims

    # get monthly sales of recent 6 months
    def get_monthly_sales_summary(self, month_number=6):
        sales_type = ['GTS', 'LPSales', 'IMS']
        sales_result = []
        # read data
        for sales_item in sales_type:
            datasheet_name = self.__class__.bu_name + '_' + sales_item
            database_fullname = self.__class__.db_path + datasheet_name + '.db'
            conn = sqlite3.connect(database_fullname)
            sql_cmd = 'SELECT Month, sum(Value_SAP_Price) as ' + sales_item + ' FROM ' + datasheet_name + \
                      ' GROUP by Month ORDER by Month'
            sales_result.append(pd.read_sql(con=conn, sql=sql_cmd, index_col='Month'))
        # join the data
        df_sales = sales_result[0]
        df_sales = df_sales.join(sales_result[1])
        df_sales = df_sales.join(sales_result[2])
        # get last six rows
        df_sales_result = df_sales.tail(month_number)
        return df_sales_result.stack().unstack(0)

    def get_top_eso_v2(self, material_type, num=20):
        # check material type:
        instrument_trigger = 'Y' if material_type == 'Instrument' else 'N'
        # link to ESO db
        datasheet_name = self.__class__.bu_name + "_" + "ESO"
        database_fullname = self.__class__.db_path + datasheet_name + ".db"
        conn = sqlite3.connect(database_fullname)
        # get last two cycle
        c = conn.cursor()
        c.execute('SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 2')
        month_list = c.fetchall()
        [current_cycle_month, last_cycle_month] = [item[0] for item in month_list]
        # get eso of current cycle
        crt_title = 'ESO_' + material_type + '_' + current_cycle_month.replace('-', '')
        if material_type == 'NPI':
            sql_cmd = 'SELECT Hierarchy_5, sum(NPI_Reverse_Value) as ' + crt_title + ' FROM ' + datasheet_name + \
                      ' WHERE Month= \'' + current_cycle_month + '\' GROUP by Hierarchy_5'
        else:
            sql_cmd = 'SELECT Hierarchy_5, sum(Excess_Value + Obsolete_Value + Slow_Moving_Value) as ' + crt_title + \
                      ' FROM ' + datasheet_name + ' WHERE Instrument = \'' + instrument_trigger + \
                      '\' AND Suzhou = \'N\' AND Month = \'' + current_cycle_month + '\' GROUP by Hierarchy_5'
        df_eso = pd.read_sql(sql=sql_cmd, con=conn)
        # change to capitalized h5 name
        df_eso['Hierarchy_5'] = df_eso['Hierarchy_5'].str.upper()
        df_eso = df_eso.set_index('Hierarchy_5')
        # add ratio
        df_eso['Ratio'] = df_eso[crt_title] / df_eso[crt_title].sum()
        # get last cycle
        pre_title = 'ESO_' + material_type + '_' + last_cycle_month.replace('-', '')
        if material_type == 'NPI':
            sql_cmd = 'SELECT Hierarchy_5, sum(NPI_Reverse_Value) as ' + pre_title + ' FROM ' + datasheet_name + \
                      ' WHERE Month= \'' + last_cycle_month + '\' GROUP by Hierarchy_5'
        else:
            sql_cmd = 'SELECT Hierarchy_5, sum(Excess_Value + Obsolete_Value + Slow_Moving_Value) as ' + pre_title + \
                      ' FROM ' + datasheet_name + ' WHERE Instrument = \'' + instrument_trigger + \
                      '\' AND Suzhou = \'N\' AND Month = \'' + last_cycle_month + \
                      '\' GROUP by Hierarchy_5 COLLATE NOCASE'
        df_eso_pre = pd.read_sql(sql=sql_cmd, con=conn)
        # change to capitalized h5 name
        df_eso_pre['Hierarchy_5'] = df_eso_pre['Hierarchy_5'].str.upper()
        df_eso_pre = df_eso_pre.set_index('Hierarchy_5')
        # test
        # print(df_eso.head(), df_eso_pre.head())
        # combine and sort
        if material_type != 'Instrument':
            df_eso = df_eso.join(df_eso_pre).join(self.get_pm()).sort_values([crt_title], ascending=False)
        else:
            df_eso = df_eso.join(df_eso_pre).sort_values([crt_title], ascending=False)
        return df_eso.head(num)

    def snop_summary_generation(self):
        # writer = pd.ExcelWriter(self.__class__.file_fullname)
        # initiate list to export
        list_snop_summary = []

        # export 6 months JNJ inventory
        print('Export 6 months JNJ Inventory')
        df_jnj_monthly_inv = self.get_monthly_inventory_list('JNJ_INV')
        # df_jnj_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=1)
        list_snop_summary.append([df_jnj_monthly_inv, (1, 1)])

        # export 6 months LP inventory
        print('Export 6 months NED Inventory')
        df_lp_monthly_inv = self.get_monthly_inventory_list('LP_INV')
        # df_lp_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=6, startcol=1)
        list_snop_summary.append([df_lp_monthly_inv, (6, 1)])

        # export 6 months sales data
        print('Export 6 months sales data')
        df_six_month_sales = self.get_monthly_sales_summary(6)
        # df_six_month_sales.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=12, startcol=1)
        list_snop_summary.append([df_six_month_sales, (12, 1)])

        # export total inventory month
        print('Export total inventory month')
        df_total_inv_month = self.get_total_inv_month()
        list_snop_summary.append([df_total_inv_month, (18, 1)])

        # export top 20 gts products
        print('Export TOP GTS')
        df_top_gts = self.get_top_sales_v2("GTS")
        # df_top_gts.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=10)
        list_snop_summary.append([df_top_gts, (1, 10)])

        # export top 20 inv products
        print('Export TOP Inventory')
        df_top_jnj_inv = self.get_top_inv_v2('JNJ_INV')
        # df_top_jnj_inv.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=16)
        list_snop_summary.append([df_top_jnj_inv, (1, 16)])

        # export top 20 eso - Instrument
        print('Export TOP ESO - Instrument')
        df_top_instrument_eso = self.get_top_eso_v2('Instrument')
        # df_top_instrument_eso.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=22)
        list_snop_summary.append([df_top_instrument_eso, (1, 22)])

        # export top 20 eso - Implant
        print('Export TOP ESO - Implant')
        df_top_implant_eso = self.get_top_eso_v2('Implant')
        # df_top_implant_eso.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=28)
        list_snop_summary.append([df_top_implant_eso, (1, 28)])

        # export top 20 eso - Implant
        print('Export TOP ESO - NPI')
        df_top_implant_eso = self.get_top_eso_v2('NPI')
        # df_top_implant_eso.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=1, startcol=28)
        list_snop_summary.append([df_top_implant_eso, (1, 34)])

        return list_snop_summary
        # writer.close()


class SNOPHierarchy5Export:

    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"
    file_path = "../data/_Source_Data/"
    file_fullname = ""

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def set_file_fullname(self, file_name_input):
        self.__class__.file_fullname = file_name_input

    def get_hierarchy5_list(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        datasheet_name = self.__class__.bu_name + '_Master_Data'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT Hierarchy_5, count(Material) as Code_Qty FROM ' + datasheet_name + ' GROUP by Hierarchy_5'
        df_h5_all = pd.read_sql(sql=sql_cmd, con=conn, index_col='Hierarchy_5')
        return df_h5_all

    def get_pm_list(self):
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        datasheet_name = self.__class__.bu_name + '_PM_List'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT * FROM ' + datasheet_name
        df_pm_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Hierarchy_5')
        return df_pm_list

    def get_h5_sales_result(self, sale_type, year_type='current_year'):
        datasheet_name = self.__class__.bu_name + '_' + sale_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get latest month
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 1'
        c.execute(sql_cmd)
        month_result = c.fetchall()[0][0]
        title_in_list = sale_type
        if year_type == 'last_year':
            month_result = str(int(month_result[0:4]) - 1) + month_result[-3:]
            title_in_list = sale_type + '_Last_Year'
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_SAP_Price) as ' + title_in_list + '_Value FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + month_result + \
                  '\" GROUP BY Hierarchy_5 COLLATE NOCASE ORDER BY Hierarchy_5 COLLATE NOCASE'
        df_sales = pd.read_sql(sql=sql_cmd, con=conn)
        df_sales['Hierarchy_5'] = df_sales['Hierarchy_5'].str.upper()
        df_sales_result = df_sales.set_index('Hierarchy_5')
        return df_sales_result

    # get 6 month sales data with Standard Cost
    def get_h5_6m_sales(self, sales_type):
        datasheet_name = self.__class__.bu_name + '_' + sales_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get latest month
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 6'
        c.execute(sql_cmd)
        result = c.fetchall()
        month_result = [item[0] for item in result]
        str_month_list = generate_str_month_list(month_result)
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_Standard_Cost)/6 as SixMth_AVG_' + sales_type + ' FROM ' + datasheet_name \
                  + ' WHERE Month in (' + str_month_list + ') GROUP by Hierarchy_5 COLLATE NOCASE'
        df_avg_sales = pd.read_sql(sql=sql_cmd, con=conn)
        df_avg_sales['Hierarchy_5'] = df_avg_sales['Hierarchy_5'].str.upper()
        df_avg_sales_result = df_avg_sales.set_index('Hierarchy_5')
        return df_avg_sales_result

    def get_h5_inv(self, inv_type, year_type='current_year'):
        datasheet_name = self.__class__.bu_name + '_' + inv_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get latest month
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 1'
        c.execute(sql_cmd)
        month_result = c.fetchall()[0][0]
        title_in_list = inv_type
        # get the value of last year
        if year_type == 'last_year':
            month_result = str(int(month_result[0:4]) - 1) + month_result[-3:]
            title_in_list = inv_type + '_Last_Year'
        sql_cmd = 'SELECT Hierarchy_5, sum(Value_Standard_Cost) as ' + title_in_list + ' FROM ' + datasheet_name + \
                  ' WHERE Month = \"' + month_result + '\" GROUP BY Hierarchy_5 COLLATE NOCASE'
        df_inv = pd.read_sql(sql=sql_cmd, con=conn)
        df_inv['Hierarchy_5'] = df_inv['Hierarchy_5'].str.upper()
        df_inv_result = df_inv.set_index('Hierarchy_5')
        return df_inv_result

    def get_ytd_mapping_month_list(self, sales_type):
        datasheet_name = self.__class__.bu_name + '_' + sales_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get month list
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC'
        c.execute(sql_cmd)
        result = c.fetchall()
        month_list = [item[0] for item in result]
        current_year_index = month_list[0][:4]
        # get current year month list
        current_year_month_list = []
        for index_item, list_item in enumerate(month_list):
            if list_item[:4] == current_year_index:
                current_year_month_list.append(list_item)
            else:
                year_gap_index = index_item
                break
        # get last year month list
        last_year_month_list = month_list[12:12+year_gap_index]
        return [current_year_month_list, last_year_month_list]

    def generate_ytm_sales_mapping(self, sales_type):
        [current_year_month_list, last_year_month_list] = self.get_ytd_mapping_month_list(sales_type)
        datasheet_name = self.__class__.bu_name + '_' + sales_type
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT upper(Hierarchy_5) as Hierarchy_5, Month, sum(Value_SAP_Price) as Sales_Value FROM ' + \
                  datasheet_name + ' GROUP by Month, Hierarchy_5 COLLATE NOCASE'
        df_sales = pd.read_sql(con=conn, sql=sql_cmd)
        df_sales_result = pd.pivot_table(df_sales, index='Hierarchy_5', columns='Month', values='Sales_Value')
        df_current_year, df_last_year = df_sales_result.loc[:, current_year_month_list], df_sales_result.loc[:, last_year_month_list]
        # get ytm sales result
        df_current_year.loc[:, 'Current_Year_TTL'] = df_current_year.apply(lambda x: x.sum(), axis=1)
        df_last_year.loc[:, 'Last_Year_TTL'] = df_last_year.apply(lambda x: x.sum(), axis=1)
        # join and get the variance
        df_current_year = df_current_year.join(df_last_year)
        gap_title = sales_type + '_YTD_Gap'
        df_current_year.loc[:, gap_title] = df_current_year['Current_Year_TTL'] - df_current_year['Last_Year_TTL']
        return df_current_year[gap_title]

    def get_h5_backorder(self):
        datasheet_name = self.__class__.bu_name + '_JNJ_INV'
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get latest month
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 1'
        c.execute(sql_cmd)
        month_result = c.fetchall()[0][0]
        # get backorder code qty, qty, and value in sap price by h5
        sql_cmd = 'SELECT Hierarchy_5, count(Material) as BO_Codes, 0-sum(Available_Stock) as BO_Qty, ' \
                  '0-sum(Value_SAP_Price) as BO_Value FROM TU_JNJ_INV WHERE Month=\"' + month_result + \
                  '\" AND Available_Stock<0 GROUP by Hierarchy_5'
        df_backorder = pd.read_sql(sql=sql_cmd, con=conn, index_col='Hierarchy_5')
        return df_backorder

    def get_h5_eso(self):
        datasheet_name = self.__class__.bu_name + '_ESO'
        database_fullname = self.__class__.db_path + datasheet_name + '.db'
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        # get latest month
        sql_cmd = 'SELECT DISTINCT Month FROM ' + datasheet_name + ' ORDER by Month DESC LIMIT 1'
        c.execute(sql_cmd)
        month_result = c.fetchall()[0][0]
        sql_cmd = 'SELECT Hierarchy_5, sum(Excess_Quantity) as E_Qty, sum(Slow_Moving_Quantity) as SM_Qty, ' \
                  'sum(Obsolete_Quantity) as Q_Qty, sum(NPI_Reverse_Value) as NPI_ESO, sum(Total_ESO_Value) as ESO_Value FROM TU_ESO ' \
                  'WHERE Month=\"' + month_result + '\" GROUP by Hierarchy_5 COLLATE NOCASE'
        df_eso = pd.read_sql(sql=sql_cmd, con=conn)
        df_eso['Hierarchy_5'] = df_eso['Hierarchy_5'].str.upper()
        df_eso_result = df_eso.set_index('Hierarchy_5')
        return df_eso_result

    def generate_h5_summary_entrance(self):
        # get h5 list
        df_h5_list = self.get_hierarchy5_list()
        # get pm list
        df_pm_list = self.get_pm_list()
        df_result = df_h5_list.join(df_pm_list)
        # get gts result (including last year)
        df_gts_result = self.get_h5_sales_result('GTS')
        df_result = df_result.join(df_gts_result)
        df_gts_result_last_year = self.get_h5_sales_result('GTS', 'last_year')
        df_result = df_result.join(df_gts_result_last_year)
        # get LPsales result (including last year)
        df_lpsales_result = self.get_h5_sales_result('LPSales')
        df_result = df_result.join(df_lpsales_result)
        df_lpsales_result_last_year = self.get_h5_sales_result('LPSales', 'last_year')
        df_result = df_result.join(df_lpsales_result_last_year)
        # get IMS result (including last year)
        df_ims_result = self.get_h5_sales_result('IMS')
        df_result = df_result.join(df_ims_result)
        df_ims_result_last_year = self.get_h5_sales_result('IMS', 'last_year')
        df_result = df_result.join(df_ims_result_last_year)
        # get backorder
        df_backorder = self.get_h5_backorder()
        df_result = df_result.join(df_backorder)
        # get JNJ Inventory
        df_jnj_inv = self.get_h5_inv('JNJ_INV')
        df_result = df_result.join(df_jnj_inv)
        # get 6M AVG gts
        df_avg_gts = self.get_h5_6m_sales('GTS')
        df_result = df_result.join(df_avg_gts)
        df_result['JNJ_INV_Mth'] = df_result['JNJ_INV'] / df_result['SixMth_AVG_GTS']
        # get JNJ INV of last year
        df_jnj_inv_last_year = self.get_h5_inv('JNJ_INV', 'last_year')
        df_result = df_result.join(df_jnj_inv_last_year)
        # get LP Inventory
        df_lp_inv = self.get_h5_inv('LP_INV')
        df_result = df_result.join(df_lp_inv)
        # get 6M AVG LPsales
        df_avg_lpsales = self.get_h5_6m_sales('LPSales')
        df_result = df_result.join(df_avg_lpsales)
        df_result['LP_INV_Mth'] = df_result['LP_INV'] / df_result['SixMth_AVG_LPSales']
        # delete avg sales
        df_result.drop(['SixMth_AVG_GTS', 'SixMth_AVG_LPSales'], axis=1, inplace=True)
        # get LP Inventory of last year
        df_lp_inv_last_year = self.get_h5_inv('LP_INV', 'last_year')
        df_result = df_result.join(df_lp_inv_last_year)
        # get ESO
        df_eso = self.get_h5_eso()
        df_result = df_result.join(df_eso)
        # add YTM vs. last year
        df_result = df_result.join(self.generate_ytm_sales_mapping('GTS'))
        df_result = df_result.join(self.generate_ytm_sales_mapping('LPSales'))
        df_result = df_result.join(self.generate_ytm_sales_mapping('IMS'))
        # add gts and jnj_inv ranking
        df_result['GTS_Rank'] = df_result['GTS_Value'].rank(method='min', ascending=False)
        df_result['JNJ_INV_Rank'] = df_result['JNJ_INV'].rank(method='min', ascending=False)
        # Move two ranking to head
        df_item_gts_rank = df_result['GTS_Rank']
        df_item_jnj_inv_rank = df_result['JNJ_INV_Rank']
        df_result.drop(labels=['GTS_Rank'], axis=1, inplace=True)
        df_result.drop(labels=['JNJ_INV_Rank'], axis=1, inplace=True)
        df_result.insert(0, 'JNJ_INV_Rank', df_item_jnj_inv_rank)
        df_result.insert(0, 'GTS_Rank', df_item_gts_rank)
        # Export
        return df_result
        # writer = pd.ExcelWriter(self.__class__.file_fullname, mode='a')
        # df_result.to_excel(writer, sheet_name="H5", index=True, freeze_panes=(1, 1))
        # writer.close()
        # print("Done~")


class SNOPExportEntrance:
    bu_name = ""
    export_path = "../data/_Output/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def set_file_fullname(self, type):
        # current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        current_time = time.strftime("%Y%m", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_" + type + "_" + current_time + ".xlsx"
        return self.__class__.export_path + file_name

    def export_code_detail_file(self):
        # get dataframe of code detail
        print('Start to generate Code level page')
        snop_code_generation = SNOPCodeExport(self.__class__.bu_name)
        [df_code, lst_column_name] = snop_code_generation.generate_code_onesheet()
        print('Start to export code detail excel file')
        with pd.ExcelWriter(self.set_file_fullname('Code')) as writer:
            df_code.to_excel(writer, sheet_name="Code", index=False, header=lst_column_name, freeze_panes=(1, 1))
        print('Code detail was exported.')

    def export_summary_file(self):
        # get dataframe of Hierarchy_5 level
        print('Start to generate Hierarchy_5 level page')
        snop_h5_generation = SNOPHierarchy5Export(self.__class__.bu_name)
        df_h5 = snop_h5_generation.generate_h5_summary_entrance()
        # get summary of report wise
        print('Start to generate summary page.')
        snop_summary_generation = SNOPSummaryExport(self.__class__.bu_name)
        df_summary_page = snop_summary_generation.snop_summary_generation()
        # export to excel
        print('Start to export summary page to excel file')
        with pd.ExcelWriter(self.set_file_fullname('Summary')) as writer:
            df_h5.to_excel(writer, sheet_name="H5", index=True, freeze_panes=(1, 1))
            for item in df_summary_page:
                [df_summary, (row_num, col_num)] = item
                df_summary.to_excel(writer, sheet_name="SNOP_Summary", index=True, startrow=row_num, startcol=col_num)
        print('Summary page was exported.')

    def start_snop_export(self):
        # confirm if to start
        print('== SNOP Excel File Export ==')
        cmd_input = input('Please choose your option (1 - Code Detail, 2 - Summary Page , 0 - Both Page) : ')
        if cmd_input == '1':
            self.export_code_detail_file()
        elif cmd_input == '2':
            self.export_summary_file()
        elif cmd_input == '0':
            self.export_code_detail_file()
            self.export_summary_file()
        else:
            print('Wrong input, please try again~')
            return
        print('Done~')


if __name__ == '__main__':
    test_module = SNOPSummaryExport('TU')
    test_module.get_total_inv_month()

