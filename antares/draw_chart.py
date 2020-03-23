from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os


# draw line charter
def line_chart(code_name, x_value, y_value, x_label, y_label, chart_ttl):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + code_name.replace(" ", "_").replace("/", "_") + ".html"
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width="1500px"))
        .add_xaxis(x_value)
        .add_yaxis(y_label, y_value, is_smooth=True)
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name=x_label),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                is_scale=True),
            title_opts=opts.TitleOpts(title=chart_ttl),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    os.startfile(file_name)


# draw stack bar chart for backorder daily trend
def backorder_trend_chart(date_list, backorder_value):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/Backorder_trend.html"
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis("ND", backorder_value[2], stack="stack1")
        .add_yaxis("ROP", backorder_value[1], stack="stack1")
        .add_yaxis("IND", backorder_value[0], stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Backorder trend (Value in RMB)"),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    os.startfile(file_name)


# draw stack bar chart for pending inventory trend
def pending_inventory_trend_chart(date_list, pending_inventory_data, title_name):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/pending_inventory_trend.html"
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis("Nonbonded", pending_inventory_data[1], stack="stack1")
        .add_yaxis("Bonded", pending_inventory_data[0], stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title=title_name),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    os.startfile(file_name)


# draw all-in-one chart for code and h5 summary with echarts
def all_in_one_echart(name, final_month_list, jnj_inv_month, lp_inv_month, sales_gts, sales_lpsales, sales_ims,
                      final_fcst_data, data_type):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + name.replace("/", "_") + "-all-in-one.html"
    sales_unit = "PC" if data_type == "code" else "RMB"
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="1500px"))
        .add_xaxis(final_month_list)
        .add_yaxis("JNJ", jnj_inv_month)
        .add_yaxis("NED", lp_inv_month)
        .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} " + sales_unit)
            )
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(title_opts=opts.TitleOpts(title="All-in-one for " + name),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], )
    )
    line_gts = Line().add_xaxis(final_month_list).add_yaxis("GTS", sales_gts, yaxis_index=1, is_smooth=True)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_lpsales = Line().add_xaxis(final_month_list).add_yaxis("NED Sales", sales_lpsales, yaxis_index=1, is_smooth=True)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_ims = Line().add_xaxis(final_month_list).add_yaxis("IMS", sales_ims, yaxis_index=1, is_smooth=True)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_fcst = Line().add_xaxis(final_month_list).add_yaxis("Forecast", final_fcst_data, yaxis_index=1, is_smooth=True)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.overlap(line_gts)
    bar.overlap(line_lpsales)
    bar.overlap(line_ims)
    bar.overlap(line_fcst)
    bar.render(file_name)
    os.startfile(file_name)
    pass