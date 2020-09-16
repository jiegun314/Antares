from pyecharts.charts import Line
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.globals import WarningType
import platform
import subprocess
import os


# draw line charter
def line_chart(code_name, x_value, y_value, x_label, y_label, chart_ttl):
    WarningType.ShowWarning = False
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
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                is_scale=True),
            title_opts=opts.TitleOpts(title=chart_ttl),
            toolbox_opts=opts.ToolboxOpts(),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)


# draw line charter
def double_line_chart(material_name, x_value, y1_value, y2_value, x_label, y1_label, y2_label, chart_ttl, y_index=1):
    WarningType.ShowWarning = False
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + material_name.replace(" ", "_").replace("/", "_") + ".html"
    line_qty = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width="1500px"))
        .add_xaxis(x_value)
        .add_yaxis(y1_label, y1_value, is_smooth=True)
        .add_yaxis(y2_label, y2_value, yaxis_index=y_index, is_smooth=True)
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            xaxis_opts=opts.AxisOpts(name=x_label),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                is_scale=True),
            title_opts=opts.TitleOpts(title=chart_ttl),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="line"),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], )
        .extend_axis(
            yaxis=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                is_scale=True
            )
        )
    )
    line_qty.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)


# draw stack bar chart for backorder daily trend
def backorder_trend_chart(date_list, backorder_value):
    WarningType.ShowWarning = False
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
                         toolbox_opts=opts.ToolboxOpts(),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)


# draw stack bar chart for backorder daily trend
def backorder_trend_line_chart(date_list, backorder_value, bu_name):
    WarningType.ShowWarning = False
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + bu_name + "_Backorder_trend.html"
    chart_title = "Backorder Trend of " + bu_name + " (Value in RMB)"
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis(
            series_name="ND",
            stack="总量",
            y_axis=backorder_value[2],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="ROP",
            stack="总量",
            y_axis=backorder_value[1],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="IND",
            stack="总量",
            y_axis=backorder_value[0],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=True, position="top"),
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=chart_title),
            toolbox_opts=opts.ToolboxOpts(),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
        )
    )
    c.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)


# draw stack bar chart for pending inventory trend
def pending_inventory_trend_chart(date_list, pending_inventory_data, title_name):
    WarningType.ShowWarning = False
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/pending_inventory_trend.html"
    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.ROMA, width="1500px"))
        .add_xaxis(date_list)
        .add_yaxis("Nonbonded", pending_inventory_data[1], stack="stack1")
        .add_yaxis("Bonded", pending_inventory_data[0], stack="stack1")
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(title_opts=opts.TitleOpts(title=title_name),
                         toolbox_opts=opts.ToolboxOpts(),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],)
    )
    c.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)


# draw all-in-one chart for code and h5 summary with echarts
def all_in_one_echart(name, final_month_list, jnj_inv_month, lp_inv_month, sales_gts, sales_lpsales, sales_ims,
                      final_fcst_data, data_type):
    WarningType.ShowWarning = False
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + name.replace("/", "_") + "-all-in-one.html"
    sales_unit = "PC" if data_type == "code" else "RMB"
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS, width="1500px", height="800px"))
        .add_xaxis(final_month_list)
        .add_yaxis("JNJ", jnj_inv_month, itemstyle_opts=opts.AreaStyleOpts(opacity=0.5))
        .add_yaxis("NED", lp_inv_month, itemstyle_opts=opts.AreaStyleOpts(opacity=0.5))
        .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} " + sales_unit)
            )
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(title_opts=opts.TitleOpts(title="All-in-one for " + name),
                         toolbox_opts=opts.ToolboxOpts(),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], )
    )
    line_gts = Line().add_xaxis(final_month_list).add_yaxis("GTS", sales_gts, yaxis_index=1, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3))\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_lpsales = Line().add_xaxis(final_month_list).add_yaxis("NED Sales", sales_lpsales, yaxis_index=1, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3))\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_ims = Line().add_xaxis(final_month_list).add_yaxis("IMS", sales_ims, yaxis_index=1, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3))\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_fcst = Line().add_xaxis(final_month_list).add_yaxis("Forecast", final_fcst_data, yaxis_index=1, is_smooth=True, linestyle_opts=opts.LineStyleOpts(width=3))\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.overlap(line_gts)
    bar.overlap(line_lpsales)
    bar.overlap(line_ims)
    bar.overlap(line_fcst)
    bar.render(file_name)
    if platform.system() == "Linux":
        subprocess.call(["xdg-open", file_name])
    else:
        os.startfile(file_name)

