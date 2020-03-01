from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os


# draw line charter
def line_chart(code_name, x_value, y_value, x_label, y_label, chart_ttl):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + code_name.replace(" ", "_") + ".html"
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.CHALK, width="1500px"))
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
    os.system(file_name)


# draw stack bar chart for backorder daily trend
def backorder_trend_chart(date_list, backorder_value):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/Backorder_trend.html"
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis("ND", backorder_value[2], stack="stack1")
        .add_yaxis("ROP", backorder_value[1], stack="stack1")
        .add_yaxis("IND", backorder_value[0], stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title="Backorder trend (Value in RMB)"),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    os.system(file_name)


# draw stack bar chart for pending inventory trend
def pending_inventory_trend_chart(date_list, pending_inventory_data, title_name):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/pending_inventory_trend.html"
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis("Nonbonded", pending_inventory_data[1], stack="stack1")
        .add_yaxis("Bonded", pending_inventory_data[0], stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title=title_name),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    os.system(file_name)
