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
    def get_month_list(self, cclt_mode):
        # cclt_mode计算模式，historical表示只要历史月份，all表示包含将来预计月份
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

    # 获取历史销量
    def get_sale_list(self, code_list, data_type):
        # 打印标题
        print("====== Read %s Historical Data======" % data_type)
        sales_qty_result = []
        # 计数变量
        counter = 0
        list_length = len(code_list)
        list_show = []
        gap_show = int(list_length / 20)
        for i in range(1, 21):
            list_show.append(i * gap_show)
        num = 5
        for code in code_list:
            get_sales_qty = calculation.InfoCheck(self.__class__.bu_name)
            sales_code_result = get_sales_qty.get_code_sales(data_type, code, self.__class__.base_year * 12)
            sales_qty_result.append(sales_code_result)
            # 显示计数
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        print("\n")
        print("====== Read %s Codes for Calculation======" % len(code_list))
        return sales_qty_result

    # 36个月的历史纪录取最小偏差
    def fun_36(self, args):
        # 读取月销量
        week_num, cny_index, pre_volume = args

        # _Season,_AS9,_AT9,_Base,_WeekNUM,_AS14,_Pre_Volume=args
        def v(x): return (((x[12] * 1 ** 2 + x[13] * 1 + x[14]) * (week_num[0] * x[0] * x[16] + x[15] * cny_index[0]) -
                           pre_volume[0]) ** 2 +
                          ((x[12] * 2 ** 2 + x[13] * 2 + x[14]) * (week_num[1] * x[1] * x[16] + x[15] * cny_index[12]) -
                           pre_volume[1]) ** 2 +
                          ((x[12] * 3 ** 2 + x[13] * 3 + x[14]) * (week_num[2] * x[2] * x[16] + x[15] * cny_index[13]) -
                           pre_volume[2]) ** 2 +
                          ((x[12] * 4 ** 2 + x[13] * 4 + x[14]) * (week_num[3] * x[3] * x[16] + x[15] * cny_index[14]) -
                           pre_volume[3]) ** 2 +
                          ((x[12] * 5 ** 2 + x[13] * 5 + x[14]) * (week_num[4] * x[4] * x[16] + x[15] * cny_index[4]) -
                           pre_volume[4]) ** 2 +
                          ((x[12] * 6 ** 2 + x[13] * 6 + x[14]) * (week_num[5] * x[5] * x[16] + x[15] * cny_index[5]) -
                           pre_volume[5]) ** 2 +
                          ((x[12] * 7 ** 2 + x[13] * 7 + x[14]) * (week_num[6] * x[6] * x[16] + x[15] * cny_index[6]) -
                           pre_volume[6]) ** 2 +
                          ((x[12] * 8 ** 2 + x[13] * 8 + x[14]) * (week_num[7] * x[7] * x[16] + x[15] * cny_index[7]) -
                           pre_volume[7]) ** 2 +
                          ((x[12] * 9 ** 2 + x[13] * 9 + x[14]) * (week_num[8] * x[8] * x[16] + x[15] * cny_index[8]) -
                           pre_volume[8]) ** 2 +
                          ((x[12] * 10 ** 2 + x[13] * 10 + x[14]) * (
                                      week_num[9] * x[9] * x[16] + x[15] * cny_index[9]) - pre_volume[9]) ** 2 +
                          ((x[12] * 11 ** 2 + x[13] * 11 + x[14]) * (
                                      week_num[10] * x[10] * x[16] + x[15] * cny_index[10]) - pre_volume[10]) ** 2 +
                          ((x[12] * 12 ** 2 + x[13] * 12 + x[14]) * (
                                      week_num[11] * x[11] * x[16] + x[15] * cny_index[11]) - pre_volume[11]) ** 2 +
                          ((x[12] * 13 ** 2 + x[13] * 13 + x[14]) * (
                                      week_num[12] * x[0] * x[16] + x[15] * cny_index[12]) - pre_volume[12]) ** 2 +
                          ((x[12] * 14 ** 2 + x[13] * 14 + x[14]) * (
                                      week_num[13] * x[1] * x[16] + x[15] * cny_index[13]) - pre_volume[13]) ** 2 +
                          ((x[12] * 15 ** 2 + x[13] * 15 + x[14]) * (
                                      week_num[14] * x[2] * x[16] + x[15] * cny_index[14]) - pre_volume[14]) ** 2 +
                          ((x[12] * 16 ** 2 + x[13] * 16 + x[14]) * (
                                      week_num[15] * x[3] * x[16] + x[15] * cny_index[15]) - pre_volume[15]) ** 2 +
                          ((x[12] * 17 ** 2 + x[13] * 17 + x[14]) * (
                                      week_num[16] * x[4] * x[16] + x[15] * cny_index[16]) - pre_volume[16]) ** 2 +
                          ((x[12] * 18 ** 2 + x[13] * 18 + x[14]) * (
                                      week_num[17] * x[5] * x[16] + x[15] * cny_index[17]) - pre_volume[17]) ** 2 +
                          ((x[12] * 19 ** 2 + x[13] * 19 + x[14]) * (
                                      week_num[18] * x[6] * x[16] + x[15] * cny_index[18]) - pre_volume[18]) ** 2 +
                          ((x[12] * 20 ** 2 + x[13] * 20 + x[14]) * (
                                      week_num[19] * x[7] * x[16] + x[15] * cny_index[19]) - pre_volume[19]) ** 2 +
                          ((x[12] * 21 ** 2 + x[13] * 21 + x[14]) * (
                                      week_num[20] * x[8] * x[16] + x[15] * cny_index[20]) - pre_volume[20]) ** 2 +
                          ((x[12] * 22 ** 2 + x[13] * 22 + x[14]) * (
                                      week_num[21] * x[9] * x[16] + x[15] * cny_index[21]) - pre_volume[21]) ** 2 +
                          ((x[12] * 23 ** 2 + x[13] * 23 + x[14]) * (
                                      week_num[22] * x[10] * x[16] + x[15] * cny_index[22]) - pre_volume[22]) ** 2 +
                          ((x[12] * 24 ** 2 + x[13] * 24 + x[14]) * (
                                      week_num[23] * x[11] * x[16] + x[15] * cny_index[23]) - pre_volume[23]) ** 2 +
                          ((x[12] * 25 ** 2 + x[13] * 25 + x[14]) * (
                                      week_num[24] * x[0] * x[16] + x[15] * cny_index[24]) - pre_volume[24]) ** 2 +
                          ((x[12] * 26 ** 2 + x[13] * 26 + x[14]) * (
                                      week_num[25] * x[1] * x[16] + x[15] * cny_index[25]) - pre_volume[25]) ** 2 +
                          ((x[12] * 27 ** 2 + x[13] * 27 + x[14]) * (
                                      week_num[26] * x[2] * x[16] + x[15] * cny_index[26]) - pre_volume[26]) ** 2 +
                          ((x[12] * 28 ** 2 + x[13] * 28 + x[14]) * (
                                      week_num[27] * x[3] * x[16] + x[15] * cny_index[27]) - pre_volume[27]) ** 2 +
                          ((x[12] * 29 ** 2 + x[13] * 29 + x[14]) * (
                                      week_num[28] * x[4] * x[16] + x[15] * cny_index[28]) - pre_volume[28]) ** 2 +
                          ((x[12] * 30 ** 2 + x[13] * 30 + x[14]) * (
                                      week_num[29] * x[5] * x[16] + x[15] * cny_index[29]) - pre_volume[29]) ** 2 +
                          ((x[12] * 31 ** 2 + x[13] * 31 + x[14]) * (
                                      week_num[30] * x[6] * x[16] + x[15] * cny_index[30]) - pre_volume[30]) ** 2 +
                          ((x[12] * 32 ** 2 + x[13] * 32 + x[14]) * (
                                      week_num[31] * x[7] * x[16] + x[15] * cny_index[31]) - pre_volume[31]) ** 2 +
                          ((x[12] * 33 ** 2 + x[13] * 33 + x[14]) * (
                                      week_num[32] * x[8] * x[16] + x[15] * cny_index[32]) - pre_volume[32]) ** 2 +
                          ((x[12] * 34 ** 2 + x[13] * 34 + x[14]) * (
                                      week_num[33] * x[9] * x[16] + x[15] * cny_index[33]) - pre_volume[33]) ** 2 +
                          ((x[12] * 35 ** 2 + x[13] * 35 + x[14]) * (
                                      week_num[34] * x[10] * x[16] + x[15] * cny_index[34]) - pre_volume[34]) ** 2 +
                          ((x[12] * 36 ** 2 + x[13] * 36 + x[14]) * (
                                      week_num[35] * x[11] * x[16] + x[15] * cny_index[35]) - pre_volume[35]) ** 2) / 36

        return v

    # 24个月的历史纪录取最小偏差
    def fun_24(self, args):
        # 读取月销量
        week_num, cny_index, pre_volume = args

        # _Season,_AS9,_AT9,_Base,_WeekNUM,_AS14,_Pre_Volume=args
        def v(x): return (((x[12] * 1 ** 2 + x[13] * 1 + x[14]) * (week_num[0] * x[0] * x[16] + x[15] * cny_index[0]) -
                           pre_volume[0]) ** 2 +
                          ((x[12] * 2 ** 2 + x[13] * 2 + x[14]) * (week_num[1] * x[1] * x[16] + x[15] * cny_index[12]) -
                           pre_volume[1]) ** 2 +
                          ((x[12] * 3 ** 2 + x[13] * 3 + x[14]) * (week_num[2] * x[2] * x[16] + x[15] * cny_index[13]) -
                           pre_volume[2]) ** 2 +
                          ((x[12] * 4 ** 2 + x[13] * 4 + x[14]) * (week_num[3] * x[3] * x[16] + x[15] * cny_index[14]) -
                           pre_volume[3]) ** 2 +
                          ((x[12] * 5 ** 2 + x[13] * 5 + x[14]) * (week_num[4] * x[4] * x[16] + x[15] * cny_index[4]) -
                           pre_volume[4]) ** 2 +
                          ((x[12] * 6 ** 2 + x[13] * 6 + x[14]) * (week_num[5] * x[5] * x[16] + x[15] * cny_index[5]) -
                           pre_volume[5]) ** 2 +
                          ((x[12] * 7 ** 2 + x[13] * 7 + x[14]) * (week_num[6] * x[6] * x[16] + x[15] * cny_index[6]) -
                           pre_volume[6]) ** 2 +
                          ((x[12] * 8 ** 2 + x[13] * 8 + x[14]) * (week_num[7] * x[7] * x[16] + x[15] * cny_index[7]) -
                           pre_volume[7]) ** 2 +
                          ((x[12] * 9 ** 2 + x[13] * 9 + x[14]) * (week_num[8] * x[8] * x[16] + x[15] * cny_index[8]) -
                           pre_volume[8]) ** 2 +
                          ((x[12] * 10 ** 2 + x[13] * 10 + x[14]) * (
                                      week_num[9] * x[9] * x[16] + x[15] * cny_index[9]) - pre_volume[9]) ** 2 +
                          ((x[12] * 11 ** 2 + x[13] * 11 + x[14]) * (
                                      week_num[10] * x[10] * x[16] + x[15] * cny_index[10]) - pre_volume[10]) ** 2 +
                          ((x[12] * 12 ** 2 + x[13] * 12 + x[14]) * (
                                      week_num[11] * x[11] * x[16] + x[15] * cny_index[11]) - pre_volume[11]) ** 2 +
                          ((x[12] * 13 ** 2 + x[13] * 13 + x[14]) * (
                                      week_num[12] * x[0] * x[16] + x[15] * cny_index[12]) - pre_volume[12]) ** 2 +
                          ((x[12] * 14 ** 2 + x[13] * 14 + x[14]) * (
                                      week_num[13] * x[1] * x[16] + x[15] * cny_index[13]) - pre_volume[13]) ** 2 +
                          ((x[12] * 15 ** 2 + x[13] * 15 + x[14]) * (
                                      week_num[14] * x[2] * x[16] + x[15] * cny_index[14]) - pre_volume[14]) ** 2 +
                          ((x[12] * 16 ** 2 + x[13] * 16 + x[14]) * (
                                      week_num[15] * x[3] * x[16] + x[15] * cny_index[15]) - pre_volume[15]) ** 2 +
                          ((x[12] * 17 ** 2 + x[13] * 17 + x[14]) * (
                                      week_num[16] * x[4] * x[16] + x[15] * cny_index[16]) - pre_volume[16]) ** 2 +
                          ((x[12] * 18 ** 2 + x[13] * 18 + x[14]) * (
                                      week_num[17] * x[5] * x[16] + x[15] * cny_index[17]) - pre_volume[17]) ** 2 +
                          ((x[12] * 19 ** 2 + x[13] * 19 + x[14]) * (
                                      week_num[18] * x[6] * x[16] + x[15] * cny_index[18]) - pre_volume[18]) ** 2 +
                          ((x[12] * 20 ** 2 + x[13] * 20 + x[14]) * (
                                      week_num[19] * x[7] * x[16] + x[15] * cny_index[19]) - pre_volume[19]) ** 2 +
                          ((x[12] * 21 ** 2 + x[13] * 21 + x[14]) * (
                                      week_num[20] * x[8] * x[16] + x[15] * cny_index[20]) - pre_volume[20]) ** 2 +
                          ((x[12] * 22 ** 2 + x[13] * 22 + x[14]) * (
                                      week_num[21] * x[9] * x[16] + x[15] * cny_index[21]) - pre_volume[21]) ** 2 +
                          ((x[12] * 23 ** 2 + x[13] * 23 + x[14]) * (
                                      week_num[22] * x[10] * x[16] + x[15] * cny_index[22]) - pre_volume[22]) ** 2 +
                          ((x[12] * 24 ** 2 + x[13] * 24 + x[14]) * (
                                      week_num[23] * x[11] * x[16] + x[15] * cny_index[23]) - pre_volume[23]) ** 2) / 24

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
        i = 0
        x = np.arange(1, 25, 1) if _base_year == 2 else np.arange(1, 37, 1)
        # 线性拟合
        z1 = np.polyfit(x, list(_pre_volume), 1)
        # 获取截距和斜率
        _at9_start = z1[0]
        _base_start = z1[1]
        # 猜测初始值
        # 基本思路，当历史销量都为零时，直接放入零，当斜率和截距的总和为负数时，选择1，其余情况，取前三年实际均值和拟合值的比值
        s_index = []
        k = 1
        while k <= 12:
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
            k = k + 1
        x0 = np.asarray(
            (s_index[0], s_index[1], s_index[2], s_index[3], s_index[4], s_index[5], s_index[6], s_index[7], s_index[8],
             s_index[9], s_index[10], s_index[11],
             _as9_start, _at9_start, _base_start, _as14_start, _as10_start))
        # 运行拟合
        if _base_year == 3:
            res = minimize(self.fun_36(args), x0, method='SLSQP', constraints=cons, tol=0.1)
        else:
            res = minimize(self.fun_24(args), x0, method='SLSQP', constraints=cons, tol=0.1)
        # 打印拟合结果
        result = res.x
        # 打印历史值
        # print(_pre_volume)
        # 拟合过去几个月的量
        pre_result = []
        j = 0
        while j < 12 * _base_year:
            # print(result[j%12-1])
            # 获得计算值
            value_cclt = (result[12] * (j + 1) ** 2 + result[13] * (j + 1) + result[14]) * (_week_num[j] * result[j % 12] * result[16] + result[15] * cny_index[j])
            pre_result.append(max(0, value_cclt))
            j = j + 1
        # print(pre_result)
        # 计算将来24个月的量
        fcst_result = []
        j = 1
        while j <= 24:
            # print(result[j%12-1])
            if j != 12 and j != 24:
                k = j % 12 - 1
            else:
                k = 11
            value_cclt = (result[12] * (j + 36) ** 2 + result[13] * (j + 36) + result[14]) * (_week_num[j - 1] * result[k] * result[16] + result[15] * _cny_index[j - 1])
            fcst_result.append(max(0, value_cclt))
            j = j + 1
        # print(fcst_result)
        simulation_result = pre_result + fcst_result
        # 返回所有今年的模拟值
        return simulation_result

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

    # write into database
    def export_to_database(self, lst_data):
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

    # 对于IMS最后一个月数据补足
    def fulfill_last_month_ims(self, lst_sales_data):
        sales_sum = 0
        for item in lst_sales_data:
            sales_sum += item[-1]
        # 如果最后一个月数据不存在，则取六个月平均
        if sales_sum == 0:
            for lst_code_sales in lst_sales_data:
                six_month_sales = 0
                for index in range(-2, -8, -1):
                    six_month_sales += lst_code_sales[index]
                lst_code_sales[-1] = int(six_month_sales / 6)
            print("==Last month IMS has been fulfilled==")
            return lst_sales_data
        # 如果存在则返回原值
        else:
            return lst_sales_data

    # fcst程序入口
    def get_forecast_entrance(self):
        # 打印标题
        print("====== < Dragon - Statistical Forecast Generator > ======")
        print("===== !Warning! Make sure you've updated sales data and release your PC capacity! =====")
        trigger = input(">>>> Ready to Go? (Y / N) : ")
        if trigger != "Y" and trigger != "y":
            return
        inv_type = input("Choose your baseline for calculation (1 - LP Sales, 2 - IMS) : ")
        if inv_type != '1' and inv_type != "2":
            print("!Error! Please input 1 or 2 only. Retry!")
            return
        elif inv_type == "1":
            data_type = "LPSales"
            self.__class__.base_year = 2
        else:
            data_type = "IMS"
            self.__class__.base_year = 3
        # Set Parameter of X_Square
        x_square_input = input("Input Parameter for X_Square (Data Type: Float, Default: 0): ")
        try:
            x_square = float(x_square_input)
        except ValueError:
            print("Wrong input! Please input a correct number!")
            return
        # 获取活跃代码列表
        get_code_list = data_import.DataInput(self.__class__.bu_name)
        active_code_list = get_code_list.get_active_codes('Normal', 'Forecast')
        # 获取历史销量数据
        historical_sales_qty = self.get_sale_list(active_code_list, data_type)
        # 对于IMS的最后一个月进行判断补足
        if inv_type == "2":
            historical_sales_qty = self.fulfill_last_month_ims(historical_sales_qty)
        # 获取月份列表
        lst_month = self.get_month_list("all")
        # 月份星期数统计
        lst_week_in_month = self.week_in_month(self.get_current_month())
        # 春节索引表
        lst_cny_index = self.cny_index(self.get_current_month())
        # 开始计算
        # 开始计时
        start_time = datetime.now()
        print("====== Simulation Start ======")
        # 计数变量
        counter = 0
        list_length = len(historical_sales_qty)
        list_show = []
        gap_show = int(list_length / 20)
        for i in range(1, 21):
            list_show.append(i * gap_show)
        num = 5
        # 拟合开始
        fcst_result = []
        for sales_item in historical_sales_qty:
            pre_volume = tuple(sales_item)
            # 运行计算
            result = self.forecast_calculation(x_square, lst_week_in_month, lst_cny_index, pre_volume, self.__class__.base_year)
            fcst_result.append(result)
            # 显示计数
            counter += 1
            if counter in list_show:
                print(" -->", num, "%", end="", flush=True)
                num += 5
        print("\n")
        print("====== Simulation Done, Start Writing Data to System ======")
        # 数据整合
        final_result = []
        # 制作表头
        list_head = lst_month.copy()
        list_head.insert(0, "Material")
        final_result.append(list_head)
        # 导入数据
        k = 0
        for item in active_code_list:
            final_item = list([item],)
            final_item.extend(fcst_result[k])
            final_result.append(final_item)
            k += 1
        # 打印头十行
        # for j in range(0, 10):
        #     print(final_result[j])
        self.export_to_excel(final_result, data_type)
        self.export_to_database(final_result)
        stop_time = datetime.now()
        print("====Simulation Complete. Time: %s seconds. " % (stop_time - start_time).seconds)


if __name__ == '__main__':
    new_fcst = GetStatisticalForecast('TU')
    new_fcst.get_forecast_entrance()
