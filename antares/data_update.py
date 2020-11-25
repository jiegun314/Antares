# import os, sys
import json
import sqlite3
import pandas as pd
import calculation as cclt
import time
import os
# import math
# import data_import as dtimp
import numpy as np
from datetime import datetime


class MonthlyUpdate:
    bu_name = ""
    update_path = "../data/_Update/"
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    def update_sales_with_pandas(self, inv_type):
        print("==" + inv_type + " Import==")
        # 输入Y确认进行导入
        print("--*Warning* - Please make sure data is correctly named and put in _Update folder.")
        cmd_key = input("Ready to continue? (Y/N): ")
        if cmd_key.upper() != "Y":
            return
        # read excel file
        print("==Start to read the data==")
        file_name = self.__class__.update_path + "Update_" + self.__class__.bu_name + "_" + inv_type + ".xlsx"
        df_qty = pd.read_excel(file_name, dtype={'Month': object}, index_col='Material')
        print("==Reading complete, start to map master data==")
        # read master data
        master_data_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        conn = sqlite3.connect(master_data_fullname)
        table_name = self.__class__.bu_name + "_Master_Data"
        sql_cmd = 'SELECT Material, Standard_Cost, SAP_Price, Hierarchy_4, Hierarchy_5 FROM ' + table_name
        df_master_data = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # join and calculate value
        df_sales = df_qty.join(df_master_data)
        df_sales['Value_Standard_Cost'] = df_sales['Quantity'] * df_sales['Standard_Cost']
        df_sales['Value_SAP_Price'] = df_sales['Quantity'] * df_sales['SAP_Price']
        df_sales['Business_Unit'] = self.__class__.bu_name
        df_sales.drop(columns=['Standard_Cost', 'SAP_Price'], inplace=True)
        df_sales.reset_index(inplace=True)
        # write to db
        print("==Mapping complete, start to import to database==")
        file_name = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        df_sales.to_sql(name=file_name, con=conn, index=False, if_exists='append')
        print("===== <%s Import Successfully!> =====" % inv_type)
        pass

    def update_sales(self, inv_type):
        print("==" + inv_type + " Import==")
        # 输入Y确认进行导入
        print("--*Warning* - Please make sure data is correctly named and put in _Update folder.")
        cmd_key = input("Ready to continue? (Y/N): ")
        if cmd_key.upper() != "Y":
            return
        # read excel file
        print("==Start to read the data==")
        file_name = self.__class__.update_path + "Update_" + self.__class__.bu_name + "_" + inv_type + ".xlsx"
        df = pd.read_excel(file_name, dtype={'Month': object})
        lst_material = np.array(df).tolist()
        print("==Reading complete, start to map master data==")
        # 实例化一个查询对象
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        # 数据整合
        for material_item in lst_material:
            # get master data
            material_code = material_item[0]
            master_data_list = ['Standard_Cost', 'Hierarchy_4', 'Hierarchy_5', 'SAP_Price']
            master_data_result = info_check.get_single_code_all_master_data(material_code, master_data_list)
            [md_standard_cost, md_h4_name, md_h5_name, md_sap_price] = master_data_result
            # 插入std cost价格
            if not md_standard_cost:
                material_item.append(0)
            else:
                material_item.append(md_standard_cost * material_item[2])
            # 插入sap价格
            if not md_sap_price:
                material_item.append(0)
            else:
                material_item.append(md_sap_price * material_item[2])
            # Insert BU name, h4 and h5 name
            material_item.append(self.__class__.bu_name)
            material_item.append(md_h4_name)
            material_item.append(md_h5_name)
        # 插入数据库
        print("==Mapping complete, start to import to database==")
        file_name = self.__class__.bu_name + "_" + inv_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        conn.executemany("INSERT INTO " + file_name + " values (?,?,?,?,?,?,?,?)", lst_material)
        conn.commit()
        conn.close()
        print("===== <%s Import Successfully!> =====" % inv_type)

    def update_lp_inv(self):
        print("==LP Inventory Import==")
        print("--*Warning* - Please make sure data is correctly name and put in _Update folder.")
        # 输入Y确认进行导入
        cmd_key = input("Ready to continue? (Y/N):")
        if cmd_key.upper() != "Y":
            return
        print("==Start to read the data==")
        file_name = self.__class__.update_path + "Update_" + self.__class__.bu_name + "_LP_INV.xlsx"
        df = pd.read_excel(file_name, dtype={'Month': object})
        lst_lp_inv = np.array(df).tolist()
        print("==Reading complete, start to map master data==")
        # 实例化一个查询对象
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        # 数据整合
        for material_item in lst_lp_inv:
            # get master data
            material_code = material_item[0]
            master_data_list = ['Standard_Cost', 'Hierarchy_4', 'Hierarchy_5', 'Phoenix_Status', 'SAP_Price']
            master_data_result = info_check.get_single_code_all_master_data(material_code, master_data_list)
            [md_standard_cost, md_h4_name, md_h5_name, md_phoenix_status, md_sap_price] = master_data_result
            md_suzhou_status = "Y" if material_code[-2:] == "CN" else "N"
            # 插入std cost价格
            if not md_standard_cost:
                material_item.append(0)
            else:
                material_item.append(md_standard_cost * material_item[2])
            # 插入SAP Price价格
            if not md_sap_price:
                material_item.append(0)
            else:
                material_item.append(md_sap_price * material_item[2])
            # 插入BU, h4, h5
            material_item.append(self.__class__.bu_name)
            material_item.append(md_h4_name)
            material_item.append(md_h5_name)
            # 插入Suzhou属性
            material_item.append(md_suzhou_status)
            # 插入Phoenix属性
            material_item.append(md_phoenix_status)
        # 插入数据库
        print("==Reading complete, start importing to database==")
        tbl_name = self.__class__.bu_name + "_LP_INV"
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        conn.executemany("INSERT INTO " + tbl_name + " values (?,?,?,?,?,?,?,?,?,?)", lst_lp_inv)
        conn.commit()
        conn.close()
        print("===== <LP Inventory Import Successfully!> =====")

    def update_jnj_inv_with_pandas(self):
        print("==JNJ Inventory Import==")
        import_date = input("Please input the date your want to import (YYYYMMDD): ")
        # Get inventory month
        str_month = import_date[0:4] + "-" + import_date[4:6]
        import_tbl_name = "INV" + import_date
        db_fullname = self.__class__.db_path + "TU_CRT_INV.db"
        # check if this date is available in list
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        sql_cmd = "SELECT count(*) FROM sqlite_master where type = \'table\' and name = \'" + import_tbl_name + "\'"
        c.execute(sql_cmd)
        tbl_result = c.fetchone()[0]
        if tbl_result == 0:
            print("!Error. Wrong date input, please re-input. ")
            return
        # read raw data
        sql_cmd = "SELECT Material, Inventory_OnHand, Available_Stock, Pending_Inventory_Bonded_Total_Qty, " \
                  "Pending_Inventory_Bonded_Q_Hold_Qty, Pending_Inventory_NonB_Total_Qty, SS as Safety_Stock FROM " \
                  + import_tbl_name + " Order by Available_Stock DESC"
        df_jnj_inv = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        df_jnj_inv.fillna(0, inplace=True)
        df_jnj_inv = df_jnj_inv.astype('int')
        # insert month
        df_jnj_inv['Month'] = str_month
        col_month = df_jnj_inv.pop('Month')
        df_jnj_inv.insert(0, 'Month', col_month)
        # read master data
        master_database = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        master_table_name = self.__class__.bu_name + '_Master_Data'
        conn = sqlite3.connect(master_database)
        sql_cmd = 'SELECT Material, Hierarchy_4, Hierarchy_5, Standard_Cost, SAP_Price, PM, Instrument, ' \
                  'Phoenix_Status as Phoenix FROM ' + master_table_name
        df_master_data = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        df_master_data.fillna(0, inplace=True)
        # join the dataframe
        df_jnj_inv = df_jnj_inv.join(df_master_data)
        # calculate inventory value
        df_jnj_inv['Value_Standard_Cost'] = df_jnj_inv['Available_Stock'] * df_jnj_inv['Standard_Cost']
        df_jnj_inv['Value_SAP_Price'] = df_jnj_inv['Available_Stock'] * df_jnj_inv['SAP_Price']
        df_jnj_inv['Pending_NB_Std_Cost'] = df_jnj_inv['Pending_Inventory_NonB_Total_Qty'] * df_jnj_inv[
            'Standard_Cost']
        df_jnj_inv['Pending_NB_SAP_Price'] = df_jnj_inv['Pending_Inventory_NonB_Total_Qty'] * df_jnj_inv[
            'SAP_Price']
        df_jnj_inv['Pending_B_Std_Cost'] = df_jnj_inv['Pending_Inventory_Bonded_Total_Qty'] * df_jnj_inv[
            'Standard_Cost']
        df_jnj_inv['Pending_B_SAP_Price'] = df_jnj_inv['Pending_Inventory_Bonded_Total_Qty'] * df_jnj_inv[
            'SAP_Price']
        df_jnj_inv['Total_Inventory'] = df_jnj_inv['Available_Stock'] + df_jnj_inv[
            'Pending_Inventory_Bonded_Total_Qty'] + df_jnj_inv['Pending_Inventory_NonB_Total_Qty']
        df_jnj_inv['Total_Inventroy_Std_Cost'] = df_jnj_inv['Total_Inventory'] * df_jnj_inv['Standard_Cost']
        df_jnj_inv['Total_Inventory_SAP_Price'] = df_jnj_inv['Total_Inventory'] * df_jnj_inv['SAP_Price']
        # remove price
        df_jnj_inv.drop(columns=['Standard_Cost', 'SAP_Price'], inplace=True)
        # reset index
        df_jnj_inv.reset_index(inplace=True)
        # add Suzhou
        df_jnj_inv['Suzhou'] = 'N'
        df_jnj_inv.loc[df_jnj_inv['Material'].str.contains('CN'), 'Suzhou'] = 'Y'
        # write back to database
        inventory_database = self.__class__.db_path + self.__class__.bu_name + '_JNJ_INV.db'
        inventory_table = self.__class__.bu_name + '_JNJ_INV'
        conn = sqlite3.connect(inventory_database)
        df_jnj_inv.to_sql(name=inventory_table, con=conn, index=False, if_exists='append')
        print("===== <JNJ Inventory Import Successfully!> =====")

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
        sql_cmd = "SELECT Material, Inventory_OnHand, Available_Stock, Pending_Inventory_Bonded_Total_Qty, " \
                  "Pending_Inventory_Bonded_Q_Hold_Qty, Pending_Inventory_NonB_Total_Qty, SS FROM " \
                  + import_tbl_name + " Order by Available_Stock DESC"
        c.execute(sql_cmd)
        lst_jnj_inv = []
        inv_output = c.fetchall()
        # 转成列表，插入月份
        for material_item in inv_output:
            item_jnj_inv = list(material_item)
            item_jnj_inv.insert(0, str_month)
            lst_jnj_inv.append(item_jnj_inv)
        # 实例化一个查询对象
        info_check = cclt.InfoCheck(self.__class__.bu_name)
        # 计数变量
        counter, num = 0, 5
        list_show = list(range(int(len(lst_jnj_inv) / 20), len(lst_jnj_inv) + 1, int(len(lst_jnj_inv) / 20)))
        # 数据整合
        for material_item in lst_jnj_inv:
            # get master data
            material_code = material_item[1]
            # master_data_result = info_check.get_master_data(material_code)[1]
            # md_standard_cost = master_data_result[6]
            # md_h4_name = master_data_result[2]
            # md_h5_name = master_data_result[3]
            # md_phoenix_status = "Y" if info_check.get_code_phoenix_result(material_code)[0] == "Phoenix Product" else "N"
            # md_suzhou_status = "Y" if material_code[-2:] == "CN" else "N"
            # md_instrument_status = info_check.get_bu_master_data(material_code, "Instrument")
            # md_pm_status = info_check.get_bu_master_data(material_code, "PM")
            # # get sap price
            # md_sap_price = info_check.get_code_sap_price(material_code)
            master_data_list = ['Standard_Cost', 'Hierarchy_4', 'Hierarchy_5', 'Phoenix_Status', 'SAP_Price', 'PM']
            master_data_result = info_check.get_single_code_all_master_data(material_code, master_data_list)
            [md_standard_cost, md_h4_name, md_h5_name, md_phoenix_status, md_sap_price, md_pm] = master_data_result
            # change blank PM to "N/A"
            md_pm = "N/A" if md_pm is None else md_pm
            md_suzhou_status = "Y" if material_code[-2:] == "CN" else "N"
            md_instrument_status = 'N' if material_code[0:1] in ['2', '4'] or material_code[0:2] in ['02', '04']\
                                          or material_code[0:3] == 'CNB' else 'Y'
            # 设定价格
            item_std_cost = md_standard_cost if md_standard_cost else 0
            item_sap_price = md_sap_price if md_sap_price else 0
            # 插入Value_Standard_Cost
            material_item.append(item_std_cost * material_item[3])
            # 插入Value_SAP_Price
            material_item.append(item_sap_price * material_item[3])
            # 插入Pending_NB_Std_Cost
            material_item.append(item_std_cost * material_item[6])
            # 插入Pending_NB_SAP_Price
            material_item.append(item_sap_price * material_item[6])
            # 插入Pending_B_Std_Cost
            material_item.append(item_std_cost * material_item[4])
            # 插入Pending_B_SAP_Price
            material_item.append(item_sap_price * material_item[4])
            # 插入 Total_Inventory, Total_Inventory_Std_Cost, Total_Inventory_SAP_Price
            total_inv_qty = material_item[3] + material_item[4] + material_item[6]
            material_item.extend([total_inv_qty, total_inv_qty * item_std_cost, total_inv_qty * item_sap_price])
            # 插入 h4, h5, pm, instrument, suzhou, phoenix六个特殊属性
            material_item.extend([md_h4_name, md_h5_name, md_pm, md_instrument_status,
                                  md_suzhou_status, md_phoenix_status])
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        # 插入数据库
        print(" ")
        print("==Reading complete, start importing to database==")
        tbl_name = self.__class__.bu_name + "_JNJ_INV"
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        conn = sqlite3.connect(db_fullname)
        conn.executemany("INSERT INTO " + tbl_name + " values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         lst_jnj_inv)
        conn.commit()
        conn.close()
        print("===== <JNJ Inventory Import Successfully!> =====")

    def update_eso(self):
        file_name = self.__class__.bu_name + '_ESO'
        file_fullname = self.__class__.update_path + 'Update_' + file_name + '.xlsx'
        eso_db_fullname = self.__class__.db_path + file_name + '.db'
        master_data_filename = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        master_data_sheetname = self.__class__.bu_name + '_Master_Data'
        # read excel
        print("Start to read the Excel file")
        df_eso = pd.read_excel(file_fullname, index_col='Material')
        df_eso['Total_ESO_Quantity'] = df_eso['Excess_Quantity'] + df_eso['Obsolete_Quantity'] + df_eso['Slow_Moving_Quantity']
        # print(df_eso.head(), df_eso.info())
        # read master data
        conn = sqlite3.connect(master_data_filename)
        sql_cmd = 'SELECT Material, Hierarchy_5, PM, Phoenix_Status, Instrument FROM ' + master_data_sheetname
        df_master_data = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # print(df_master_data.head(), df_master_data.info())
        df_eso = df_eso.join(df_master_data)
        # judge Suzhou products
        df_eso['Suzhou'] = 'N'
        df_eso.loc[df_eso.index.str.endswith('CN'), 'Suzhou'] = 'Y'
        # df_eso.to_csv(self.__class__.db_path + 'Test.csv', index=True)
        # print(df_eso.head(), df_eso.info())
        conn = sqlite3.connect(eso_db_fullname)
        df_eso.to_sql(file_name, con=conn, if_exists='append')
        print('ESO updated')

    # import final forecast
    def update_final_forecast(self):
        print("==Final Forecast Import==")
        file_name = self.__class__.bu_name + "_Forecast"
        file_fullname = self.__class__.update_path + "Update_" + file_name + ".xlsx"
        print("Warning - Make sure you've put file %s under update folder." % file_name)
        if input("Ready to proceed? (Y/N): ").upper() != 'Y':
            return
        print("Start to read forecast file")
        df_forecast = pd.read_excel(file_fullname, index_col='Material').fillna(0)
        # get month list
        month_list = df_forecast.columns.values.tolist()
        month_length = len(month_list)
        # get code list
        code_list = df_forecast.index.values.tolist()
        # get hierarchy name and sap_price
        database_full_name = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        datafile_name = self.__class__.bu_name + '_Master_Data'
        conn = sqlite3.connect(database_full_name)
        sql_cmd = 'SELECT Material, Hierarchy_5, SAP_Price FROM ' + datafile_name
        df_master_data = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # print(df_forecast.head(), df_master_data.head())
        df_forecast = df_forecast.join(df_master_data)
        df_forecast.fillna(0, inplace=True)
        # merge sap value
        print("Start to generate forecast in value format")
        # print(df_forecast.head())
        for index in range(0, len(month_list)):
            column_name = 'Value_' + month_list[index]
            df_forecast[column_name] = df_forecast.apply(lambda x: x[month_list[index]] * x['SAP_Price'], axis=1)
        print("Convert to import list")
        forecast_to_upload = []
        for code_item in code_list:
            # add code and hierarchy_5
            list_item_basic_info = [code_item, df_forecast.at[code_item, 'Hierarchy_5']]
            # add value
            for month_item in month_list:
                list_item_unit = list_item_basic_info + [month_item, df_forecast.at[code_item, month_item],
                                                         df_forecast.at[code_item, 'Value_' + month_item]]
                forecast_to_upload.append(list_item_unit)
        # change to dataframe for upload
        dict_forecast_upload = {'Material': [item[0] for item in forecast_to_upload],
                                'Hierarchy_5': [item[1] for item in forecast_to_upload],
                                'Month': [item[2] for item in forecast_to_upload],
                                'Quantity': [item[3]*1 for item in forecast_to_upload],
                                'Value_SAP_Price': [item[4]*1 for item in forecast_to_upload]}
        df_forecast_upload = pd.DataFrame(dict_forecast_upload)
        # write to final forecast
        # print(df_forecast_upload.info())
        print("Update to database as final forecast")
        tbl_final_fcst = self.__class__.bu_name + "_Final_Forecast"
        db_final_fcst_fullname = self.__class__.db_path + tbl_final_fcst + ".db"
        tbl_name = tbl_final_fcst + "_" + time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(db_final_fcst_fullname)
        # df_forecast_upload.to_csv('test.csv')
        df_forecast_upload.to_sql(tbl_name, conn, index=False, if_exists='replace')
        # df_forecast.to_sql('TEMP', conn, index=True, if_exists='replace')
        conn.commit()
        conn.close()
        print("Final forecast updated!~")

    def data_update_entrance(self, cmd):
        if cmd == "901":
            self.update_sales_with_pandas("GTS")
        elif cmd == "902":
            self.update_sales_with_pandas("LPSales")
        elif cmd == "903":
            self.update_sales_with_pandas("IMS")
        elif cmd == '905':
            self.update_jnj_inv_with_pandas()
        elif cmd == "906":
            self.update_lp_inv()
        elif cmd == "908":
            self.update_final_forecast()
        elif cmd == "909":
            self.update_eso()
        else:
            print("!!Error: wrong user name, please restart the program.")


class MasterDataConsolidation:
    db_path = "../data/_DB/"

    def __init__(self):
        pass

    @property
    def bu_name(self):
        return self._bu_name

    @bu_name.setter
    def bu_name(self, value):
        self._bu_name = value

    def master_data_update_entrance(self, model='Normal'):
        print("==Start to refresh master data for %s==" % self._bu_name)
        # read master data
        df_master_data = self.import_material_master(model)
        # get code list
        print('--1. Getting Material Master--')
        code_list = df_master_data["Material"].tolist()
        hierarchy_5_list = df_master_data["Hierarchy_5"].tolist()
        # get sap price
        print('--2. Getting SAP Price--')
        df_master_data['SAP_Price'] = self.mapping_sap_price(code_list)
        # get ranking
        print('--3. Getting Ranking--')
        df_master_data['Ranking'] = self.mapping_abc_ranking(code_list)
        # get ROP setting
        print('--4. Getting MRP Type--')
        [mrp_type, reorder_point] = self.mapping_rop_setting(code_list)
        df_master_data['MRP_Type'] = mrp_type
        df_master_data['Reorder_Point'] = reorder_point
        # get phoenix status
        print('--5. Getting Phoenix Status--')
        [phoenix_status, target_sku, discontinuation_date, obsolescence_date] = self.mapping_phoenix_setting(code_list)
        df_master_data['Phoenix_Status'] = phoenix_status
        df_master_data['Phoenix_Target_SKU'] = target_sku
        df_master_data['Phoenix_Discontinuation_Date'] = discontinuation_date
        df_master_data['Phoenix_Obsolescence_Date'] = obsolescence_date
        # get GTIN
        print('--6. Getting GTIN--')
        df_master_data['GTIN'] = self.mapping_gtin(code_list)
        # get RAG
        print('--7. Getting RAG--')
        df_master_data['RAG'] = self.mapping_rag(code_list)
        # get PM
        print('--8. Getting PM List--')
        df_master_data['PM'] = self.mapping_pm(hierarchy_5_list)
        # update instrument PM
        df_master_data.loc[
            (~df_master_data['Material'].str.slice(stop=1).isin(['2', '4', '7'])) &
            (~df_master_data['Material'].str.slice(stop=2).isin(['02', '04', '07'])) &
            (df_master_data['Material'].str.slice(stop=3) != 'CNB'), 'PM'] = 'Instrument'
        # write back to database
        # print(df_master_data.head())
        self.finalize_master_data(df_master_data, model)

    def finalize_master_data(self, df, model):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        if model == 'Normal':
            data_sheet = self._bu_name + '_Master_Data'
        else:
            data_sheet = self._bu_name + '_Master_Data_Demo'
        conn = sqlite3.connect(database_file)
        df.to_sql(data_sheet, con=conn, index=False, if_exists='replace')
        print('--Done--')

    def import_material_master(self, model):
        database_file = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_file)
        if model == 'Normal':
            sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self._bu_name + '\"'
        else:
            sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self._bu_name + '\" LIMIT 100'
        df = pd.read_sql(sql=sql_cmd, con=conn)
        return df

    def mapping_sap_price(self, code_list):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = self._bu_name + '_SAP_Price'
        lst_sap_price = []
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT Price FROM ' + data_sheet + ' WHERE Material = \"' + code_item + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_sap_price.append(result[0][0])
            else:
                lst_sap_price.append(0.0)
        return lst_sap_price

    def mapping_abc_ranking(self, code_list):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = 'Ranking'
        lst_ranking = []
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT Ranking FROM ' + data_sheet + ' WHERE Material = \"' + code_item + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_ranking.append(result[0][0])
            else:
                lst_ranking.append("C")
        return lst_ranking

    def mapping_rop_setting(self, code_list):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = self._bu_name + '_ROP_Setting'
        lst_rop_setting = [[], []]
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT [MRP Type], [Reorder Point] FROM ' + data_sheet + ' WHERE Material = \"' + \
                      code_item + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_rop_setting[0].append(result[0][0])
                lst_rop_setting[1].append(result[0][1])
            else:
                lst_rop_setting[0].append("ND")
                lst_rop_setting[1].append(0)
        return lst_rop_setting

    def mapping_phoenix_setting(self, code_list):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = self._bu_name + '_Phoenix_List'
        lst_phoenix = [[], [], [], []]
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT [Target SKU], [Discontinuation Date], [Obsolescence Date] FROM ' + data_sheet \
                      + ' WHERE [Exit SKU] = \"' + code_item + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_phoenix[0].append("Y")
                lst_phoenix[1].append(result[0][0])
                lst_phoenix[2].append(result[0][1])
                lst_phoenix[3].append(result[0][2])
            else:
                lst_phoenix[0].append("N")
                lst_phoenix[1].append(None)
                lst_phoenix[2].append(None)
                lst_phoenix[3].append(None)
        return lst_phoenix

    def mapping_gtin(self, code_list):
        lst_gtin = []
        database_file = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT Barcode FROM GTIN WHERE [Material code] = \"' + code_item + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_gtin.append(result[0][0])
            else:
                lst_gtin.append(0)
        return lst_gtin

    def mapping_rag(self, code_list):
        lst_rag = []
        conn = sqlite3.connect(self.__class__.db_path + "Master_Data.db")
        c = conn.cursor()
        for code_item in code_list:
            sql_cmd = 'SELECT REGLICNO, REGAPDATE, REGEXDATE, LIFEYEAR FROM RAG_Report WHERE MATNR = \"' + \
                      code_item + '\" ORDER BY REGAPDATE'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                dict_rag = {}
                for i in range(len(result)):
                    dict_element_rag = {}
                    for j in range(len(result[i])):
                        dict_element_rag["REGLICNO"] = result[i][0]
                        dict_element_rag["REGAPDATE"] = result[i][1]
                        dict_element_rag["REGEXDATE"] = result[i][2]
                        dict_element_rag["LIFEYEAR"] = result[i][3]
                    dict_rag[str(i + 1)] = dict_element_rag
                lst_rag.append(json.dumps(dict_rag))
                # lst_rag.append(str(result))
            else:
                lst_rag.append(None)
        return lst_rag

    def mapping_pm(self, h5_list):
        lst_pm = []
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = self._bu_name + '_PM_List'
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        for h5_code in h5_list:
            sql_cmd = 'SELECT PM FROM ' + data_sheet + ' WHERE Hierarchy_5 = \"' + h5_code + '\"'
            c.execute(sql_cmd)
            result = c.fetchall()
            if result:
                lst_pm.append(result[0][0])
            else:
                lst_pm.append('NA')
        return lst_pm


class MasterDataConsolidationV2:
    db_path = '../data/_DB/'
    bu_name = ''

    def __init__(self, bu_name_input):
        self.__class__.bu_name = bu_name_input

    # get df of material master
    def import_material_master(self, model):
        database_file = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_file)
        if model == 'Normal':
            sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self.__class__.bu_name + '\"'
        else:
            sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self.__class__.bu_name + '\"'
        df = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        return df

    def import_sap_price(self):
        database_file = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_sheet = self.__class__.bu_name + '_SAP_Price'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT Material, Price as SAP_Price FROM ' + data_sheet
        df = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        return df

    def import_abc_ranking(self):
        database_file = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_sheet = 'Ranking'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT Material, Ranking FROM ' + data_sheet
        df = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        return df

    def import_rop_setting(self):
        database_file = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_sheet = self.__class__.bu_name + '_ROP_Setting'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT Material, [MRP Type] as MRP_Type, [Reorder Point] as Reorder_Point FROM ' + data_sheet
        df = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        return df

    def import_phoenix_setting(self):
        database_file = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        data_sheet = self.__class__.bu_name + '_Phoenix_List'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT [Exit SKU] as Material, Program as Phoenix_Status, [Target SKU] as Phoenix_Target_SKU, ' \
                  '[Discontinuation Date] as Phoenix_Discontinuation_Date, ' \
                  '[Obsolescence Date] as Phoenix_Obsolescence_Date FROM ' \
                  + data_sheet
        df = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        df['Phoenix_Status'] = 'Y'
        return df

    def import_gtin(self):
        database_file = self.__class__.db_path + 'Master_Data.db'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT [Material code] as Material, Barcode as GTIN FROM GTIN'
        df_gtin = pd.read_sql(con=conn, sql=sql_cmd, index_col='Material')
        df_gtin = df_gtin[~df_gtin.index.duplicated()]
        return df_gtin

    def import_rag_data(self, material_list):
        database_file = self.__class__.db_path + 'Master_Data.db'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT MATNR as Material, REGLICNO, REGAPDATE, REGEXDATE, LIFEYEAR FROM RAG_Report ORDER BY REGAPDATE'
        df_rag = pd.read_sql(con=conn, sql=sql_cmd)
        dict_rag = {}
        for material_item in material_list:
            df_rag_result = df_rag.loc[df_rag['Material'] == material_item,
                                         ['REGLICNO', 'REGAPDATE', 'REGEXDATE', 'LIFEYEAR']]
            list_rag_result = df_rag_result.values.tolist()
            dict_rag_item = {}
            for i in range(len(list_rag_result)):
                dict_element_rag = {}
                for j in range(len(list_rag_result[i])):
                    dict_element_rag["REGLICNO"] = list_rag_result[i][0]
                    dict_element_rag["REGAPDATE"] = list_rag_result[i][1]
                    dict_element_rag["REGEXDATE"] = list_rag_result[i][2]
                    dict_element_rag["LIFEYEAR"] = list_rag_result[i][3]
                dict_rag_item[str(i + 1)] = dict_element_rag
            dict_rag[material_item] = json.dumps(dict_rag_item)
        df_rag_return = pd.DataFrame.from_dict(dict_rag, orient='index', columns=['RAG'])
        return df_rag_return

    def import_pm(self):
        database_file = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        data_sheet = self.__class__.bu_name + '_PM_List'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT Hierarchy_5, PM FROM ' + data_sheet
        df = pd.read_sql(con=conn, sql=sql_cmd)
        return df

    def master_data_update_entrance(self, model='Normal'):
        print("==Start to refresh master data for %s==" % self.__class__.bu_name)
        # read master data
        df_master_data = self.import_material_master(model)
        # get code list
        print('--1. Getting Material Master--')
        code_list = list(df_master_data.index)
        hierarchy_5_list = df_master_data["Hierarchy_5"].unique().tolist()
        # get sap price
        print('--2. Getting SAP Price--')
        df_master_data = df_master_data.join(self.import_sap_price())
        df_master_data.loc[df_master_data['SAP_Price'].isna(), 'SAP_Price'] = 0
        # get ranking
        print('--3. Getting Ranking--')
        df_master_data = df_master_data.join(self.import_abc_ranking())
        df_master_data.loc[df_master_data['Ranking'].isna(), 'Ranking'] = 'C'
        # get ROP setting
        print('--4. Getting MRP Type--')
        df_master_data = df_master_data.join(self.import_rop_setting())
        # get phoenix status
        print('--5. Getting Phoenix Status--')
        df_master_data = df_master_data.join(self.import_phoenix_setting())
        df_master_data.loc[df_master_data['Phoenix_Status'].isna(), 'Phoenix_Status'] = 'N'
        # get GTIN
        print('--6. Getting GTIN--')
        df_master_data = df_master_data.join(self.import_gtin())
        # get RAG
        print('--7. Getting RAG--')
        df_master_data = df_master_data.join(self.import_rag_data(code_list))
        # get PM
        print('--8. Getting PM List--')
        pm_list = self.import_pm().values.tolist()
        for item in pm_list:
            df_master_data.loc[df_master_data['Hierarchy_5'] == item[0], 'PM'] = item[1]
        # re-arrange pm list for instrument
        df_master_data = df_master_data.reset_index()
        df_master_data.rename(columns={"index": "Material"}, inplace=True)
        # test judgement of implant and instrument
        # df_master_data['Product_Type'] = 'Instrument'
        # df_master_data.loc[df_master_data['Material'].str.slice(stop=1).isin(['2', '4', '7']), 'Product_Type'] = 'Implant'
        # df_master_data.loc[
        #     df_master_data['Material'].str.slice(stop=2).isin(['02', '04', '07']), 'Product_Type'] = 'Implant'
        # df_master_data.loc[df_master_data['Material'].str.slice(stop=3) == 'CNB', 'Product_Type'] = 'Implant'
        df_master_data.loc[
            (~df_master_data['Material'].str.slice(stop=1).isin(['2', '4', '7'])) &
            (~df_master_data['Material'].str.slice(stop=2).isin(['02', '04', '07'])) &
            (df_master_data['Material'].str.slice(stop=3) != 'CNB'), 'PM'] = 'Instrument'
        # update implant/instrument
        df_master_data['Instrument'] = 'N'
        df_master_data.loc[df_master_data['PM'] == 'Instrument', 'Instrument'] = 'Y'
        # write to database
        self.finalize_master_data(df_master_data, model)

    def finalize_master_data(self, df, model):
        database_file = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        if model == 'Normal':
            data_sheet = self.__class__.bu_name + '_Master_Data'
        else:
            data_sheet = self.__class__.bu_name + '_Master_Data_Demo'
        conn = sqlite3.connect(database_file)
        df.to_sql(data_sheet, con=conn, index=False, if_exists='replace')
        print('--Done--')


class MasterDataUpdate:
    bu_name = ''
    file_path = "../data/_Source_Data/"
    update_path = "../data/_Update/"
    db_path = "../data/_DB/"

    def __init__(self, bu_name_input):
        self.__class__.bu_name = bu_name_input

    # import BU base master data
    def import_master_data(self):
        # for TU. data_type = {"Master_Data", "SAP_Price", "Phoenix_List"}
        print("==Import Master Data for %s==" % self.__class__.bu_name)
        print("Please Choose Master Data Type (1 - PM_List, 2 - SAP_Price, 3 - Phoenix_List, 4 - ROP_Setting, "
              "5 - ABC Ranking, 6 - NPI List)")
        cmd_code = input("cmd >> master_data >> ")
        if cmd_code == "1":
            data_type = "PM_List"
        elif cmd_code == "2":
            self.import_sap_price()
            return
        elif cmd_code == "3":
            data_type = "Phoenix_List"
        elif cmd_code == "4":
            data_type = "ROP_Setting"
        elif cmd_code == '5':
            self.generate_abc_ranking()
            print('ABC Ranking Template Done.~')
            return
        elif cmd_code == '6':
            data_type = 'NPI_List'
        else:
            print("!!Wrong code, please try again!")
            return
        file_name = self.__class__.bu_name + "_" + data_type
        file_fullname = self.__class__.file_path + file_name + ".xlsx"
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        print("~ Start to read the data file %s" % file_name)
        start_time = datetime.now()
        if data_type == "ROP_Setting":
            df = pd.read_excel(file_fullname, na_values="0", dtype={'Reorder Point': np.int32})
        else:
            df = pd.read_excel(file_fullname, na_values="0")
        # data = df.values
        stop_time = datetime.now()
        print("~ File reading complete with time of %s seconds" % (stop_time-start_time).seconds)
        # 写入数据库
        conn = sqlite3.connect(db_fullname)
        df.to_sql(name=file_name, con=conn, if_exists='replace', index=False)
        print("%s is imported" % data_type)

    # import SAP_Price in separate txt format
    def import_sap_price(self):
        str_directory = self.file_path + 'TU_SAP_Price/'
        table_name = self.bu_name + '_SAP_Price'
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        lst_file = os.listdir(str_directory)
        for filename in lst_file:
            df = pd.read_csv(str_directory + filename, skiprows=5, skipfooter=1, sep='|', skipinitialspace=True,
                             header=None, thousands=',', encoding='latin1')
            column_list = df.columns.values.tolist()
            df.drop(columns=[column_list[0], column_list[-1]], inplace=True)
            df_total_price = df.copy() if lst_file.index(filename) == 0 else pd.concat([df_total_price, df])
        df_total_price.columns = ['CnTy', 'DChl', 'Material', 'Description', 'Price', 'Unit', 'per', 'UoM',
                                  'Valid From', 'Valid to']
        df_total_price['Material'] = df_total_price['Material'].str.strip()
        conn = sqlite3.connect(db_fullname)
        df_total_price.to_sql(name=table_name, con=conn, if_exists='replace', index=False)
        print("SAP_Price is imported")

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
        if cmd_code == '3':
            df = pd.read_excel(master_data_file,  dtype={'Barcode': str})
            # print(df.info())
        elif cmd_code == "2":
            df = pd.read_excel(master_data_file, dtype={'REGAPDATE': str, 'REGEXDATE': str},
                               skiprows=[1, ])
        else:
            df = pd.read_excel(master_data_file)
        print("Start to import into database.")
        database_name = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_name)
        df.to_sql(name=master_data_filename, con=conn, if_exists='replace', index=False)
        print("%s imported" % master_data_filename)

    # ranking ABC by 6 month IMS sales value.
    def generate_abc_ranking(self, sales_source="IMS", month_qty=6):
        tbl_name = self.__class__.bu_name + "_" + sales_source
        db_fullname = self.__class__.db_path + tbl_name + ".db"
        master_data_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get month list
        str_cmd = "SELECT DISTINCT month from " + tbl_name + " ORDER BY month DESC LIMIT " + str(month_qty)
        c.execute(str_cmd)
        result = c.fetchall()
        month_list = ""
        for item in result:
            month_list = month_list + '\"' + item[0] + '\",'
        month_list = month_list.rstrip(",")
        # get recent month IMS
        str_cmd = "SELECT Material, sum(Quantity) as IMS_Quantity,  sum(Value_SAP_Price) as IMS_Value from " + \
                  tbl_name + " WHERE Month in (" + month_list + ") GROUP by Material ORDER by IMS_Value DESC"
        df_ims_query = pd.read_sql(sql=str_cmd, con=conn, index_col='Material')
        # get accumulate IMS data and ranking
        ims_total = df_ims_query['IMS_Value'].sum()
        df_ims_query['Ratio'] = df_ims_query['IMS_Value'] / ims_total
        df_ims_query['Cum_Ratio'] = df_ims_query['Ratio'].cumsum()
        df_ims_query['Ranking'] = df_ims_query['Cum_Ratio'].apply(lambda x: 'A' if x < 0.8 else ('B' if x < 0.95 else 'C'))
        # get phoenix list
        df_phoenix_list = self.get_phoenix_products_list()
        df_ims_query = df_ims_query.join(df_phoenix_list)
        # change all phoenix products to Ranking C
        df_ims_query.loc[~df_ims_query['Target SKU'].isnull(), 'Ranking'] = 'C'
        # delete calculation column
        df_ims_query.drop(['Ratio', 'Cum_Ratio', 'Target SKU'], axis=1, inplace=True)
        conn = sqlite3.connect(master_data_db_fullname)
        df_ims_query.to_sql(name="Ranking", con=conn, if_exists='replace')
        print('Ranking updated')
        conn.close()

    # get phoenix products list
    def get_phoenix_products_list(self):
        database_file = self.__class__.db_path + self.bu_name + "_Master_Data.db"
        data_sheet = self.bu_name + '_Phoenix_List'
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT [Exit SKU], [Target SKU] FROM ' + data_sheet
        df_phoenix_list = pd.read_sql(sql=sql_cmd, con=conn, index_col='Exit SKU')
        return df_phoenix_list


if __name__ == "__main__":
    DataUpdate = MasterDataUpdate('TU')
    DataUpdate.import_sap_price()
    # DataUpdate.master_data_update_entrance()
    # print(DataUpdate.mapping_rag(["440.834", "440.831S"]))
    # dataupdate = MonthlyUpdate('TU')
    # dataupdate.update_lp_inv()
