# This file is used to proceed marketing intelligent
import json
import sqlite3
import numpy as np
import time
from tabulate import tabulate
import public_function as pb_func
import calculation as cclt


class MI:
    bu_name = ""
    db_path = "../data/_DB/"
    bp_file = "../data/_Source_Data/DPS_Setting.json"
    source_path = "../data/_Source_Data/MI/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # Read json file to get gts bp
    def get_bp(self):
        with open(self.__class__.bp_file) as f:
            data = json.load(f)
        dict_bp = data[self.__class__.bu_name]["BP"]
        lst_bp = [[item["Month"] for item in dict_bp], [item["Value"] for item in dict_bp]]
        return lst_bp

    # read sales of one BU
    def get_bu_sales(self, month_list, sales_type, price_type):
        sales_result = []
        file_name = self.__class__.bu_name + "_" + sales_type
        db_fullname = self.__class__.db_path + file_name + ".db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        for month_item in month_list:
            if price_type == "Standard_Cost":
                sql_cmd = "SELECT month, sum(Value_Standard_Cost) from " + file_name + " WHERE Month = \'" + \
                          month_item + "\' GROUP BY month"
            else:
                sql_cmd = "SELECT month, sum(Value_SAP_Price) from " + file_name + " WHERE Month = \'" + \
                          month_item + "\' GROUP BY month"
            c.execute(sql_cmd)
            sales_result.append(c.fetchall()[0])
        conn.commit()
        conn.close()
        return sales_result

    # read forecast with values
    def get_forecast(self, fcst_type, month_list, cclt_type, name="TU"):
        if fcst_type == "Statistical":
            db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast.db"
        else:
            db_fullname = self.__class__.db_path + self.__class__.bu_name + "_Final_Forecast.db"
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        # get newest forecast
        c.execute("SELECT name from sqlite_master where type = \"table\" ORDER by name DESC")
        tbl_name = c.fetchone()[0]
        lst_result = []
        # get volume list
        for month_item in month_list:
            if cclt_type == "by_code":
                sql_cmd = "SELECT Quantity, Value_SAP_Price from " + tbl_name + " WHERE Material = \'" + name + \
                          "\' AND Month = \'" + month_item + "\'"
            elif cclt_type == "by_h5":
                sql_cmd = "SELECT sum(Quantity), sum(Value_SAP_Price) from " + tbl_name + \
                          " WHERE Hierarchy_5 = \'" + name + "\' AND Month = \'" + month_item + "\'"
            else:
                sql_cmd = "SELECT sum(Quantity), sum(Value_SAP_Price) from " + tbl_name + \
                          " WHERE Month = \'" + month_item + "\'"
            try:
                c.execute(sql_cmd)
                result = c.fetchall()[0]
            except IndexError:
                result = (0, 0)
            lst_result.append([month_item] + list(result))
        return lst_result

    # generate passed month and new month list in current year
    def get_month_list(self):
        current_year = int(time.strftime("%Y", time.localtime()))
        current_month = int(time.strftime("%m", time.localtime()))
        old_month_list = np.arange(1, current_month, 1)
        new_month_list = np.arange(current_month, 13, 1)

        passed_month_list = []
        for month_item in old_month_list:
            t = (current_year, month_item, 17, 17, 3, 38, 1, 48, 0)
            secs = time.mktime(t)
            time_1 = time.strftime("%Y-%m", time.localtime(secs))
            passed_month_list.append(time_1)

        forecast_month_list = []
        for month_item in new_month_list:
            t = (current_year, month_item, 17, 17, 3, 38, 1, 48, 0)
            secs = time.mktime(t)
            time_1 = time.strftime("%Y-%m", time.localtime(secs))
            forecast_month_list.append(time_1)
        return passed_month_list, forecast_month_list

    # get bp_dp alignment by bu
    def get_bpdp_alignment(self):
        print("BP/DP Alignment for %s" % self.__class__.bu_name)
        passed_month_list, forecast_month_list = self.get_month_list()
        # read sales data
        gts_value = self.get_bu_sales(passed_month_list, "GTS", "SAP_Price")
        # read forecast data
        final_forecast_sap_price = self.get_forecast("Final", forecast_month_list, "by_BU")
        statis_forecast_sap_price = self.get_forecast("Statistical", forecast_month_list, "by_BU")
        final_dp_value = [int(item[1]) for item in gts_value] + [item[2] for item in final_forecast_sap_price]
        statis_dp_value = [int(item[1]) for item in gts_value] + [item[2] for item in statis_forecast_sap_price]
        # get bp data
        month_list, bp_value = self.get_bp()
        # Get sum
        statis_dp_value.append(sum(statis_dp_value))
        final_dp_value.append(sum(final_dp_value))
        bp_value.append(sum(bp_value))
        # Add ratio
        index = 0
        statis_ratio, final_ratio = [], []
        while index < len(final_dp_value):
            final_ratio_temp = final_dp_value[index] / bp_value[index]
            statis_ratio_temp = statis_dp_value[index] / bp_value[index]
            final_ratio.append(str('{:.1%}'.format(final_ratio_temp)))
            statis_ratio.append(str('{:.1%}'.format(statis_ratio_temp)))
            index += 1
        # Add title
        month_list = ["Month"] + month_list + ["Summary"]
        bp_value = ["BP"] + bp_value
        statis_dp_value = ["Actual/Statis. DP"] + statis_dp_value
        statis_ratio = ["Ratio"] + statis_ratio
        final_dp_value = ["Actual/Final DP"] + final_dp_value
        final_ratio = ["Ratio"] + final_ratio

        final_list = [month_list, bp_value, statis_dp_value, statis_ratio, final_dp_value, final_ratio]
        print(tabulate(final_list, tablefmt="psql", headers="firstrow", floatfmt=",.0f"))
        pass

    # check MI file availability
    def check_mi_file(self):
        db_fullname = self.__class__.db_path + self.__class__.bu_name + "_MI.db"
        filename = self.__class__.bu_name + "_MI_" + time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(db_fullname)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master where type = \'table\'")
        result = [item[0] for item in c.fetchall()]
        # if current month does not exist
        if filename not in result:
            c.execute('''CREATE TABLE ''' + filename + '''
                    (Material TEXT NOT NULL,
                    Hierarchy_5 TEXT NOT NULL,
                    Month TEXT NOT NULL,
                    Quantity INTEGER NOT NULL,
                    Value_SAP_Price REAL NOT NULL
                    );''')
            print("--New MI file initiated--")
        conn.commit()
        conn.close()

    # input mi by code
    def mi_by_code(self, ext_cmd="BLANK"):
        # get code number in ext
        if ext_cmd == "BLANK":
            print("-- Please input the material code: --")
            code = input("cmd >> MI >> BY_CODE >> ")
        else:
            code = ext_cmd
        # check code availability
        while not pb_func.check_code_availability(self.__class__.bu_name, code) and code != "exit":
            # if wrong input
            print("!Error!. Code does not exit. Please re-input")
            code = input("cmd >> MI >> BY_CODE >> ")
        # check exit
        if code == "exit":
            return
        # get MI data
        print("--Input your MI data in YYYYMM:Quantity")
        mi_result = []
        mi_input = input("cmd >> MI >> BY_CODE >> " + code + " >> ")
        while mi_input != "exit":
            # upload input to database
            if mi_input == "save":
                if len(mi_result) == 0:
                    print("No data yet.")
                else:
                    # insert value to db and release all the input
                    pb_func.upload_mi_data(code, self.__class__.bu_name, mi_result)
                    mi_result = []
                    print("--MI updated in Database--")
            else:
                mi_detail = mi_input.replace(' ', '').split(';')
                for mi_data in mi_detail:
                    mi_month = mi_data[0:6]
                    mi_qty = mi_data[7:]
                    if pb_func.check_future_month(mi_month, 24):
                        if mi_qty[0] == "-":
                            mi_qty_temp = mi_qty.lstrip('-')
                            if mi_qty_temp.isnumeric():
                                mi_result.append([mi_month, 0 - int(mi_qty_temp)])
                        elif mi_qty.isnumeric():
                            mi_result.append([mi_month, int(mi_qty)])
                        else:
                            pass
                    else:
                        pass
                print("MI Summary: ", mi_result)
            mi_input = input("cmd >> MI >> BY_CODE >> " + code + " >> ")
        pass

    # add mi by H5
    def mi_by_h5(self):
        print("-- Please input the Hierarchy_5 name: --")
        h5_input = input("cmd >> MI >> BY_H5 >> ")
        infocheck = cclt.InfoCheck(self.__class__.bu_name)
        h5_result = infocheck.get_h5_name(h5_input)
        if h5_result == "NULL":
            print("No Similar H5, Please re-input")
            return
        else:
            # get code list in this hierarchy:
            code_list = self.get_code_list_in_h5(h5_result)
            print("--Please input ratio (%) (float number)--")
            h5_ratio_input = input("cmd >> MI >> " + h5_result + " >> ")
            try:
                h5_ratio = float(h5_ratio_input)
            except ValueError:
                print("Not correct Number, Plz re-input")
                return
            print(h5_ratio)

        pass

    # get code list in forecast of one H5
    def get_code_list_in_h5(self, h5_name):
        # get code list in forecast
        statis_fcst_dbname = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast.db"
        statis_fcst_filename = self.__class__.bu_name + "_Statistical_Forecast_" + \
                               time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(statis_fcst_dbname)
        c = conn.cursor()
        c.execute("SELECT DISTINCT(Material) FROM " + statis_fcst_filename)
        fcst_code_list = [item[0] for item in c.fetchall()]
        conn.commit()
        conn.close()
        # get code list in this h5 in master file
        master_data_dbname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        master_data_filename = self.__class__.bu_name + "_Master_Data"
        conn = sqlite3.connect(master_data_dbname)
        c = conn.cursor()
        c.execute("SELECT Material from " + master_data_filename + " WHERE Hierarchy_5 = \'" + h5_name + "\'")
        master_code_list = [item[0] for item in c.fetchall()]
        # mapping forecast code list with h5 list
        code_list_result = []
        for item in master_code_list:
            if item in fcst_code_list:
                code_list_result.append(item)
        return code_list_result

    # submit MI, add mi to final forecast
    def submit_mi(self):
        # define database and filename
        mi_dbname = self.__class__.db_path + self.__class__.bu_name + "_MI.db"
        mi_filename = self.__class__.bu_name + "_MI_" + time.strftime("%Y%m", time.localtime())
        statis_fcst_dbname = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast.db"
        statis_fcst_filename = self.__class__.bu_name + "_Statistical_Forecast_" + \
                               time.strftime("%Y%m", time.localtime())
        final_fcst_dbname = self.__class__.db_path + self.__class__.bu_name + "_Final_Forecast.db"
        final_fcst_filename = self.__class__.bu_name + "_Final_Forecast_" + time.strftime("%Y%m", time.localtime())
        # get all mi data
        conn = sqlite3.connect(mi_dbname)
        c = conn.cursor()
        c.execute("SELECT * FROM " + mi_filename)
        # mi_result, [Material, Hierarchy_5, Month, Quantity, Value_SAP_Price]
        mi_result = c.fetchall()
        conn.commit()
        conn.close()
        # calculate final forecast
        conn2 = sqlite3.connect(statis_fcst_dbname)
        c = conn2.cursor()
        lst_final_fcst = []
        for mi_item in mi_result:
            sql_cmd = "SELECT Quantity, Value_SAP_Price FROM " + statis_fcst_filename + " WHERE Material = \'" + \
                      mi_item[0] + "\' AND Month = \'" + mi_item[2] + "\'"
            c.execute(sql_cmd)
            result = c.fetchall()[0]
            lst_final_fcst.append([mi_item[0], mi_item[1], mi_item[2], mi_item[3] + result[0], mi_item[4] + result[1]])
        conn2.commit()
        conn2.close()
        # upload final forecast
        conn3 = sqlite3.connect(final_fcst_dbname)
        c = conn3.cursor()
        for fcst_item in lst_final_fcst:
            sql_cmd = "Update " + final_fcst_filename + " SET \'Quantity\' = " + str(fcst_item[3]) + \
                      ", \'Value_SAP_Price\' = " + str(fcst_item[4]) + " WHERE Material = \'" + fcst_item[0] + \
                      "\' AND Month = \'" + fcst_item[2] + "\'"
            c.execute(sql_cmd)
        conn3.commit()
        conn3.close()

    # Reset Final Forecast as Statistical forecast
    def reset_final_forecast(self):
        # open file
        statis_fcst_dbname = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast.db"
        statis_fcst_filename = self.__class__.bu_name + "_Statistical_Forecast_" + \
                               time.strftime("%Y%m", time.localtime())
        final_fcst_dbname = self.__class__.db_path + self.__class__.bu_name + "_Final_Forecast.db"
        final_fcst_filename = self.__class__.bu_name + "_Final_Forecast_" + time.strftime("%Y%m", time.localtime())

        conn = sqlite3.connect(statis_fcst_dbname)
        c = conn.cursor()
        c.execute("SELECT * FROM " + statis_fcst_filename)
        fcst_result = c.fetchall()
        conn.commit()
        conn.close()

        conn = sqlite3.connect(final_fcst_dbname)
        c = conn.cursor()
        c.execute("DELETE FROM " + final_fcst_filename)
        c.executemany("INSERT INTO " + final_fcst_filename + " VALUES(?, ?, ?, ?, ?) ", fcst_result)
        conn.commit()
        conn.close()

    # entrance of MI
    def mi_start(self):
        print("==Market Intelligence Start==")
        print("==Note: Plz ensure statistical forecast is ready==")
        # check if mi file already here
        self.check_mi_file()
        print("--Please input your MI CMD--")
        # input cmd
        cmd_mi_code = input("cmd >> MI >> ")
        while cmd_mi_code.upper() != "EXIT" and cmd_mi_code.upper() != "QUIT":
            if cmd_mi_code == "bpdp":
                self.get_bpdp_alignment()
            elif cmd_mi_code[0:4].upper() == "CODE":
                if len(cmd_mi_code) != 4:
                    self.mi_by_code(cmd_mi_code[5:].replace(' ', ''))
                else:
                    self.mi_by_code()
            elif cmd_mi_code.upper() == "SUBMIT":
                print("==Start to update final forecast==")
                self.submit_mi()
                print("==MI submitted & final forecast updated==")
            elif cmd_mi_code.upper() == "RESET":
                self.reset_final_forecast()
                print("==Final Forecast has been reset to statistical forecast==")
            else:
                print("!Error. Please input your cmd or print exit to leave!")
            cmd_mi_code = input("cmd >> MI >> ")
        print("==Market Intelligence Close==")


if __name__ == '__main__':
    test = MI("TU")
    # test.get_statistical_forecast(["2019-09", "2019-10", "2019-11"], "by_code", "111")
    print(test.get_code_list_in_h5("VA Hand"))
