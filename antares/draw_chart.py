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


# draw all-in-one chart for code and h5 summary with matplotlib
def all_in_one_chart(name, final_month_list, inv_month_max, inv_month_gap, jnj_inv_month, lp_inv_month, sales_gts,
                     sales_lpsales, sales_ims, final_fcst_data):
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax1 = plt.subplots(figsize=(15, 4))
    color = 'tab:red'
    ind = np.arange(len(jnj_inv_month))
    width = 0.35
    rects1 = ax1.bar(ind - width / 2, jnj_inv_month, width, facecolor='w', edgecolor="r",
                     label="JNJ Inventory")
    rects2 = ax1.bar(ind + width / 2, lp_inv_month, width, facecolor='w', edgecolor="b",
                     label="LP Inventory")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Inventory (Months)")
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(np.arange(0, inv_month_max, step=inv_month_gap))
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel("Sales")
    ax2.plot(final_month_list, sales_gts, 'b-', linewidth=1.5, label="GTS")
    ax2.plot(final_month_list, sales_lpsales, 'g-.', linewidth=1.5, label="LP_Sales")
    ax2.plot(final_month_list, sales_ims, 'r--', linewidth=1.5, label="IMS")
    ax2.plot(final_month_list, final_fcst_data, 'c:', linewidth=1.5, label="Forecast")
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title("One-page Summary for " + name)
    plt.legend()

    # Add label on the chart
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            value = height
            if height == 0:
                value = ""
            ax1.annotate('{}'.format(value),
                         xy=(rect.get_x() + rect.get_width() / 2, height),
                         xytext=(0, 3),  # 3 points vertical offset
                         textcoords="offset points",
                         ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)
    fig.tight_layout()
    plt.show()


# draw all-in-one chart for code and h5 summary with echarts
def all_in_one_echart(name, final_month_list, jnj_inv_month, lp_inv_month, sales_gts, sales_lpsales, sales_ims,
                      final_fcst_data):
    sys_path = os.path.abspath('..')
    file_name = sys_path + "/data/_Charter/" + name.replace("/", "_") + "-all-in-one.html"
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.INFOGRAPHIC, width="1500px"))
        .add_xaxis(final_month_list)
        .add_yaxis("JNJ", jnj_inv_month)
        .add_yaxis("NED", lp_inv_month)
        .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} RMB")
            )
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(title_opts=opts.TitleOpts(title="All-in-one for " + name),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], )
    )
    line_gts = Line().add_xaxis(final_month_list).add_yaxis("GTS", sales_gts, yaxis_index=1)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_lpsales = Line().add_xaxis(final_month_list).add_yaxis("NED Sales", sales_lpsales, yaxis_index=1)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_ims = Line().add_xaxis(final_month_list).add_yaxis("IMS", sales_ims, yaxis_index=1)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    line_fcst = Line().add_xaxis(final_month_list).add_yaxis("Forecast", final_fcst_data, yaxis_index=1)\
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.overlap(line_gts)
    bar.overlap(line_lpsales)
    bar.overlap(line_ims)
    bar.overlap(line_fcst)
    bar.render(file_name)
    os.startfile(file_name)
    pass
