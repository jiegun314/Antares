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
from alive_progress import alive_bar


class MonthlyUpdate:
    bu_name = ""
    update_path = "../data/_Update/"
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

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

    def update_jnj_inventory(self):
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


class MasterDataConsolidation:
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
        sql_cmd = 'SELECT MATNR as Material, REGLICNO, REGAPDATE, REGEXDATE, LIFEYEAR FROM RAG_Report ' \
                  'ORDER BY REGAPDATE'
        df_rag = pd.read_sql(con=conn, sql=sql_cmd)
        dict_rag = {}
        with alive_bar(len(material_list), bar='blocks') as bar:
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
                bar()
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

    # import bu level master data
    def import_bu_master_data(self, data_type):
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
        print("~ File reading complete with time of %s seconds" % (stop_time - start_time).seconds)
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

    def import_public_master_data(self, master_data_filename):
        master_data_path = self.__class__.update_path + "Public/"
        master_data_file = master_data_path + master_data_filename + ".xlsx"
        print("!Make sure you have put file %s in %s" % (master_data_filename, master_data_path))
        # start to read file
        print("Start to read data file.")
        if master_data_filename == 'GTIN':
            df = pd.read_excel(master_data_file,  dtype={'Barcode': str})
            # print(df.info())
        elif master_data_filename == "RAG_Report":
            df = pd.read_excel(master_data_file, dtype={'REGAPDATE': str, 'REGEXDATE': str}, skiprows=[1, ])
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

    # generate new Trauma ranking by considering LPSales and GTS
    def generate_tu_abc_ranking(self, month_qty=12):
        master_data_db_fullname = self.__class__.db_path + self.__class__.bu_name + '_Master_Data.db'
        # get IMS, LPSales, GTS result
        df_ims = self._generate_historical_sales('IMS', 'Value_SAP_Price', month_qty)
        df_lpsales = self._generate_historical_sales('LPSales', 'Quantity', month_qty)
        df_gts = self._generate_historical_sales('GTS', 'Quantity', month_qty)
        # get and combine quantity
        df_ims_qty = self._generate_historical_sales('IMS', 'Quantity', month_qty)
        df_ims = df_ims.join(df_ims_qty)
        # ranking in IMS
        # get accumulate IMS data and ranking
        ims_total = df_ims['IMS_Value_SAP_Price'].sum()
        df_ims['Ratio'] = df_ims['IMS_Value_SAP_Price'] / ims_total
        df_ims['Cum_Ratio'] = df_ims['Ratio'].cumsum()
        df_ims['Ranking'] = df_ims['Cum_Ratio'].apply(lambda x: 'A' if x < 0.8 else ('B' if x < 0.95 else 'C'))
        # mapping with GTS and lpsales
        df_ims = df_ims.join(df_lpsales)
        df_ims = df_ims.join(df_gts)
        df_ims.fillna(0, inplace=True)
        df_ims['GTS_and_LPSales'] = df_ims['GTS_Quantity'] + df_ims['LPSales_Quantity']
        # set ranking C and sum(IMS, GTS, LPSales) = 0  to rank D
        df_ims.loc[(df_ims['IMS_Value_SAP_Price'] == 0) & (df_ims['GTS_and_LPSales'] == 0), 'Ranking'] = 'D'
        # set ranking C and sum(GTS, LPSales) > 3 to rank B. Currently not used
        # df_ims.loc[(df_ims['Ranking'] == 'C') & ((df_ims['GTS_Quantity'] > 3) | (df_ims['GTS_and_LPSales'] > 3)),
        #            'Ranking'] = 'New_B'
        # get phoenix list
        df_phoenix_list = self.get_phoenix_products_list()
        df_ims = df_ims.join(df_phoenix_list)
        # change all phoenix products to Ranking D
        df_ims.loc[~df_ims['Target SKU'].isnull(), 'Ranking'] = 'D'
        # get the result
        df_ims.reset_index(inplace=True)
        df_ranking_result = df_ims[['Material', 'IMS_Quantity', 'IMS_Value_SAP_Price', 'Ranking']]
        # write back to database
        conn = sqlite3.connect(master_data_db_fullname)
        df_ranking_result.to_sql(name="Ranking", con=conn, if_exists='replace', index=False)
        print('Ranking updated')

    # a internal function to get sales summary result
    # sales_type: GTS, LPSales, IMS
    # value_type: Quantity, Value_Standard_Cost, Value_SAP_Price
    # month_qty: int > 0
    def _generate_historical_sales(self, sales_type, value_type, month_qty) -> pd.DataFrame:
        item_name = '%s_%s' % (sales_type, value_type)
        table_name = '%s_%s' % (self.__class__.bu_name, sales_type)
        database_fullname = '%s%s.db' % (self.__class__.db_path, table_name)
        conn = sqlite3.connect(database_fullname)
        c = conn.cursor()
        sql_cmd = 'SELECT DISTINCT month FROM %s ORDER BY month DESC LIMIT %s' % (table_name, str(month_qty))
        c.execute(sql_cmd)
        result = c.fetchall()
        lst_month = [item[0] for item in result]
        # change the month list to string of scope
        str_month_list = '\"' + '\",\"'.join(lst_month) + '\"'
        # get the sales data
        sql_cmd = 'SELECT Material, sum(%s) as %s FROM %s WHERE Month in (%s) GROUP by Material ' \
                  'ORDER by %s DESC' % (value_type, item_name, table_name, str_month_list, item_name)
        df_inv = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        return df_inv

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
    DataUpdate.generate_tu_abc_ranking()
    # DataUpdate.master_data_update_entrance()
    # print(DataUpdate.mapping_rag(["440.834", "440.831S"]))
    # dataupdate = MonthlyUpdate('TU')
    # dataupdate.update_lp_inv()
