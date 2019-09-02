from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os


# draw line charter
def line_chart(code_name, x_value, y_value, x_label, y_label, chart_ttl):

    file_name = "../data/_Charter/" + code_name.replace(" ", "_") + ".html"
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
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
            title_opts=opts.TitleOpts(title=chart_ttl),)
    )
    c.render(file_name)
    os.system(file_name)


