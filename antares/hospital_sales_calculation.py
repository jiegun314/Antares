import pandas as pd
import sqlite3
from pyecharts import options as opts
from pyecharts.charts import Timeline, Grid, Bar, Map, Pie, Line
from pyecharts.globals import WarningType
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from typing import List
import math
import platform
import subprocess
import numpy as np
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

    # get data list for AIO chart
    def get_data_for_AIO_chart(self):
        database_full_name = self.__class__.database_path + self.__class__.bu_name + '_Hospital_Sales.db'
        data_file_name = self.__class__.bu_name + '_Hospital_Sales'
        conn = sqlite3.connect(database_full_name)
        sql_cmd = 'SELECT Month, Province, round(sum(Sales_Value),0) as Sales_Value FROM ' + data_file_name + \
                  ' GROUP BY Month, Province Order by Month, Sales_Value DESC'
        df_sales_result = pd.read_sql(con=conn, sql=sql_cmd)
        # get month_list
        month_list = df_sales_result['Month'].unique().tolist()
        list_final_data = []
        for month_item in month_list:
            df_monthly_sales = df_sales_result.loc[df_sales_result['Month'] == month_item, ['Province', 'Sales_Value']]
            df_monthly_sales['Ratio'] = df_monthly_sales['Sales_Value'] / df_monthly_sales['Sales_Value'].sum() * 100
            list_monthly_sales = df_monthly_sales.values.tolist()
            # generate dict for final data
            list_value = []
            for item_monthly_sales in list_monthly_sales:
                [item_province, item_sales_value, item_ratio] = item_monthly_sales
                list_value.append({"name": item_province, "value": [item_sales_value, item_ratio, item_province]})
            list_final_data.append({'time': month_item, 'data': list_value})
        # get monthly ttl IMS (in MM RMB)
        df_monthly_ttl = df_sales_result.pivot_table(index='Month', values='Sales_Value', aggfunc=np.sum)
        list_monthly_ttl = [round(item[0]/1000000,2) for item in df_monthly_ttl.values.tolist()]
        # get min and max
        minNum, maxNum = df_sales_result['Sales_Value'].min(), df_sales_result['Sales_Value'].max()
        return [month_list, list_final_data, list_monthly_ttl, minNum, maxNum]

    # generate AIO chart
    def get_year_chart(self, year, data, time_list, total_num, maxNum, minNum):
        map_data = [
            [[x["name"], x["value"]] for x in d["data"]] for d in data if d["time"] == year
        ][0]
        min_data, max_data = (minNum, maxNum)
        data_mark: List = []
        i = 0
        for x in time_list:
            if x == year:
                data_mark.append(total_num[i])
            else:
                data_mark.append("")
            i = i + 1

        map_chart = (
            Map()
                .add(
                series_name="",
                data_pair=map_data,
                zoom=1,
                center=[119.5, 34.5],
                is_map_symbol_show=False,
                itemstyle_opts={
                    "normal": {"areaColor": "#323c48", "borderColor": "#404a59"},
                    "emphasis": {
                        "label": {"show": Timeline},
                        "areaColor": "rgba(255,255,255, 0.5)",
                    },
                },
            )
                .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="All-in-One Chart of IMS Distribution - " + str(year),
                    subtitle="",
                    pos_left="center",
                    pos_top="top",
                    title_textstyle_opts=opts.TextStyleOpts(
                        font_size=25, color="rgba(255,255,255, 0.9)"
                    ),
                ),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True,
                    formatter=JsCode(
                        """function(params) {
                        if ('value' in params.data) {
                            return params.data.value[2] + ': ' + params.data.value[0];
                        }
                    }"""
                    ),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_calculable=True,
                    dimension=0,
                    pos_left="30",
                    pos_top="center",
                    range_text=["High", "Low"],
                    range_color=["lightskyblue", "yellow", "orangered"],
                    textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                    min_=min_data,
                    max_=max_data,
                ),
            )
        )

        line_chart = (
            Line()
                .add_xaxis(time_list)
                .add_yaxis("", total_num)
                .add_yaxis(
                "",
                data_mark,
                markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
            )
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Monthly IMS Total Value (MM RMB)", pos_left="72%", pos_top="5%"
                )
            )
        )
        bar_x_data = [x[0] for x in map_data]
        bar_y_data = [{"name": x[0], "value": x[1][0]} for x in map_data]
        bar = (
            Bar()
                .add_xaxis(xaxis_data=bar_x_data)
                .add_yaxis(
                series_name="",
                y_axis=bar_y_data,
                label_opts=opts.LabelOpts(
                    is_show=True, position="right", formatter="{b} : {c}"
                ),
            )
                .reversal_axis()
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    max_=maxNum, axislabel_opts=opts.LabelOpts(is_show=False)
                ),
                yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(is_show=False)),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                visualmap_opts=opts.VisualMapOpts(
                    is_calculable=True,
                    dimension=0,
                    pos_left="10",
                    pos_top="top",
                    range_text=["High", "Low"],
                    range_color=["lightskyblue", "yellow", "orangered"],
                    textstyle_opts=opts.TextStyleOpts(color="#ddd"),
                    min_=min_data,
                    max_=max_data,
                ),
            )
        )

        pie_data = [[x[0], x[1][0]] for x in map_data]
        pie = (
            Pie()
                .add(
                series_name="",
                data_pair=pie_data,
                radius=["15%", "35%"],
                center=["80%", "82%"],
                itemstyle_opts=opts.ItemStyleOpts(
                    border_width=1, border_color="rgba(0,0,0,0.3)"
                ),
            )
                .set_global_opts(
                tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b} {d}%"),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )

        grid_chart = (
            Grid()
                .add(
                bar,
                grid_opts=opts.GridOpts(
                    pos_left="10", pos_right="45%", pos_top="50%", pos_bottom="5"
                ),
            )
                .add(
                line_chart,
                grid_opts=opts.GridOpts(
                    pos_left="65%", pos_right="80", pos_top="10%", pos_bottom="50%"
                ),
            )
                .add(pie, grid_opts=opts.GridOpts(pos_left="45%", pos_top="60%"))
                .add(map_chart, grid_opts=opts.GridOpts())
        )

        return grid_chart

    def start_generate_AIO_chart(self):
        [time_list, data, total_num, minNum, maxNum] = self.get_data_for_AIO_chart()
        timeline = Timeline(
            init_opts=opts.InitOpts(width="1600px", height="900px", theme=ThemeType.PURPLE_PASSION)
        )
        for y in time_list:
            g = self.get_year_chart(y, data, time_list, total_num, maxNum, minNum)
            timeline.add(g, time_point=str(y))

        timeline.add_schema(
            orient="vertical",
            is_auto_play=True,
            is_inverse=True,
            play_interval=5000,
            pos_left="null",
            pos_right="5",
            pos_top="20",
            pos_bottom="20",
            width="60",
            label_opts=opts.LabelOpts(is_show=True, color="#fff"),
        )
        chart_full_name = self.__class__.chart_path + "AIO.html"
        timeline.render(chart_full_name)
        if platform.system() == "Linux":
            subprocess.call(["xdg-open", chart_full_name])
        else:
            os.startfile(chart_full_name)
        pass


if __name__ == '__main__':
    test = HospitalSalesCalculation('TU')
    test.start_generate_AIO_chart()