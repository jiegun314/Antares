# 基本思路
# 设置过去36个月的销量M_36,M_35,......M_1,当前月份M, 将来月份F_1, .....F_23
# T[i]表示月份系数，M_36=>1，逐渐累积，当前月是M=>37
# _WeekNUM是每月的星期数
# _Season[j]是每个月的调整系数,每年循环,j=1->12
# _CNY表示新年，0或者1
# FCST[i]=(_AS9*T[i]^2+_AT9*T[i]+_Base)*_WeekNUM*_AS10*_Season[j]
#        +_AS14*_CNY*(_AS9*T[i]^2+_AT9*T[i]+_Base)+_Other_Factor*_AS12  (i=1 - 36)
# 现阶段不考虑其他因素，取公式如下
# FCST[i]=(_AS9*T[i]^2+_AT9*T[i]+_Base)*（_WeekNUM*_AS10*_Season[j]+_AS14*_CNY[i]）
# 变量: _Season[j], _Base, _AS9, _AS12, _AS14, _AT9, _AS10
# 起始值
# _Season[j]=1 (for j=1 to j=12)，逐个载入？？？
# _AT9, _Base分别是M_36到M_1直线拟合的斜率和截距
# _AS9, _AS14, _AS12从零开始, _AS10从0.25开始
# 约束条件
# _AS9<=0, _Season[j]12个原始求和=12，每个元素>0
# 判断条件【取最小值】
# (FCST[i]-M_(37-i))^2/36，i从0到35的求和最小
# 最后结果
# 将i=37到i=60带入FCST[i],

# 创建表达式
# _Season月份系数
# _Pre_Volume前36个月的销量
# 变量X的表达式X=(_Season（x0-x11）,_AS9(x12),_AT9(x13),_Base(x14),_AS14(x15),_AS10(x16))

from scipy.optimize import minimize
import numpy as np
import time
import calculation
import data_import
import pandas as pd
import sqlite3
from datetime import datetime
from alive_progress import alive_bar


class GetStatisticalForecast:
    bu_name = ""
    db_path = "../data/_DB/"
    base_year = 0
    export_path = "../data/_Output/"

    def __init__(self, bu):
        self.__class__.bu_name = bu

    # 获取当前月份
    @staticmethod
    def get_current_month():
        return time.strftime("%Y-%m", time.localtime())

    # 获取code by month的N个月的月份列表
    def get_month_list(self, cclt_mode) -> list:
        # cclt_mode计算模式，historical表示只要历史月份，future表示将来月份, all表示包含将来预计月份
        # years表示历史数据的年份
        # 获得当前月份
        if cclt_mode == "historical":
            months = self.__class__.base_year * 12
        else:
            months = self.__class__.base_year * 12 + 24
        crt_month = time.strftime("%Y-%m", time.localtime())
        lst_month = crt_month.split("-")
        # 计算开始年份
        tmp_year = int(lst_month[0]) - self.__class__.base_year
        tmp_month = int(lst_month[1])
        # 生成result_month结果数组
        result_month = []
        # 转换成月份列表
        i = 1
        while i <= months:
            t = (tmp_year, tmp_month, 1, 0, 0, 0, 0, 0, 0)
            secs = time.mktime(t)
            result_month.append(time.strftime("%Y-%m", time.localtime(secs)))
            tmp_month = tmp_month + 1
            if tmp_month == 13:
                tmp_month = 1
                tmp_year = tmp_year + 1
            i = i + 1
        result_month = result_month[-24:] if cclt_mode == 'future' else result_month
        return result_month

    # 获取每个月中的星期数
    def week_in_month(self, first_month):
        # 导入月份YYYY-MM
        no_of_month = self.__class__.base_year * 12
        # 截取月份数
        month_index = int(first_month[-2:])
        # 初始化列表
        week_num = []
        i = 1
        while i <= no_of_month:
            if month_index % 3 == 0:
                week_num.append(5)
            else:
                week_num.append(4)
            i = i + 1
            month_index = month_index + 1
        # 转换成元组
        return tuple(week_num)

    # 获取春节的月份index
    def cny_index(self, first_month):
        # 导入月份YYYY-MM
        no_of_month = self.__class__.base_year * 12
        # 截取月份数
        month_index = int(first_month[-2:])
        # 初始化列表
        cny_index = []
        i = 1
        while i <= no_of_month:
            if month_index % 12 == 1:
                cny_index.append(1)
            else:
                cny_index.append(0)
            i = i + 1
            month_index = month_index + 1
        # 转换为元组
        return tuple(cny_index)

    # get sales quantity
    def get_historical_sales_qty(self, code_list, sales_type):
        print("====== Read %s Historical Data======" % sales_type)
        crt_mth = time.strftime("%Y-%m", time.localtime())
        mth_list = calculation.InfoCheck.get_time_list(crt_mth, 0 - self.__class__.base_year * 12)
        lst_blank = [0 * item for item in range(0, self.__class__.base_year * 12)]
        str_mth_list = '('
        for i in range(len(mth_list)):
            if i != (len(mth_list) - 1):
                str_mth_list = str_mth_list + '\"' + mth_list[i] + '\",'
            else:
                str_mth_list = str_mth_list + '\"' + mth_list[i] + '\")'
        sales_qty_result = []
        # connect to database
        database_fullname = self.__class__.db_path + self.__class__.bu_name + '_' + sales_type + '.db'
        table_name = self.__class__.bu_name + '_' + sales_type
        conn = sqlite3.connect(database_fullname)
        sql_cmd = 'SELECT Material, Month, Quantity FROM ' + table_name + ' WHERE Month in ' + str_mth_list
        df_qty = pd.read_sql(con=conn, sql=sql_cmd)
        df_pivot = pd.pivot_table(df_qty, index='Material', columns='Month', values='Quantity')
        df_pivot.fillna(0, inplace=True)
        # fill the last month if no data
        if mth_list[-1] not in df_pivot.columns.tolist():
            df_pivot[mth_list[-1]] = df_pivot[mth_list[-2]]
        # mapping to the code list
        for code_item in code_list:
            try:
                sales_qty_result.append(df_pivot.loc[code_item].values.tolist())
            except KeyError:
                sales_qty_result.append(lst_blank)
        return sales_qty_result

    # new func to get minimum variance of legacy sales recorde in past months
    def func(self, args, mth_qty):
        week_num, cny_index, pre_volume = args
        # _Season,_AS9,_AT9,_Base,_WeekNUM,_AS14,_Pre_Volume=args

        def v(x):
            ttl_rsl = 0
            for i in range(mth_qty):
                ttl_rsl += ((x[12] * (i + 1) ** 2 + x[13] * (i + 1) + x[14]) *
                            (week_num[i] * x[i % 12] * x[16] + x[15] * cny_index[i]) - pre_volume[i]) ** 2
            ttl_rsl = ttl_rsl / mth_qty
            return ttl_rsl
        return v

    def con(self, args):
        # 约束条件
        _AS9_crtt, _season, _season_tt = args
        cons = ({'type': 'ineq', 'fun': lambda x: _AS9_crtt - x[12]},
                {'type': 'eq', 'fun': lambda x: x[0] + x[1] + x[2] + x[3] + x[4] + x[5] + x[6] +
                                                x[7] + x[8] + x[9] + x[10] + x[11] - _season_tt},
                {'type': 'ineq', 'fun': lambda x: x[0] - _season},
                {'type': 'ineq', 'fun': lambda x: x[1] - _season},
                {'type': 'ineq', 'fun': lambda x: x[2] - _season},
                {'type': 'ineq', 'fun': lambda x: x[3] - _season},
                {'type': 'ineq', 'fun': lambda x: x[4] - _season},
                {'type': 'ineq', 'fun': lambda x: x[5] - _season},
                {'type': 'ineq', 'fun': lambda x: x[6] - _season},
                {'type': 'ineq', 'fun': lambda x: x[7] - _season},
                {'type': 'ineq', 'fun': lambda x: x[8] - _season},
                {'type': 'ineq', 'fun': lambda x: x[9] - _season},
                {'type': 'ineq', 'fun': lambda x: x[10] - _season},
                {'type': 'ineq', 'fun': lambda x: x[11] - _season},
                )
        return cons

    def forecast_calculation(self, x2_parameter, week_num, cny_index, his_volume, base_year):
        # 定义常量-每月星期数
        _week_num = week_num
        # 定义常量 - 春节index
        _cny_index = cny_index
        # 定义历史数据的年数
        _base_year = int(base_year)
        # 定义常量-过去24或者36月的销量
        # 注意，在导入销量的时候抹去负数，变成零
        _pre_volume = his_volume
        # 生成参数元组
        args = (_week_num, _cny_index, _pre_volume)
        # 生成约束条件
        # 第一个参数代表二次项系数的最大值，如果为零，则表示为开口向下的二次函数
        args_con = (x2_parameter, 0, 12)
        cons = self.con(args_con)
        # 设置_AS9,_AS14,_AS10
        _as9_start, _as14_start, _as10_start = 0, 0, 0.25
        # 获取_AT9, _Base
        # 生成x轴月份列表
        # i = 0
        x = np.arange(1, _base_year * 12 + 1, 1)
        # 线性拟合
        z1 = np.polyfit(x, list(_pre_volume), 1)
        # 获取截距和斜率
        _at9_start = z1[0]
        _base_start = z1[1]
        # 猜测初始值
        # 基本思路，当历史销量都为零时，直接放入零，当斜率和截距的总和为负数时，选择1，其余情况，取前三年实际均值和拟合值的比值
        s_index = []
        for k in range(1, 13):
            if _at9_start == 0 and _base_start == 0:
                ratio = 0
            elif (_at9_start + _base_start) < 0:
                ratio = 1
            else:
                if _base_year == 2:
                    avg_temp = (_pre_volume[k - 1] + _pre_volume[k + 11]) / 2
                else:
                    avg_temp = (_pre_volume[k - 1] + _pre_volume[k + 11] + _pre_volume[k + 23]) / 3
                ratio = min(10, avg_temp / (_at9_start * k + _base_start))
            s_index.append(ratio)
        x0 = np.asarray(
            (s_index[0], s_index[1], s_index[2], s_index[3], s_index[4], s_index[5], s_index[6], s_index[7], s_index[8],
             s_index[9], s_index[10], s_index[11],
             _as9_start, _at9_start, _base_start, _as14_start, _as10_start))
        # 运行拟合
        if _base_year == 3:
            res = minimize(self.func(args, 36), x0, method='SLSQP', constraints=cons, tol=0.1)
        else:
            res = minimize(self.func(args, 24), x0, method='SLSQP', constraints=cons, tol=0.1)
        # 打印拟合结果
        result = res.x
        # return the new parameter
        _as9_result, _at9_result, _base_result, _as14_result, _as10_result = result[-5:]
        # get fcst value in future 24 months
        fcst_year = 2
        forecast_result = []
        for j in range(fcst_year * 12):
            k = j % 12
            mth_index = j + 12 * _base_year + 1
            item_result = (_as9_result * mth_index ** 2 + _at9_result * mth_index + _base_result) * \
                          (_week_num[j] * result[k] * _as10_result + _as14_result * _cny_index[j])
            forecast_result.append(max(0, item_result))
        return forecast_result
        # # 打印历史值
        # # print(_pre_volume)
        # # 拟合过去几个月的量
        # pre_result = []
        # for j in range(12 * _base_year):
        #     # print(result[j%12-1])
        #     # 获得计算值
        #     value_cclt = (result[12] * (j + 1) ** 2 + result[13] * (j + 1) + result[14]) * (_week_num[j] * result[j % 12] * result[16] + result[15] * cny_index[j])
        #     pre_result.append(max(0, value_cclt))
        # # print(pre_result)
        # # 计算将来24个月的量
        # fcst_result = []
        # for j in range(1, 25):
        #     # print(result[j%12-1])
        #     if j != 12 and j != 24:
        #         k = j % 12 - 1
        #     else:
        #         k = 11
        #     value_cclt = (result[12] * (j + 12 * _base_year) ** 2 + result[13] * (j + 12 * _base_year) + result[14]) * \
        #                  (_week_num[j - 1] * result[k] * result[16] + result[15] * _cny_index[j - 1])
        #     fcst_result.append(max(0, value_cclt))
        # # print(fcst_result)
        # simulation_result = pre_result + fcst_result
        # # 返回所有今年的模拟值
        # return simulation_result

    # 写入excel报表
    def export_to_excel(self, lst_data, data_type):
        # 写入数组
        np_data = np.array(lst_data)
        # 导入dataframe
        df = pd.DataFrame(data=np_data[1:, 1:], index=np_data[1:, 0], columns=np_data[0, 1:], dtype="float64")
        # 导出到excel
        current_time = time.strftime("%y%m%d-%H%M%S", time.localtime())
        file_name = self.__class__.bu_name + "_Forecast_" + data_type + "_Base_" + current_time + ".xlsx"
        file_fullname = self.__class__.export_path + file_name
        df.to_excel(file_fullname, index_label="Material", float_format="%.2f")
        print("=== Find your result in %s ===" % file_fullname)

    # write to database
    def export_to_database(self, lst_data_input):
        # get month list
        lst_month = lst_data_input.pop(0)
        lst_month.pop(0)
        # change to format for forecast and reformat to dataframe
        lst_data = []
        for item_input in lst_data_input:
            str_material = item_input.pop(0)
            for i in range(len(item_input)):
                lst_data.append([str_material, lst_month[i], round(item_input[i])])
        df_fcst = pd.DataFrame(np.array(lst_data), columns=['Material', 'Month', 'Quantity'])
        df_fcst.set_index('Material', inplace=True)
        df_fcst['Quantity'] = df_fcst['Quantity'].astype('int64')
        # get master data
        master_data_database = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        table_name = self.__class__.bu_name + "_Master_Data"
        conn = sqlite3.connect(master_data_database)
        sql_cmd = 'SELECT Material, Hierarchy_5, SAP_Price FROM ' + table_name
        df_master_data = pd.read_sql(sql=sql_cmd, con=conn, index_col='Material')
        # combine and caculate the value
        df_fcst = df_fcst.join(df_master_data)
        df_fcst.fillna(0, inplace=True)
        df_fcst['Value_SAP_Price'] = df_fcst['Quantity'] * df_fcst['SAP_Price']
        # remove value column and reformat
        df_fcst.drop(columns='SAP_Price', inplace=True)
        df_fcst = df_fcst[['Hierarchy_5', 'Month', 'Quantity', 'Value_SAP_Price']]
        df_fcst.reset_index(inplace=True)
        # write to database
        fcst_databse_name = self.__class__.db_path + self.__class__.bu_name + "_Statistical_Forecast.db"
        table_name = self.__class__.bu_name + "_Statistical_Forecast" + "_" + time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(fcst_databse_name)
        df_fcst.to_sql(name=table_name, con=conn, index=False, if_exists='replace')
        print("=== %s Updated ===" % table_name)

    # write into database
    def export_to_database_old(self, lst_data):
        # get month list
        month_list = lst_data.pop(0)
        month_list.pop(0)
        tbl_result = [["Material", "Hierarchy_5", "Month", "Quantity", "Value_SAP_Price"]]
        db_mm_fullname = self.__class__.db_path + self.__class__.bu_name + "_Master_Data.db"
        filename = self.__class__.bu_name + "_Master_Data"
        conn = sqlite3.connect(db_mm_fullname)
        c = conn.cursor()
        # get forecast data
        for code_fcst in lst_data:
            # get forecast for one code
            lst_code = []
            code_name = code_fcst.pop(0)
            # read hierarchy_5 and sap price from master data
            sql_cmd = "SELECT Hierarchy_5, SAP_Price from " + filename + " WHERE Material = \'" + code_name + "\'"
            c.execute(sql_cmd)
            try:
                h5, sap_price = c.fetchall()[0]
            except IndexError:
                h5, sap_price = "0", 0
            index = 0
            for qty in code_fcst:
                sap_price = 0 if sap_price is None else sap_price
                lst_code.append([code_name, h5, month_list[index], int(round(qty)), int(round(qty) * sap_price)])
                index += 1
            tbl_result.extend(lst_code)
        # 写入数组
        np_data = np.array(tbl_result)
        # get data frame
        df = pd.DataFrame(data=np_data[1:, 0:], columns=np_data[0, 0:])
        df = df.astype(dtype={"Quantity": "int64", "Value_SAP_Price": "int64"})
        # write to statistical forecast
        tbl_statis_fcst = self.__class__.bu_name + "_Statistical_Forecast"
        db_statis_fcst_fullname = self.__class__.db_path + tbl_statis_fcst + ".db"
        tbl_name = tbl_statis_fcst + "_" + time.strftime("%Y%m", time.localtime())
        conn = sqlite3.connect(db_statis_fcst_fullname)
        df.to_sql(tbl_name, conn, index=False, if_exists='replace')
        conn.commit()
        conn.close()
        print("=== Statistical Forecast Updated %s ===" % db_statis_fcst_fullname)

    # fcst程序入口
    def get_forecast_entrance(self):
        # 打印标题
        print("====== < Dragon - Statistical Forecast Generator > ======")
        print("===== !Warning! Make sure you've updated sales data and release your PC capacity! =====")
        trigger = input(">>>> Ready to Go? (Y / N) : ")
        if trigger.upper() != "Y":
            return
        inv_type = input("Choose your baseline for calculation (1 - LP Sales, 2 - IMS) : ")
        if inv_type not in ['1', '2']:
            print("!Error! Please input 1 or 2 only. Retry!")
            return
        data_type = 'LPSales' if inv_type == '1' else 'IMS'
        self.__class__.base_year = 2 if inv_type == '1' else 3
        # Set Parameter of X_Square
        x_square_input = input("Input Parameter for X_Square (Data Type: Float, Default: 0): ")
        try:
            x_square = float(x_square_input)
        except ValueError:
            print("Wrong input! Please input a correct number!")
            return
        # 获取活跃代码列表
        get_code_list = data_import.DataImport(self.__class__.bu_name)
        active_code_list = get_code_list.get_active_codes('Normal', 'Forecast')
        # 获取历史销量数据
        historical_sales_qty = self.get_historical_sales_qty(active_code_list, data_type)
        # 获取月份列表
        # lst_month = self.get_month_list("all")
        # 月份星期数统计
        lst_week_in_month = self.week_in_month(self.get_current_month())
        # 春节索引表
        lst_cny_index = self.cny_index(self.get_current_month())
        # 开始计算
        # 开始计时
        start_time = datetime.now()
        print("====== Simulation Start ======")
        # simulate with progress bar
        fcst_result = []
        with alive_bar(len(historical_sales_qty), bar='blocks') as bar:
            for sales_item in historical_sales_qty:
                pre_volume = tuple(sales_item)
                # 运行计算
                result = self.forecast_calculation(x_square, lst_week_in_month, lst_cny_index, pre_volume,
                                                   self.__class__.base_year)
                fcst_result.append(result)
                bar()
        print("====== Simulation Done, Start Writing Data to System ======")
        # 数据整合
        # Make table head with Material title and future 24 month calendar
        lst_title = ['Material'] + self.get_month_list("future")
        for i in range(len(active_code_list)):
            fcst_result[i].insert(0, active_code_list[i])
        fcst_result.insert(0, lst_title)
        # 导入数据
        # k = 0
        # for item in active_code_list:
        #     final_item = list([item],)
        #     final_item.extend(fcst_result[k])
        #     final_result.append(final_item)
        #     k += 1
        # 打印头十行
        # for j in range(0, 10):
        #     print(final_result[j])
        self.export_to_excel(fcst_result, data_type)
        self.export_to_database(fcst_result)
        stop_time = datetime.now()
        print("====Simulation Complete. Time: %s seconds. " % (stop_time - start_time).seconds)


if __name__ == '__main__':
    bu_name = input('Please input BU name: ')
    new_fcst = GetStatisticalForecast(bu_name)
    new_fcst.get_forecast_entrance()
