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


class SNOPExportV2:

    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"
    file_path = "../data/_Source_Data/"

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
        sql_cmd = "SELECT * FROM " + datasheet_name
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
                                               'ESO_Quantity', 'ESO_Value_Standard_Cost'],
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
            print(sales_type_item, " is ready!")
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
            print(inv_type_item, " is ready!")
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
            print(forecast_type_item, " Forecast is ready!")
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
        print('Time cost: ', int(time_end - time_start), 's')
        print('List done, start to export to excel file')
        # Transfer to array
        array_output = np.array(snop_result)
        df = pd.DataFrame(array_output)
        # Export to Excel
        current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_" + current_time + ".xlsx"
        file_fullname = self.__class__.export_path + file_name
        df.to_excel(file_fullname, sheet_name="Code", index=False, header=lst_column_name, freeze_panes=(1, 1))
        print('Done~')


class SNOPSummaryExport:
    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def get_top_sales(self, sales_type, num=20):
        # get this cycle month and last cycle month
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -2)
        last_cycle_month, current_cycle_month = month_list[0], month_list[1]
        # link to db
        filename = self.__class__.bu_name + "_" + sales_type
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # Get this cycle top
        sql_cmd = "SELECT Hierarchy_5, sum(Value_SAP_Price) as TT_Value from " + filename + " WHERE Month = \'" + \
                  current_cycle_month + "\' GROUP by Hierarchy_5 ORDER by TT_Value DESC LIMIT " + str(num)
        c.execute(sql_cmd)
        result_this_cycle = c.fetchall()
        # Get sales value sum, ready for ratio calculation
        sql_cmd = "SELECT sum(Value_SAP_Price) from " + filename + " WHERE Month = \'" + current_cycle_month + "\'"
        c.execute(sql_cmd)
        sales_value_sum = c.fetchall()[0][0]
        for index in range(0, len(result_this_cycle)):
            h5_code = result_this_cycle[index][0]
            sql_cmd = "SELECT sum(Value_SAP_Price) as TT_Value from " + filename + " WHERE Month = \'" + \
                      last_cycle_month + "\' AND Hierarchy_5 = \'" + h5_code + "\'"
            c.execute(sql_cmd)
            # insert ratio
            result_this_cycle[index] += (result_this_cycle[index][1] / sales_value_sum,)
            # insert last cycle
            result_this_cycle[index] += (c.fetchall()[0][0],)
            # insert sequence
            result_this_cycle[index] = (str(index+1), ) + result_this_cycle[index]
        top_sales_title = [("No", "Hierarchy_5", sales_type + "_" + current_cycle_month, "Ratio",
                            sales_type + "_" + last_cycle_month), ]
        return top_sales_title + result_this_cycle

    def get_top_inv(self, inv_type, num=20):
        # get this cycle month and last cycle month
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -2)
        last_cycle_month, current_cycle_month = month_list[0], month_list[1]
        # link to db
        filename = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get value of this cycle
        sql_cmd = "SELECT Hierarchy_5, sum(Value_Standard_Cost) as tt_value FROM " + filename + " WHERE Month = \'" + \
                  current_cycle_month + "\' AND Suzhou =\'N\' AND Phoenix = \'N\' " \
                                        "GROUP by Hierarchy_5 ORDER BY tt_value DESC LIMIT " + str(num)
        c.execute(sql_cmd)
        result_this_cycle = c.fetchall()
        # get sum of inventory to calculate the ratio
        sql_cmd = "SELECT sum(Value_Standard_Cost) FROM " + filename + " WHERE Month = \'" + current_cycle_month + \
                  "\' AND Suzhou =\'N\' AND Phoenix = \'N\'"
        c.execute(sql_cmd)
        inv_value_sum = c.fetchall()[0][0]
        # get ratio and last cycle data
        for index in range(0, len(result_this_cycle)):
            h5_code = result_this_cycle[index][0]
            sql_cmd = "SELECT sum(Value_Standard_Cost) FROM " + filename + " WHERE Month = \'" + last_cycle_month + \
                      "\' AND Hierarchy_5 = \'" + h5_code + "\'"
            c.execute(sql_cmd)
            # insert ratio
            result_this_cycle[index] += (result_this_cycle[index][1] / inv_value_sum, )
            # insert last cycle
            result_this_cycle[index] += (c.fetchall()[0][0], )
            # insert sequence
            result_this_cycle[index] = (str(index + 1),) + result_this_cycle[index]
        top_inv_title = [("No", "Hierarchy_5", inv_type + "_" + current_cycle_month, "Ratio",
                            inv_type + "_" + last_cycle_month), ]
        return top_inv_title + result_this_cycle

    # Get monthly inventory
    def get_monthly_inventory_list(self, inv_type, month_qty):
        # Get inventory list
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, 0 - month_qty)
        # Initiate result list
        monthly_inv_result = []
        # Add title line
        list_title = ["Month", ]
        list_title.extend(month_list)
        monthly_inv_result.append(list_title)
        # Link JNJ DB
        filename = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get normal inventory
        monthly_inv_normal = ["Normal", ]
        for month_name in month_list:
            sql_cmd = "SELECT sum(Value_Standard_Cost) FROM " + filename + " WHERE Month = \'" + month_name + \
                      "\' AND Suzhou =\'N\' AND Phoenix = \'N\'"
            c.execute(sql_cmd)
            inv_normal = c.fetchall()[0]
            monthly_inv_normal.extend(inv_normal)
        monthly_inv_result.append(monthly_inv_normal)
        # Get suzhou inventory
        monthly_inv_suzhou = ["Suzhou", ]
        for month_name in month_list:
            sql_cmd = "SELECT sum(Value_Standard_Cost) FROM " + filename + " WHERE Month = \'" + month_name + \
                      "\' AND Suzhou =\'Y\'"
            c.execute(sql_cmd)
            inv_suzhou = c.fetchall()[0]
            if inv_suzhou[0] is None:
                monthly_inv_suzhou.append(0)
            else:
                monthly_inv_suzhou.extend(inv_suzhou)
        monthly_inv_result.append(monthly_inv_suzhou)
        # Get phoenix inventory
        monthly_inv_phoenix = ["Phoenix", ]
        for month_name in month_list:
            sql_cmd = "SELECT sum(Value_Standard_Cost) FROM " + filename + " WHERE Month = \'" + month_name + \
                      "\' AND Suzhou =\'N\' AND Phoenix = \'Y\'"
            df = pd.read_sql(sql=sql_cmd, con=conn)
            print(df.head())
            c.execute(sql_cmd)
            result = c.fetchall()[0][0]
            inv_phoenix = 0 if result is None else result
            monthly_inv_phoenix.extend(inv_phoenix)
        monthly_inv_result.append(monthly_inv_phoenix)
        # Add inventory Sum
        monthly_inv_sum = ["Total", ]
        for index in range(0, len(month_list)):
            monthly_inv_sum.append(monthly_inv_normal[index + 1] + monthly_inv_suzhou[index + 1] +
                                   monthly_inv_phoenix[index + 1])
        monthly_inv_result.append(monthly_inv_sum)
        return monthly_inv_result

    def get_top_eso(self, material_type, num=20):
        # check material type:
        if material_type == "Instrument":
            type_trigger = "Y"
        else:
            type_trigger = "N"
        # link to ESO db
        filename = self.__class__.bu_name + "_" + "ESO"
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get cycle list
        sql_cmd = "SELECT DISTINCT Month FROM " + filename
        c.execute(sql_cmd)
        cycle_list = c.fetchall()
        last_cycle_time, current_cycle_time = cycle_list[-2][0], cycle_list[-1][0]
        sql_cmd = "SELECT Hierarchy_5, sum(ESO_Value_Standard_Cost) as tt FROM " + filename + \
                  " WHERE Instrument = \'" + type_trigger + "\' AND Suzhou = \'N\' AND Month = \'" \
                  + current_cycle_time + "\' GROUP by Hierarchy_5 ORDER by tt DESC LIMIT " + str(num)
        c.execute(sql_cmd)
        eso_value_list = c.fetchall()
        # get eso total
        sql_cmd = "SELECT sum(ESO_Value_Standard_Cost) as tt FROM " + filename + " WHERE Instrument = \'" + \
                  type_trigger + "\' AND Suzhou = \'N\' AND Month = \'" + current_cycle_time + "\'"
        c.execute(sql_cmd)
        eso_value_total = c.fetchall()[0][0]
        for index in range(0, len(eso_value_list)):
            h5_code = eso_value_list[index][0]
            sql_cmd = "SELECT sum(ESO_Value_Standard_Cost) as tt FROM " + filename + " WHERE Instrument = \'" + \
                      type_trigger + "\' AND Suzhou = \'N\' AND Month = \'" + last_cycle_time + \
                      "\' AND Hierarchy_5 = \'" + h5_code + "\'"
            c.execute(sql_cmd)
            # insert ratio
            eso_value_list[index] += (eso_value_list[index][1] / eso_value_total, )
            # insert last cycle
            eso_value_list[index] += (c.fetchall()[0][0], )
            # insert sequence
            eso_value_list[index] = (str(index + 1),) + eso_value_list[index]
        top_eso_title = [("No", "Hierarchy_5", "ESO_" + material_type + "_" + current_cycle_time, "Ratio",
                          "ESO_" + material_type + "_" + last_cycle_time), ]
        return top_eso_title + eso_value_list

    def snop_summary_generation(self):
        # open file
        print('Open Blank Excel File.')
        current_time = time.strftime("%y%m%d", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_TEST_" + current_time + ".xlsx"
        file_fullname = self.__class__.export_path + file_name
        writer = pd.ExcelWriter(file_fullname)

        # export 6 months JNJ inventory
        print('Export 6 months JNJ Inventory')
        six_month_jnj_inv = self.get_monthly_inventory_list("JNJ_INV", 6)
        np_jnj_monthly_inv = np.array(six_month_jnj_inv)
        df_jnj_monthly_inv = pd.DataFrame(data=np_jnj_monthly_inv[1:, 0:], columns=np_jnj_monthly_inv[0, 0:])
        df_jnj_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=1)

        # export 6 months LP inventory
        print('Export 6 months NED Inventory')
        six_month_lp_inv = self.get_monthly_inventory_list("LP_INV", 6)
        np_lp_monthly_inv = np.array(six_month_lp_inv)
        df_lp_monthly_inv = pd.DataFrame(data=np_lp_monthly_inv[1:, 0:], columns=np_lp_monthly_inv[0, 0:])
        df_lp_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=6, startcol=1)

        # export top 20 gts products
        print('Export TOP GTS')
        top_gts_list = self.get_top_sales("GTS")
        np_top_gts = np.array(top_gts_list)
        df_top_gts = pd.DataFrame(data=np_top_gts[1:, 0:], columns=np_top_gts[0, 0:])
        # export gts, start from
        df_top_gts.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=10)

        # export top 20 inv products
        print('Export TOP Inventory')
        top_jnj_inv_list = self.get_top_inv("JNJ_INV")
        np_top_jnj_inv = np.array(top_jnj_inv_list)
        df_top_jnj_inv = pd.DataFrame(data=np_top_jnj_inv[1:, 0:], columns=np_top_jnj_inv[0, 0:])
        # export inv to excel
        df_top_jnj_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=16)

        # export top 20 eso - Instrument
        print('Export TOP ESO - Instrument')
        top_instrument_eso_list = self.get_top_eso("Instrument")
        np_top_instrument_eso = np.array(top_instrument_eso_list)
        df_top_instrument_eso = pd.DataFrame(data=np_top_instrument_eso[1:, 0:], columns=np_top_instrument_eso[0, 0:])
        # export instrument eso to excel
        df_top_instrument_eso.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=22)

        # export top 20 eso - Implant
        print('Export TOP ESO - Implant')
        top_implant_eso_list = self.get_top_eso("Implant")
        np_top_implant_eso = np.array(top_implant_eso_list)
        df_top_implant_eso = pd.DataFrame(data=np_top_implant_eso[1:, 0:], columns=np_top_implant_eso[0, 0:])
        # export instrument eso to excel
        df_top_implant_eso.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=28)

        writer.close()


if __name__ == '__main__':
    # TestModule = SNOPExportV2("TU")
    # TestModule.get_statistical_forecast_list(['2020-06', '2020-07'], 'Final')
    # TestModule.generate_code_onesheet()
    TestSummaryModule = SNOPSummaryExport('TU')
    TestSummaryModule.snop_summary_generation()
