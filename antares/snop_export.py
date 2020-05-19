# 该模块用于导出生成SNOP所需要的excel文件，包含所有相关信息

import sqlite3
import pandas as pd
import calculation
import numpy as np
import data_import
import time


class SNOPExport:
    bu_name = ""
    db_path = "../data/_DB/"
    export_path = "../data/_Output/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # 获取销量，包括数量和两个金额
    def get_code_sales_full_list(self, data_type):
        file_name = self.__class__.bu_name + "_" + data_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        str_cmd = "SELECT material, month, SUM(quantity), SUM(Value_Standard_Cost), SUM(Value_SAP_Price) from " + \
                  tbl_name + " GROUP BY material, month ORDER BY month"
        result = c.execute(str_cmd).fetchall()
        conn.close()
        return result

    # 获取库存量，包括数量和两个金额
    def get_code_inv_full_list(self, data_type):
        # 文件名，无后缀
        file_name = self.__class__.bu_name + "_" + data_type
        # 数据库完整路径加名称
        db_fullname = self.__class__.db_path + file_name + ".db"
        # 表格名称，等于文件名称
        tbl_name = file_name
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        if data_type == "JNJ_INV":
            str_cmd = "SELECT material, month, SUM(Available_Stock), SUM(Value_Standard_Cost), SUM(Value_SAP_Price) " \
                      "from " + tbl_name + " GROUP BY material, month ORDER BY month"
        else:
            str_cmd = "SELECT material, month, SUM(quantity), SUM(Value_Standard_Cost), SUM(Value_SAP_Price) from " \
                      + tbl_name + " GROUP BY material, month ORDER BY month"
        result = c.execute(str_cmd).fetchall()
        conn.commit()
        conn.close()
        return result

    # 获取代码对应的销量信息（按照月份排列）
    def get_list_data(self, code, list_data, start_month):
        sales_qty = []
        sales_standard_cost = []
        sales_sap_price = []
        for sales_item in list_data:
            if sales_item[0] == code:
                sales_qty.append((sales_item[1], sales_item[2]))
                sales_standard_cost.append((sales_item[1], sales_item[3]))
                sales_sap_price.append((sales_item[1], sales_item[4]))
        check_info = calculation.InfoCheck(self.__class__.bu_name)
        sales_qty_result = check_info.data_mapping(sales_qty, start_month, -24)
        sales_value_standard_cost = check_info.data_mapping(sales_standard_cost, start_month, -24)
        sales_value_sap_price = check_info.data_mapping(sales_sap_price, start_month, -24)
        sales_result = sales_qty_result.copy()
        sales_result.extend(sales_value_standard_cost)
        sales_result.extend(sales_value_sap_price)
        return sales_result

    # get eso quantity by code
    def get_code_eso_quantity(self, code):
        eso_cycle_month = self.get_recent_eso_cycle_month()
        eso_result = []
        filename = self.__class__.bu_name + "_ESO"
        db_fullname = self.__class__.db_path + filename + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        for cycle_month in eso_cycle_month:
            sql_cmd = "SELECT ESO_Quantity, ESO_Value_Standard_Cost, ESO_Value_SAP_Price FROM " \
                      + filename + " WHERE Material = \'" + code + "\' AND Month = \'" + cycle_month + "\'"
            c.execute(sql_cmd)
            result = c.fetchone()
            if result is None:
                eso_result.extend([0, 0, 0])
            else:
                eso_result.extend(result)
        conn.commit()
        conn.close()
        return eso_result

    # get forecast full list
    def get_forecast_fulllist(self, fcst_type):
        db_name = self.__class__.bu_name + "_" + fcst_type + "_Forecast.db"
        full_db_name = self.__class__.db_path + db_name
        current_month = time.strftime("%Y%m", time.localtime())
        tbl_name = self.__class__.bu_name + "_" + fcst_type + "_Forecast_" + current_month
        conn = sqlite3.connect(full_db_name)
        c = conn.cursor()
        c.execute('SELECT * from ' + tbl_name)
        result = c.fetchall()
        return result

    # get forecast list by code
    def get_forecast_list(self, code, fcst_type):
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        lst_fcst_quantity = list(map(int, infocheck.get_code_forecast(code, fcst_type, 24)[1]))
        code_master_data = infocheck.get_master_data(code)
        std_cost, sap_price = code_master_data[10], code_master_data[11]
        if std_cost is None:
            std_cost = 0
        if sap_price is None:
            sap_price = 0
        lst_fcst_std_cost = [item * std_cost for item in lst_fcst_quantity]
        lst_fcst_sap_price = [item * sap_price for item in lst_fcst_quantity]
        return lst_fcst_quantity + lst_fcst_sap_price

    # Get most recent tow ESO cycle month
    def get_recent_eso_cycle_month(self):
        eso_filename = self.__class__.bu_name + "_ESO"
        eso_db_fullname = self.__class__.db_path + eso_filename + ".db"
        conn = sqlite3.connect(eso_db_fullname)
        c = conn.cursor()
        c.execute("SELECT DISTINCT Month FROM " + eso_filename + " ORDER by Month DESC LIMIT 2")
        result = c.fetchall()
        conn.commit()
        conn.close()
        return [row[0] for row in result]

    # 生成表格的表头
    def generate_index(self):
        list_index = []
        # 获取material master的index
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        c.execute("PRAGMA  table_info (\"TU_Master_Data\")")
        result = c.fetchall()
        list_mm_index = []
        for item in result:
            list_mm_index.append(item[1])
        list_index.extend(list_mm_index)
        # get ESO month of recent 2 ESO cycle
        lst_eso_title = ["ESO_Quantity", "ESO_Value_Standard_Cost", "ESO_Value_SAP_Price"]
        recent_cycle_month = self.get_recent_eso_cycle_month()
        for item in recent_cycle_month:
            for eso_title_item in lst_eso_title:
                list_index.append(eso_title_item + "_" + item)
        # 获取月份列表
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = calculation.InfoCheck(self.__class__.bu_name)
        month_list = info_check.get_time_list(current_month, -24)
        fcst_month_list = info_check.get_time_list(current_month, 24)
        # 生成两个命名列表
        value_type = ["GTS", "LPSales", "IMS", "JNJ_INV", "LP_INV"]
        price_type = ["Quantity", "Standard_Cost", "SAP_Price"]
        # fcst_type = ["Statistical_Forecast", "Final_Forecast"]
        fcst_type = ["Final_Forecast", ]
        fcst_unit = ["Quantity", "SAP_Price"]
        for value_item in value_type:
            for price_item in price_type:
                for month_item in month_list:
                    str_title = value_item + "_" + price_item + "_" + month_item
                    list_index.append(str_title)
        # Generate forecast list column title
        for fcst_item in fcst_type:
            for fcst_unit_item in fcst_unit:
                for fcst_month_item in fcst_month_list:
                    list_index.append(fcst_item + "_" + fcst_unit_item + "_" + fcst_month_item)
        return list_index

    # 获取代码对应的MM信息
    def mapping_master_data(self, code, list_data):
        list_master_data = []
        for item in list_data:
            if item[0] == code:
                list_master_data = list(item).copy()
        return list_master_data

    # Entrance of SNOP file export
    def snop_export_entrance(self):
        # 获取当前月份
        current_month = time.strftime("%Y-%m", time.localtime())
        # 读取active code列表
        print("==== <Start to generate SNOP report> ====")
        get_code_list = data_import.DataInput(self.__class__.bu_name)
        active_code_list = get_code_list.get_active_codes()
        print("=== <Get Active Code List - Done > ===")
        print("=== <Get Master Data, Sales & INV Data - Start > ===")
        # 实例化计算模块
        code_calculation = calculation.InfoCheck(self.__class__.bu_name)
        # 获取master data, 销量，以及库存的数据表格
        list_master_data = code_calculation.get_master_data_list()
        list_gts_data = self.get_code_sales_full_list("GTS")
        list_lpsales_data = self.get_code_sales_full_list("LPSales")
        list_ims_data = self.get_code_sales_full_list("IMS")
        list_jnj_inv = self.get_code_inv_full_list("JNJ_INV")
        list_lp_inv = self.get_code_inv_full_list('LP_INV')
        list_statis_fcst = self.get_forecast_fulllist("Statistical")
        list_final_fcst = self.get_forecast_fulllist("Final")
        print("=== <Get Master Data, Sales & INV Data - Done > ===")
        print("=== <Generate Standard List - Start > ===")
        # 进度条显示 - 计数变量
        counter = 0
        list_length = len(active_code_list)
        list_show = []
        gap_show = int(list_length / 20)
        for i in range(1, 21):
            list_show.append(i * gap_show)
        num = 5
        # Add column title
        data_result = [self.generate_index()]
        for code_item in active_code_list:
            code_result = []
            # 载入 Material Master
            code_result.extend(self.mapping_master_data(code_item, list_master_data))
            # import 2 cycle of ESO result
            code_result.extend(self.get_code_eso_quantity(code_item))
            # 获取销量
            code_result.extend(
                self.get_list_data(code_item, list_gts_data, current_month))
            code_result.extend(
                self.get_list_data(code_item, list_lpsales_data, current_month))
            code_result.extend(
                self.get_list_data(code_item, list_ims_data, current_month))
            # 获取库存量
            code_result.extend(
                self.get_list_data(code_item, list_jnj_inv, current_month))
            code_result.extend(
                self.get_list_data(code_item, list_lp_inv, current_month))
            # 获得Forecast
            # code_result.extend(self.get_forecast_list(code_item, "Statistical"))
            code_result.extend(self.get_forecast_list(code_item, "Final"))
            # if len(code_result) != 455:
            #     print(code_item)
            data_result.append(code_result)
            # 显示计数
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        print("\n")
        print("=== <Generate Standard List - Done > ===")
        print("=== <Generate Excel File - Start > ===")
        # 写入数组
        np_snop_data = np.array(data_result)
        # 导入dataframe
        df = pd.DataFrame(data=np_snop_data[1:, 1:], columns=np_snop_data[0, 1:], index=np_snop_data[1:, 0])
        # 导出到excel
        current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_" + current_time + ".xlsx"
        file_fullname = self.__class__.export_path + file_name
        df.to_excel(file_fullname, sheet_name="Code", index_label="Material")
        print("== <SNOP File is Ready!> ==")

    # test function
    def test(self):
        get_code_list = data_import.DataInput(self.__class__.bu_name)
        active_code_list = get_code_list.get_active_codes()
        lst_result = []
        for code in active_code_list:
            lst_result.extend(self.get_code_eso_quantity(code))
        print(len(lst_result))
        pass

    def get_top_sales(self, sales_type, num=20):
        # get this cycle month and last cycle month
        current_month = time.strftime("%Y-%m", time.localtime())
        info_check = calculation.InfoCheck(self.__class__.bu_name)
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
        info_check = calculation.InfoCheck(self.__class__.bu_name)
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
        info_check = calculation.InfoCheck(self.__class__.bu_name)
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
            c.execute(sql_cmd)
            inv_phoenix = c.fetchall()[0]
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
        current_time = time.strftime("%y%m%d", time.localtime())
        file_name = self.__class__.bu_name + "_SNOP_TEST_" + current_time + ".xlsx"
        file_fullname = self.__class__.export_path + file_name
        writer = pd.ExcelWriter(file_fullname)

        # export 6 months JNJ inventory
        six_month_jnj_inv = self.get_monthly_inventory_list("JNJ_INV", 6)
        np_jnj_monthly_inv = np.array(six_month_jnj_inv)
        df_jnj_monthly_inv = pd.DataFrame(data=np_jnj_monthly_inv[1:, 0:], columns=np_jnj_monthly_inv[0, 0:])
        df_jnj_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=1)

        # export 6 months LP inventory
        six_month_lp_inv = self.get_monthly_inventory_list("LP_INV", 6)
        np_lp_monthly_inv = np.array(six_month_lp_inv)
        df_lp_monthly_inv = pd.DataFrame(data=np_lp_monthly_inv[1:, 0:], columns=np_lp_monthly_inv[0, 0:])
        df_lp_monthly_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=6, startcol=1)

        # export top 20 gts products
        top_gts_list = self.get_top_sales("GTS")
        np_top_gts = np.array(top_gts_list)
        df_top_gts = pd.DataFrame(data=np_top_gts[1:, 0:], columns=np_top_gts[0, 0:])
        # export gts, start from
        df_top_gts.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=10)

        # export top 20 inv products
        top_jnj_inv_list = self.get_top_inv("JNJ_INV")
        np_top_jnj_inv = np.array(top_jnj_inv_list)
        df_top_jnj_inv = pd.DataFrame(data=np_top_jnj_inv[1:, 0:], columns=np_top_jnj_inv[0, 0:])
        # export inv to excel
        df_top_jnj_inv.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=16)

        # export top 20 eso - Instrument
        top_instrument_eso_list = self.get_top_eso("Instrument")
        np_top_instrument_eso = np.array(top_instrument_eso_list)
        df_top_instrument_eso = pd.DataFrame(data=np_top_instrument_eso[1:, 0:], columns=np_top_instrument_eso[0, 0:])
        # export instrument eso to excel
        df_top_instrument_eso.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=22)

        # export top 20 eso - Implant
        top_implant_eso_list = self.get_top_eso("Implant")
        np_top_implant_eso = np.array(top_implant_eso_list)
        df_top_implant_eso = pd.DataFrame(data=np_top_implant_eso[1:, 0:], columns=np_top_implant_eso[0, 0:])
        # export instrument eso to excel
        df_top_implant_eso.to_excel(writer, sheet_name="SNOP_Summary", index=False, startrow=1, startcol=28)

        writer.close()


if __name__ == '__main__':
    export_test = SNOPExport("TU")
    export_test.snop_summary_generation()
    # export_test.snop_export_entrance()
    # export_test.get_forecast_fulllist("Final")

