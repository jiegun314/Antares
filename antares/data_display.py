import json
import sqlite3
import time
import calculation
from tabulate import tabulate
import public_function as pb_func
import draw_chart as chart
from prettytable import PrettyTable


class DataDisplay:
    bu_name = ""
    user_name = ""

    def __init__(self, bu, name):
        self.__class__.bu_name = bu
        self.__class__.user_name = name

    @staticmethod
    def get_current_month():
        return time.strftime("%Y-%m", time.localtime())

    @staticmethod
    # Add Index column to a 2 dimension table
    def add_table_index(lst_data, lst_index):
        for i in range(len(lst_data)):
            lst_data[i].insert(0, lst_index[i])
        return lst_data

    @staticmethod
    def show_command_list():
        pb_func.display_command_list("public_command")

    @staticmethod
    def format_output(lst_data_input):
        print(tabulate(lst_data_input, tablefmt="psql", headers="firstrow", floatfmt=",.0f"))

    @staticmethod
    def pretty_output(lst_data_input):
        x = PrettyTable()
        x.field_names = lst_data_input.pop(0)
        for item in lst_data_input:
            x.add_row(item)
        print(x)

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
            mm_result = infocheck.get_single_code_all_master_data(material_code, ['Description'])[0]
            print(material_code, ": ", mm_result)
            self.format_output(self.list_code_sales_data(material_code, month_number))

    # 显示单个代码历史库存量
    def show_code_historical_inventory(self, month_number=12):
        # Print title
        print("---- -Historical Inventory for Single Code---")
        material_code = input("Material code: ").upper()
        # 读取Master Data
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        if not pb_func.check_code_availability(self.__class__.bu_name, material_code):
            print("!!ERROR, This code does NOT exist.")
            return
        else:
            mm_result = infocheck.get_single_code_all_master_data(material_code, ['Description'])[0]
            print(material_code, ": ", mm_result)
            # Generate date list
            self.format_output(self.list_code_historical_inventory(material_code, month_number))

    # get hierarchy_5 name
    def get_h5_name(self):
        h5_input = input("Please input Hierarchy_5 name: ")
        h5_name = "ALL" if h5_input.upper() == "ALL" else pb_func.get_available_h5_name(h5_input, self.__class__.bu_name)
        return h5_name

    # display forecast for one Hierarchy_5
    def show_h5_forecast(self, h5_name, fcst_type, month_quantity=12):
        print("== %s Forecast for %s ==" % (fcst_type, h5_name))
        forecast_calculation = calculation.InfoCheck(self.__class__.bu_name)
        month_list = forecast_calculation.get_time_list(self.get_current_month(), month_quantity)
        forecast_result = forecast_calculation.get_h5_forecast(h5_name, fcst_type, month_quantity)
        forecast_output = pb_func.add_table_index([month_list, forecast_result], ["Month", "Value (SAP Price)"])
        self.format_output(forecast_output)
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


class CodeDataDisplay(DataDisplay):

    def __init__(self, bu_input, name_input):
        super(CodeDataDisplay, self).__init__(bu_input, name_input)

    # List all detail information by code
    def show_code_all_info(self, code_input='', month_number=12):
        material_code = code_input if code_input else input("Material code: ").strip().upper()
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        master_data_list = ['Material', 'Description', 'Chinese_Description', 'Hierarchy_4', 'Hierarchy_5',
                            'Sales_Status', 'Purchase_Status', 'Standard_Cost', 'SAP_Price', 'Ranking', 'MRP_Type',
                            'Reorder_Point', 'Phoenix_Status', 'Phoenix_Discontinuation_Date',
                            'Phoenix_Obsolescence_Date', 'GTIN', 'RAG']
        master_data_result = infocheck.get_single_code_all_master_data(material_code, master_data_list)
        if master_data_result:
            # get the RAG information
            master_data_list.pop()
            rag_result = json.loads(master_data_result.pop())
            lst_final_master_data = [[master_data_list[i], master_data_result[i]] for i in range(len(master_data_result))]
            print("======= <Detail Information> =======")
            self.format_output(lst_final_master_data)
            print("---- <RAG Information> ----")
            for j in range(len(rag_result)):
                print(rag_result[str(j + 1)]['REGLICNO'], " - ", rag_result[str(j + 1)]['REGAPDATE'], " - ",
                      rag_result[str(j + 1)]['REGEXDATE'], " - ", rag_result[str(j + 1)]['LIFEYEAR'])
            print("======= <Sales & Inventory Information> =======")
            # 开始输出销售量
            print("--%s Months Historical Sales Data --" % month_number)
            self.format_output(self.list_code_sales_data(material_code, month_number))
            # 开始输出库存历史量
            print("--%s Months Historical Inventory Data --" % month_number)
            self.format_output(self.list_code_historical_inventory(material_code, month_number))
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
            print("==  ESO Trend of %s  ==" % material_code)
            eso_result = infocheck.get_material_eso(material_code)
            if eso_result:
                self.format_output(eso_result)
            else:
                pass
            # print EOF
            print("-----------END-----------")
        else:
            print("!! Error. This code does not exist.")

    # display sales for single code
    def list_code_sales_data(self, material_code, month_number) -> list:
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        # generate month list
        sales_title = ["Month", "GTS", "LPSales", "IMS"]
        sales_output = [infocheck.get_time_list(self.get_current_month(), 0 - month_number)]
        # get sales data
        sale_type = ["GTS", "LPSales", "IMS"]
        for sales_item in sale_type:
            sales_output.append(infocheck.get_code_sales(sales_item, material_code, month_number))
        return self.add_table_index(sales_output, sales_title)

    # generate code level historical inventory quantity and month
    def list_code_historical_inventory(self, material_code, month_number) -> list:
        infocheck = calculation.InfoCheck(self.__class__.bu_name)
        month_list = infocheck.get_time_list(self.get_current_month(), 0-month_number)
        jnj_inventory_quantity = infocheck.get_code_inventory(material_code, "JNJ", month_number)
        lp_inventory_quantity = infocheck.get_code_inventory(material_code, "LP", month_number)
        gts_quantity = infocheck.get_code_sales("GTS", material_code, month_number)
        lpsales_quantity = infocheck.get_code_sales("LPSales", material_code, month_number)
        jnj_inventory_month = infocheck.get_inventory_month(jnj_inventory_quantity, gts_quantity, month_number)
        lp_inventory_month = infocheck.get_inventory_month(lp_inventory_quantity, lpsales_quantity, month_number)
        inventory_output = [month_list, jnj_inventory_quantity, jnj_inventory_month, lp_inventory_quantity,
                            lp_inventory_month]
        inventory_title = ["Month", "JNJ_INV", "JNJ_INV_Mth", "LP_INV", "LP_INV_Mth"]
        return self.add_table_index(inventory_output, inventory_title)

    # show All-in-One chart for code level
    def show_code_chart(self, code_input=''):
        print("-- The chart would be opened in your browser --")
        material_code = code_input if code_input else input("Material code: ").upper()
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
        historical_jnj_inv = infocheck.get_code_inventory(material_code, "JNJ", 24)
        historical_lp_inv = infocheck.get_code_inventory(material_code, "LP", 24)
        historical_inv = [historical_jnj_inv, historical_lp_inv]
        self.draw_sales_inv_fcst_chart(material_code, sales_output, historical_inv, code_forecast, 12, "code")


class HierarchyDataDisplay(DataDisplay):

    def __init__(self, bu_input, name_input):
        super(HierarchyDataDisplay, self).__init__(bu_input, name_input)

    # Show all information of one Hierarchy_5
    def show_h5_all_info(self, h5_name_input='', month_number=12, forecast_month=12):
        h5_name = "ALL" if h5_name_input.upper() == "ALL" \
            else pb_func.get_available_h5_name(h5_name_input, self.__class__.bu_name)
        if h5_name != "NULL":
            self.show_h5_sales_data(h5_name, month_number)
            self.show_h5_inventory(h5_name, month_number)
            self.show_h5_forecast(h5_name, "Statistical", forecast_month)
            self.show_h5_forecast(h5_name, "Final", forecast_month)
            self.display_hierarchy_level_eso(h5_name)
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # show eso result in hierarchy level
    def display_hierarchy_level_eso(self, h5_name):
        print("==  ESO Trend of %s  ==" % h5_name)
        info_check = calculation.InfoCheck(self.__class__.bu_name)
        eso_result = info_check.get_hierarchy_eso_value(h5_name, cycle_qty=8)
        self.format_output(eso_result)

    # show sales data for one Hierarchy_5
    def show_h5_sales_data(self, h5_name_input='', month_number=12):
        h5_name = h5_name_input if h5_name_input else self.get_h5_name()
        if h5_name != "NULL":
            print("== %s Month Historical Sales Data for %s ==" % (month_number, h5_name))
            sales_title = ["Month", "GTS", "LPSales", "IMS"]
            price_type = ['Standard_Cost', 'SAP_Price']
            for price_item in price_type:
                # Print price title
                print("-With %s-" % price_item)
                sales_result = self.get_h5_sales_data(h5_name, month_number, price_item)
                self.format_output(self.add_table_index(sales_result, sales_title))
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # get sales data for one Hierarchy_5
    def get_h5_sales_data(self, h5_name, month_number, price_item) -> list:
        h5_info_check = calculation.InfoCheck(self.__class__.bu_name)
        sales_type = ["GTS", "LPSales", "IMS"]
        # Add Month list
        h5_sales_result = [h5_info_check.get_time_list(self.get_current_month(), 0 - month_number)]
        # get data
        for sales_item in sales_type:
            h5_sales_result.append(h5_info_check.get_h5_sales_data(sales_item, price_item, h5_name, month_number))
        return h5_sales_result

    # get inventory data for one Hierarchy_5:
    def get_h5_inventory(self, h5_name, month_number, price_type) -> list:
        h5_info_check = calculation.InfoCheck(self.__class__.bu_name)
        h5_inv_result = [h5_info_check.get_time_list(self.get_current_month(), 0 - month_number)]
        inv_parameter = [["JNJ", "GTS"], ["LP", "LPSales"]]
        for para_item in inv_parameter:
            [inv_type, sale_type] = para_item
            # get sales data
            h5_sales_result = h5_info_check.get_h5_sales_data(sale_type, price_type, h5_name, month_number)
            # generate inventory value and inventory month
            h5_inv_output = h5_info_check.get_h5_inventory_data(inv_type, price_type, h5_name, month_number)
            h5_inv_month = h5_info_check.get_inventory_month(h5_inv_output, h5_sales_result, month_number)
            h5_inv_result.extend([h5_inv_output, h5_inv_month])
        return h5_inv_result

    def show_h5_inventory(self, h5_name_input='', month_number=12):
        h5_name = h5_name_input if h5_name_input else self.get_h5_name()
        if h5_name != "NULL":
            # Print title
            print("== %s Month Historical Inventory for %s (RMB) ==" % (month_number, h5_name))
            lst_price_type = ['Standard_Cost', 'SAP_Price']
            inv_title = ["Month", "JNJ", "JNJ_Mth", "LP", "LP_Mth"]
            for price_type in lst_price_type:
                print("- With %s -" % price_type)
                h5_inv_result = self.get_h5_inventory(h5_name, month_number, price_type)
                self.format_output(self.add_table_index(h5_inv_result, inv_title))
        else:
            print("!!Error, Wrong Hierarchy_5 Name, Please Check!")

    # draw chart of h5 all information
    def show_h5_chart(self, h5_name_input=''):
        # 打印标题
        print("-- The chart would be displayed in your browser --")
        h5_name = "ALL" if h5_name_input.upper() == "ALL" \
            else pb_func.get_available_h5_name(h5_name_input, self.__class__.bu_name)
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
            h5_inv_result.append(h5_info_check.get_h5_inventory_data(inv_item, "SAP_Price", h5_name, 24))
        # 读取final forecast
        h5_forecast = h5_info_check.get_h5_forecast(h5_name, "Final", 12)
        # Generate the chart with 12 months forecast
        chart_name = self.__class__.bu_name if h5_name == 'ALL' else h5_name
        self.draw_sales_inv_fcst_chart(chart_name, h5_sales_result, h5_inv_result, h5_forecast, 12, "h5")


if __name__ == "__main__":
    test = CodeDataDisplay("TU", "Jeffrey")
    test.show_code_all_info('440.834')
