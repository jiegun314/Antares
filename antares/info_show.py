import sqlite3
import time
import calculation
from tabulate import tabulate
import public_function as pb_func
import draw_chart as chart


class InfoShow:
    bu_name = ""
    user_name = ""

    def __init__(self, bu, name):
        self.__class__.bu_name = bu
        self.__class__.user_name = name

    def get_current_month(self):
        return time.strftime("%Y-%m", time.localtime())

    @staticmethod
    def show_command_list():
        pb_func.display_command_list("public_command")

    # 数据的表格化输出
    def format_output(self, data):
        print(tabulate(data, tablefmt="psql", headers="firstrow", floatfmt=",.0f"))

    # 显示单个代码销量数据
    def show_code_sales_data(self, month_number=12):
        # print title
        print("---- %sM Sales List for Single Code---" % month_number)
        material_code = input("Material code: ").upper()
        if not pb_func.check_code_availability(self.__class__.bu_name, material_code):
            print("!!ERROR, This code does NOT exist.")
            return
        else:
            # Get master data
            infocheck = calculation.InfoCheck(self.__class__.bu_name)
            mm_result = infocheck.get_master_data(material_code)
            print(mm_result[0][0], ": ", mm_result[1][0])
            self.display_code_sales_data(material_code, month_number)

    # display sales for single code
    def display_code_sales_data(self, material_code, month_number):
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        # generate month list
        date_list = infocheck.get_time_list(self.get_current_month(), 0 - month_number)
        sales_output = [["Month"] + date_list, ]
        # get sales data
        sale_type = ["GTS", "LPSales", "IMS"]
        for sales_item in sale_type:
            sales_output.append([sales_item] + infocheck.get_code_sales(sales_item, material_code, month_number))
        self.format_output(sales_output)

    # 显示单个代码历史库存量
    def show_code_hstr_inv(self, month_number=12):
        # Print title
        print("---- -Historical Inventory for Single Code---")
        material_code = input("Material code: ").upper()
        # 读取Master Data
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        if not pb_func.check_code_availability(self.__class__.bu_name, material_code):
            print("!!ERROR, This code does NOT exist.")
            return
        else:
            mm_result = infocheck.get_master_data(material_code)
            print(mm_result[0][0], ": ", mm_result[1][0])
            # Generate date list
            output = [["Month"] + infocheck.get_time_list(self.get_current_month(), 0-month_number)]
            jnj_inv_result = infocheck.get_code_jnj_inv(material_code)
            output.append(["JNJ"] + infocheck.data_mapping(jnj_inv_result, self.get_current_month(), 0-month_number))
            lp_inv_result = infocheck.get_code_lp_inv(material_code)
            output.append(["LP"] + infocheck.data_mapping(lp_inv_result, self.get_current_month(), 0-month_number))
            self.format_output(output)

    # 显示单个代码全部信息
    def show_code_all_info(self, month_number=12):
        # 打印标题
        print("---- Overall Information for Single Code---")
        material_code = input("Material code: ").upper()
        if not pb_func.check_code_availability(self.__class__.bu_name, material_code):
            print("!!ERROR, This code does NOT exist.")
            return
        else:
            infocheck = calculation.InfoCheck(self.__class__.bu_name)
            # get master_data
            print("======= <Detail Information> =======")
            master_data_result = infocheck.get_master_data(material_code)
            for i in range(len(master_data_result[0])):
                print(master_data_result[0][i], ": ", master_data_result[1][i])
            print("SAP_Price: ", infocheck.get_code_sap_price(material_code))
            print("GTIN: ", infocheck.get_code_gtin(material_code))
            # show Phoenix information
            if self.__class__.bu_name == "TU":
                print("======= <Phoenix Information> =======")
                phoenix_result = infocheck.get_code_phoenix_result(material_code)
                for i in range(0, len(phoenix_result[0])):
                    print(phoenix_result[0][i], " - ", phoenix_result[1][i])
            # show the RAG license information
            print("======= <License Information> =======")
            license_info = [["License", "Start", 'End']] + infocheck.get_code_rag(material_code)
            self.format_output(license_info)
            # 开始输出销售量
            print("--%s Months Historical Sales Data --" % month_number)
            output_sales = [["Month", ], ["GTS", ], ["LP Sales", ], ["IMS", ]]
            self.display_code_sales_data(material_code, month_number)
            # 开始输出库存历史量
            print("--%s Months Historical Inventory Data --" % month_number)
            output_inv = [["Month", ], ["JNJ_INV", ], ["JNJ_INV_Month", ], ["LP_INV", ], ["LP_INV_Month", ]]
            # 写入日期列表
            output_inv[0].extend(infocheck.get_time_list(self.get_current_month(), 0 - month_number))
            # 读取数据
            jnj_inv_result = infocheck.get_code_jnj_inv(material_code)
            output_inv[1].extend(infocheck.data_mapping(jnj_inv_result, self.get_current_month(), 0 - month_number))
            output_inv[2].extend(infocheck.get_inventory_month(output_inv[1][1:], output_sales[1][1:], month_number))
            lp_inv_result = infocheck.get_code_lp_inv(material_code)
            output_inv[3].extend(infocheck.data_mapping(lp_inv_result, self.get_current_month(), 0 - month_number))
            output_inv[4].extend(infocheck.get_inventory_month(output_inv[3][1:], output_sales[2][1:], month_number))
            self.format_output(output_inv)
            # 显示Statistical Forecast
            print("--Next 12 Months Statistical Forecast--")
            forecast_quantity = infocheck.get_code_forecast(material_code, "Statistical", 12)
            if forecast_quantity != "Fail":
                self.format_output(forecast_quantity)
            # 显示Final Forecast
            print("--Next 12 Months Final Forecast--")
            forecast_quantity = infocheck.get_code_forecast(material_code, "Final", 12)
            if forecast_quantity != "Fail":
                self.format_output(forecast_quantity)
            # 显示ESO
            self.display_material_eso(material_code, "code")
            print("-----------END-----------")

    # get hierarchy_5 name
    def get_h5_name(self):
        h5_input = input("Please input Hierarchy_5 name: ")
        h5_name = "ALL" if h5_input.upper() == "ALL" else pb_func.get_available_h5_name(h5_input, self.__class__.bu_name)
        return h5_name

    # get sales data for one Hierarchy_5
    def get_h5_sales_data(self, h5_name, month_number):
        h5_info_check = calculation.InfoCheck(self.__class__.bu_name)
        print("====================================================================")
        print("--24 Month Historical Sales Data for %s--" % h5_name)
        price_type = ("Standard_Cost", "SAP_Price")
        sales_type = ("GTS", "LPSales", "IMS")
        for price_item in price_type:
            # Print price title
            print("-With %s-" % price_item)
            # Add Month list
            h5_sales_result = [["Month", ] + h5_info_check.get_time_list(self.get_current_month(), 0 - month_number)]
            # get data
            for sales_item in sales_type:
                h5_temp = h5_info_check.get_h5_sales_data(sales_item, price_item, h5_name, month_number)
                h5_sales_result.append([sales_item, ] + h5_temp)
            self.format_output(h5_sales_result)

    # show sales data for one Hierarchy_5
    def show_h5_sales_data(self, month_number=12):
        h5_name = self.get_h5_name()
        if h5_name != "NULL":
            self.get_h5_sales_data(h5_name, month_number)
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # get inventory data for one Hierarchy_5:
    def get_h5_inventory(self, h5_name, month_number):
        h5_info_check = calculation.InfoCheck(self.__class__.bu_name)
        # Print title
        print("====================================================================")
        print("--%s Month Historical Inventory for %s (RMB)--" % (month_number, h5_name))
        # price_type = ("Standard_Cost", "SAP_Price")
        inv_type = ("JNJ", "LP")
        # Generate column name of month list
        month_list = ["Month"] + h5_info_check.get_time_list(self.get_current_month(), 0 - month_number)
        # print with Standard Cost
        print("-With Standard_Cost-")
        h5_inv_result = [month_list, ]
        for inv_item in inv_type:
            h5_inv_temp = h5_info_check.get_h5_inventory_data(inv_item, "Standard_Cost", h5_name)
            h5_inv_output = h5_info_check.data_mapping(h5_inv_temp, self.get_current_month(), 0 - month_number)
            h5_inv_result.append([inv_item] + h5_inv_output)
        self.format_output(h5_inv_result)
        # print with SAP Price
        print("-With SAP Price-")
        h5_inv_result = [month_list, ]
        # get sales data
        h5_gts_result = h5_info_check.get_h5_sales_data("GTS", "SAP_Price", h5_name, month_number)
        h5_lpsales_result = h5_info_check.get_h5_sales_data("LPSales", "SAP_Price", h5_name, month_number)
        # generate inventory value and inventory month
        # generate JNJ inventory
        h5_inv_temp = h5_info_check.get_h5_inventory_data("JNJ", "SAP_Price", h5_name)
        h5_inv_output = h5_info_check.data_mapping(h5_inv_temp, self.get_current_month(), 0 - month_number)
        h5_inv_result.append(["JNJ", ] + h5_inv_output)
        h5_inv_result.append(
            ["JNJ_Month", ] + h5_info_check.get_inventory_month(h5_inv_output, h5_gts_result, month_number))
        # generate LP inventory
        h5_inv_temp = h5_info_check.get_h5_inventory_data("LP", "SAP_Price", h5_name)
        h5_inv_output = h5_info_check.data_mapping(h5_inv_temp, self.get_current_month(), 0 - month_number)
        h5_inv_result.append(["LP", ] + h5_inv_output)
        h5_inv_result.append(
            ["LP_Month", ] + h5_info_check.get_inventory_month(h5_inv_output, h5_lpsales_result, month_number))
        self.format_output(h5_inv_result)

    def show_h5_inventory(self, month_number=12):
        h5_name = self.get_h5_name()
        if h5_name != "NULL":
            self.get_h5_inventory(h5_name, month_number)
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # display forecast for one Hierarchy_5
    def show_h5_forecast(self, h5_name, fcst_type, month_quntity=12):
        print("== %s Forecast for %s ==" % (fcst_type, h5_name))
        forecast_calculation = calculation.InfoCheck(self.__class__.bu_name)
        month_list = forecast_calculation.get_time_list(self.get_current_month(), month_quntity)
        forecast_result = forecast_calculation.get_h5_forecast(h5_name, fcst_type, month_quntity)
        self.format_output([["Month", ] + month_list, ["Value (SAP Price)", ] + forecast_result])
        pass

    # Show all information of one Hierarchy_5
    def show_h5_all_info(self, month_number=12, forecast_month=12):
        h5_name = self.get_h5_name()
        if h5_name != "NULL":
            self.get_h5_sales_data(h5_name, month_number)
            self.get_h5_inventory(h5_name, month_number)
            self.show_h5_forecast(h5_name, "Statistical", forecast_month)
            self.show_h5_forecast(h5_name, "Final", forecast_month)
            self.display_material_eso(h5_name, "h5")
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # 显示单个代码的ESO
    def show_code_eso(self):
        code_name = input("Input Material Code: ").upper()
        self.display_material_eso(code_name, eso_type="code")

    # display eso for single code
    def display_material_eso(self, material_code, eso_type):
        info_check = calculation.InfoCheck(self.__class__.bu_name)
        eso_result = info_check.get_material_eso(material_code, eso_type)
        if eso_type == "code":
            eso_output = [["Cycle", ], ["E_Qty", ], ["SM_Qty", ], ["O_Qty", ], ["ESO_Qty", ], ["ESO_Value_Std_Cost", ],
                           ["ESO_Value_SAP_Price", ]]
        else:
            eso_output = [["Cycle", ], ["ESO_Value_Std_Cost", ], ["ESO_Value_SAP_Price", ]]
        for item in eso_result:
            for index in range(0, len(eso_output)):
                eso_output[index].append(item[index])
        print(tabulate(eso_output, tablefmt="psql", headers="firstrow", floatfmt=",.0f"))

    # 显示单个代码的综合图表
    def show_code_chart(self):
        print("==Single Code General Chart==")
        material_code = input("Material code: ").upper()
        # 验证代码是否存在
        if not pb_func.check_code_availability(self.__class__.bu_name, material_code):
            print("!! This code does no exist, please try again.")
            return
        # 读取销量数据
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        sales_list = ("GTS", "LPSales", "IMS")
        sales_output = []
        for index in range(0, 3):
            sales_output.append(infocheck.get_code_sales(sales_list[index], material_code, 24))
        # 读取final forecast
        code_forecast = infocheck.get_code_forecast(material_code, "Final", 12)[1]
        # 读取库存数据
        inventory_result = infocheck.get_code_jnj_inv(material_code)
        historical_jnj_inv = infocheck.data_mapping(inventory_result, self.get_current_month(), -24)
        inventory_result = infocheck.get_code_lp_inv(material_code)
        historical_lp_inv = infocheck.data_mapping(inventory_result, self.get_current_month(), -24)
        historical_inv = [historical_jnj_inv, historical_lp_inv]
        self.draw_sales_inv_fcst_chart(material_code, sales_output, historical_inv, code_forecast, 12, "code")

    # 显示H5的综合图表
    def show_h5_chart(self):
        # 打印标题
        print("==Hierarchy_5 General Chart==")
        h5_name = self.get_h5_name()
        if h5_name == "NULL":
            return
        h5_info_check = calculation.InfoCheck(self.__class__.bu_name)
        # 读取数据
        # 读取历史销量
        sales_type = ("GTS", "LPSales", "IMS")
        h5_sales_result = []
        for sales_item in sales_type:
            h5_sales_result.append(h5_info_check.get_h5_sales_data(sales_item, "SAP_Price", h5_name, 24))
        # 读取库存量
        inv_type = ("JNJ", "LP")
        h5_inv_result = []
        for inv_item in inv_type:
            h5_temp = h5_info_check.get_h5_inventory_data(inv_item, "SAP_Price", h5_name)
            h5_inv_result.append(h5_info_check.data_mapping(h5_temp, self.get_current_month(), -24))
        # 读取final forecast
        h5_forecast = h5_info_check.get_h5_forecast(h5_name, "Final", 12)
        # Generate the chart with 12 months forecast
        self.draw_sales_inv_fcst_chart(h5_name, h5_sales_result, h5_inv_result, h5_forecast, 12, "h5")
        pass

    # 画综合图
    def draw_sales_inv_fcst_chart(self, name, sales_data, inv_data, fcst_data, fcst_month, data_type):
        # get integer format of all sales data
        sales_gts = list(map(int, sales_data[0]))
        sales_lpsales = list(map(int, sales_data[1]))
        sales_ims = list(map(int, sales_data[2]))
        jnj_inv, lp_inv = inv_data
        # set blank and zero list
        lst_blank, lst_zero = [], []
        for index in range(0, 12):
            lst_blank.append(None)
            lst_zero.append(0)
        # get inventory month
        jnj_inv_month = calculation.InfoCheck.get_inventory_month(jnj_inv, sales_gts, 24, blank_type=1)
        lp_inv_month = calculation.InfoCheck.get_inventory_month(lp_inv, sales_lpsales, 24, blank_type=1)
        # fulfill sales and inventory data with blank in future 12 months
        sales_gts.extend(lst_blank)
        sales_lpsales.extend(lst_blank)
        sales_ims.extend(lst_blank)
        jnj_inv_month.extend(lst_blank)
        lp_inv_month.extend(lst_blank)
        # fulfill forecast data with blank in historical 24 months
        final_fcst_data = lst_blank + lst_blank + fcst_data
        # link fcst data with gts
        final_fcst_data[23] = sales_gts[23]
        # start to generate chart
        # generate full month list
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        historical_month_list = infocheck.get_time_list(self.get_current_month(), -24)
        final_month_list = historical_month_list + infocheck.get_time_list(self.get_current_month(), fcst_month)
        # draw the chart
        chart.all_in_one_echart(name, final_month_list, jnj_inv_month, lp_inv_month, sales_gts, sales_lpsales,
                                sales_ims, final_fcst_data, data_type)
        print("--The chart is generated, you can also find it under ../data/_Charter --")


if __name__ == "__main__":
    test = InfoShow("TU", "Jeffrey")
    test.show_code_sales_data()