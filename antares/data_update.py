# import os, sys
import json
import sqlite3
import pandas as pd
import calculation as cclt
import time
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
        # 29 个元素
        file_name = self.__class__.bu_name + "_ESO"
        file_fullname = self.__class__.update_path + "Update_" + file_name + ".xlsx"
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
        print("ESO File is updated")
        pass

    # import final forecast
    def update_final_forecast(self):
        print("==Final Forecast Import==")
        file_name = self.__class__.bu_name + "_Forecast"
        file_fullname = self.__class__.update_path + "Update_" + file_name + ".xlsx"
        print("Warning - Make sure you've put file %s under update folder." % file_name)
        if input("Ready to proceed? (Y/N): ").upper() != 'Y':
            return
        print("Start to read forecast file")
        df_forecast = pd.read_excel(file_fullname).fillna(0)
        # get month list
        month_list = np.delete(df_forecast.columns.values, 0, 0).tolist()
        month_length = len(month_list)
        # get code list
        code_list = df_forecast['Code'].values.tolist()
        # get hierarchy name and sap_price
        infocheck = cclt.InfoCheck(self.__class__.bu_name)
        print("Start to map Hierarchy_5 data")
        hierarchy_5_list = infocheck.get_master_data_for_list(code_list, "Hierarchy_5")
        print("Start to map SAP_Price data")
        sap_price_list = infocheck.get_master_data_for_list(code_list, "SAP_Price")
        print("Start to generate list")
        # merge back to dataframe
        df_forecast.insert(1, "Hierarchy_5", hierarchy_5_list)
        df_forecast.insert(2, "SAP_Price", sap_price_list)
        # merge sap value
        print("Start to generate forecast in value format")
        # print(df_forecast.head())
        for index in range(0, len(month_list)):
            column_name = 'Value_' + month_list[index]
            df_forecast[column_name] = df_forecast.apply(lambda x: x[month_list[index]] * x['SAP_Price'], axis=1)
        print("Convert to import list")
        list_forecast_raw = df_forecast.values.tolist()
        forecast_to_upload = []
        for forecast_item in list_forecast_raw:
            index = 0
            for month_item in month_list:
                # insert code and hierarchy_5
                forecast_single_line = forecast_item[0:2]
                # insert month
                forecast_single_line.append(month_item)
                # insert forecast quantity
                forecast_single_line.append(forecast_item[index + 3])
                # insert forecast value
                forecast_single_line.append(forecast_item[index + 3 + month_length])
                # insert single line for one code in one month
                forecast_to_upload.append(forecast_single_line)
                index += 1
        # change to dataframe for upload
        df_forecast_upload = pd.DataFrame(forecast_to_upload,
                                          columns=["Material", "Hierarchy_5", "Month", "Quantity", "Value_SAP_Price"])
        # df_forecast_upload.to_excel(self.__class__.update_path + "forecast.xlsx")
        # write to final forecast
        print("Update to database as final forecast")
        tbl_final_fcst = self.__class__.bu_name + "_Final_Forecast"
        db_final_fcst_fullname = self.__class__.db_path + tbl_final_fcst + ".db"
        tbl_name = tbl_final_fcst + "_" + time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(db_final_fcst_fullname)
        df_forecast_upload.to_sql(tbl_name, conn, index=False, if_exists='replace')
        conn.commit()
        conn.close()
        print("Final forecast updated!~")

    def data_update_entrance(self, cmd):
        if cmd == "901":
            self.update_sales("GTS")
        elif cmd == "902":
            self.update_sales("LPSales")
        elif cmd == "903":
            self.update_sales("IMS")
        elif cmd == '905':
            self.update_jnj_inv()
        elif cmd == "906":
            self.update_lp_inv()
        elif cmd == "908":
            self.update_final_forecast()
        elif cmd == "909":
            self.update_eso()
        else:
            print("!!Error: wrong user name, please restart the program.")


class MasterDataUpdate:
    db_path = "../data/_DB/"

    def __init__(self):
        pass

    @property
    def bu_name(self):
        return self._bu_name

    @bu_name.setter
    def bu_name(self, value):
        self._bu_name = value

    def master_data_update_entrance(self):
        print("==Start to refresh master data for %s==" % self._bu_name)
        # read master data
        df_master_data = self.import_material_master()
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
        # write back to database
        # print(df_master_data.head())
        self.finalize_master_data(df_master_data)

    def finalize_master_data(self, df):
        database_file = self.__class__.db_path + self._bu_name + "_Master_Data.db"
        data_sheet = self._bu_name + '_Master_Data'
        conn = sqlite3.connect(database_file)
        df.to_sql(data_sheet, con=conn, index=False, if_exists='replace')
        # from sqlalchemy import create_engine
        # engine = create_engine('sqlite:///' + self._bu_name + '_Master_Data_Demo')
        # data_sheet = self._bu_name + '_Master_Data_Demo'
        # df.to_sql(data_sheet, con=engine, index=False, if_exists='replace')
        print('--Done--')

    def import_material_master(self):
        database_file = self.__class__.db_path + "Master_Data.db"
        conn = sqlite3.connect(database_file)
        sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self._bu_name + '\"'
        # sql_cmd = 'SELECT * FROM MATERIAL_MASTER WHERE Business_Unit = \"' + self._bu_name + '\" LIMIT 100'
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
                lst_pm.append(None)
        return lst_pm


if __name__ == "__main__":
    DataUpdate = MasterDataUpdate()
    DataUpdate.bu_name = "TU"
    DataUpdate.master_data_update_entrance()
    # print(DataUpdate.mapping_rag(["440.834", "440.831S"]))
    # dataupdate = MonthlyUpdate('TU')
    # dataupdate.update_lp_inv()
