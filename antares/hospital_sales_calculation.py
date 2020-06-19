import pandas as pd
import sqlite3
from pyecharts import options as opts
from pyecharts.charts import Map, Timeline
from pyecharts.globals import WarningType
from pyecharts.globals import ThemeType
import math
import platform
import subprocess
import os


class HospitalSalesCalculation:
    bu_name = ''
    database_path = '../data/_DB/'
    update_file_path = '../data/_Update/'
    sys_path = os.path.abspath('..')
    chart_path = sys_path + "/data/_Charter/"

    def __init__(self, bu_input):
        self.__class__.bu_name = bu_input
        pass

    def read_china_sales_data(self):
        database_full_name = self.__class__.database_path + self.__class__.bu_name + '_Hospital_Sales.db'
        data_file_name = self.__class__.bu_name + '_Hospital_Sales'
        conn = sqlite3.connect(database_full_name)
        # get month list
        sql_cmd = 'SELECT DISTINCT(Month) FROM ' + data_file_name
        month_list = [item[0] for item in pd.read_sql(con=conn, sql=sql_cmd).values.tolist()]
        # read province and monthly sales data from database
        sql_cmd = 'SELECT Month, Province, round(sum(Sales_Value)/1000000, 1) as Sales_Value FROM ' + data_file_name + \
                  ' GROUP BY Province, Month ORDER BY Month'
        df_sales = pd.read_sql(con=conn, sql=sql_cmd)
        max_sales = math.ceil(df_sales.loc[:,'Sales_Value'].max())
        # write in to dict
        dict_sales = {}
        for month_item in month_list:
            df_monthly_sales = df_sales.loc[df_sales['Month']==month_item, ['Province', 'Sales_Value']]
            monthly_sales_result = df_monthly_sales.values.tolist()
            dict_sales[month_item] = monthly_sales_result
        # draw chart
        self.draw_map_chart(dict_sales, max_sales, 'china')

    def read_province_sales_data(self, province_selected):
        database_full_name = self.__class__.database_path + self.__class__.bu_name + '_Hospital_Sales.db'
        data_file_name = self.__class__.bu_name + '_Hospital_Sales'
        conn = sqlite3.connect(database_full_name)
        # get month list
        sql_cmd = 'SELECT DISTINCT(Month) FROM ' + data_file_name
        month_list = [item[0] for item in pd.read_sql(con=conn, sql=sql_cmd).values.tolist()]
        # read city and monthly sales data from database
        sql_cmd = 'SELECT Month, City, round(sum(Sales_Value)/1000000, 1) as Sales_Value FROM ' + data_file_name + \
                  ' WHERE Province = \"' + province_selected + '\" GROUP BY City, Month ORDER BY Month'
        df_sales = pd.read_sql(con=conn, sql=sql_cmd)
        max_sales = math.ceil(df_sales.loc[:, 'Sales_Value'].max())
        # write in to dict
        dict_sales = {}
        for month_item in month_list:
            df_monthly_sales = df_sales.loc[df_sales['Month'] == month_item, ['City', 'Sales_Value']]
            monthly_sales_result = df_monthly_sales.values.tolist()
            dict_sales[month_item] = monthly_sales_result
        # draw chart
        self.draw_map_chart(dict_sales, max_sales, province_selected)

    def draw_map_chart(self, data_input, data_max, region):
        WarningType.ShowWarning = False
        month_list = list(data_input.keys())
        tl = Timeline(init_opts=opts.InitOpts(width="1200px", height="800px", theme=ThemeType.VINTAGE))
        for month_item in month_list:
            sales_data = data_input[month_item]
            if region != 'china':
                sales_data = [[item[0] + '市', item[1]] for item in sales_data]
            map0 = (
                Map()
                    .add(self.__class__.bu_name, sales_data, region)
                    .set_global_opts(
                    title_opts=opts.TitleOpts(title="%s销售数据(MM RMB) - %s" % (region, month_item)),
                    visualmap_opts=opts.VisualMapOpts(max_=data_max,
                                                      is_calculable=True,
                                                      range_color=["lightskyblue", "yellow", "orangered"],),
                )
            )
            tl.add(map0, "{}".format(month_item))
        chart_full_name = self.__class__.chart_path + "timeline_map.html"
        tl.render(chart_full_name)
        if platform.system() == "Linux":
            subprocess.call(["xdg-open", chart_full_name])
        else:
            os.startfile(chart_full_name)

    def generate_province_list(self):
        database_full_name = self.__class__.database_path + self.__class__.bu_name + '_Hospital_Sales.db'
        data_file_name = self.__class__.bu_name + '_Hospital_Sales'
        conn = sqlite3.connect(database_full_name)
        sql_cmd = 'SELECT DISTINCT(Province) FROM ' + data_file_name
        df = pd.read_sql(con=conn, sql=sql_cmd)
        province_list = [item[0] for item in df.values.tolist()]
        return province_list


if __name__ == '__main__':
    test = HospitalSalesCalculation('TU')
    test.generate_province_list()
