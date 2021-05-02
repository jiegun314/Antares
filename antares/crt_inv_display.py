from crt_inv_calculation import CurrentInventoryCalculation as CIC
from crt_inv_calculation import TraumaCurrentInventoryCalculation as TU_CIC
from tabulate import tabulate
import public_function as pb_func
import draw_chart as chart
import pandas as pd


class CurrentInventoryDisplay:
    bu_name = ""
    db_path = "../data/_DB/"
    backorder_path = "../data/_Backorder/"
    inventory_path = "../data/_INV_Export/"
    source_file_path = "../data/_Source_Data/"
    oneclick_path = "L:\\COMPASS\\Oneclick Inventory Report\\Output\\"
    currency_rate = 6.9233

    def __init__(self):
        self.initiate_calculation()

    def initiate_calculation(self):
        self.oneclickcalculation = TU_CIC() if self.__class__.bu_name == 'TU' else CIC(self.__class__.bu_name)

    def display_code_status(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Single Code Inventory===")
        # 获取日期
        code_name = input("Input Material Code: ").upper()
        # check if this code exist in material master
        while not CodeCalculation.check_code(code_name):
            code_name = input("Wrong code, please re-input: ").upper()
        # start to get inventory data from oneclick database
        str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        # check if this date exist in newest oneclick file
        while not CodeCalculation.check_date_availability(table_name):
            print("!!Error - Wrong date, Please re-input! ")
            str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
            table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        code_inv_output = CodeCalculation.get_code_inv(code_name, table_name)
        print(tabulate(code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="github"))

    def display_mapping_inventory(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Inventory Status Mapping with Lists===")
        # get data file
        file_fullname = self.__class__.source_file_path + "Data_Mapping.txt"
        try:
            fo = open(file_fullname, "r")
        except FileNotFoundError:
            print("!Error, please make sure you have put Data_Mapping.txt under _Source_Data folder")
            return
        code_list = [item.strip() for item in fo.readlines()]
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = CodeCalculation.get_newest_date()
        else:
            table_name = "INV" + inventory_date
        if not CodeCalculation.check_date_availability(table_name):
            print("!Error, please make sure you input the correct date.")
            return
        inventory_result = CodeCalculation.inventory_mapping(code_list, table_name)
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result))))

    def display_h5_inv_detail(self):
        # CodeCalculation = CIC(self.__class__.bu_name)
        print("===Hierarchy_5 Inventory Detail List===")
        # Get H5 Name
        h5_input = input("Input Hierarchy_5 Name : ")
        h5_name = pb_func.get_available_h5_name(h5_input, self.__class__.bu_name)
        # if not right h5 name, return
        if h5_name == "NULL":
            print("No such Hierarchy_5 name and please try again!~")
            return
        # get the date
        date_input = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        # table_name = CodeCalculation.get_newest_date() if date_input == "" else "INV" + date_input
        # [inventory_result, total_inv_value] = CodeCalculation.get_h5_inv_detail(h5_name, table_name)
        inventory_date = self.oneclickcalculation.get_newest_date() if date_input == "" else date_input
        [inventory_result, total_inv_value] = self.oneclickcalculation.get_h5_inv_detail(h5_name, inventory_date)
        print("Total Inventory Value of " + h5_name + " is %s" % (format(total_inv_value, ",.0f")))
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result)), floatfmt=",.0f"))

    def display_current_backorder(self):
        # CodeCalculation = CIC(self.__class__.bu_name)
        print("===Current Backorder List===")
        # 获取日期
        date_input = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        # table_name = CodeCalculation.get_newest_date() if date_input == "" else "INV" + date_input
        inventory_date = self.oneclickcalculation.get_newest_date() if date_input == '' else date_input
        print("===== <Result of %s> =====" % inventory_date)
        # backorder_result = CodeCalculation.get_current_bo(table_name)
        backorder_result = self.oneclickcalculation.get_current_bo(inventory_date)
        print(tabulate(backorder_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(backorder_result)), floatfmt=",.0f"))

    def display_backorder_trend(self):
        # print title
        print("===Display Backorder Trend===")
        print(">> Calculation ongoing, please wait~")
        # CodeCalculation = CIC(self.__class__.bu_name)
        # [date_list, backorder_value_summary] = CodeCalculation.generate_backorder_trend()
        [date_list, backorder_value_summary] = self.oneclickcalculation.generate_backorder_trend()
        chart.backorder_trend_line_chart(date_list, backorder_value_summary, self.__class__.bu_name)
        print(">> Done, the chart is opened in web browser.")

    # display aging backorder list
    def display_aging_backorder(self):
        # print title
        print("===Display Aging Backorder===")
        # set exception list with abnormal backorder information
        exception_list = pb_func.get_exception_list(self.__class__.bu_name, "Aging_Backorder")
        CodeCalculation = CIC(self.__class__.bu_name)
        [aging_backorder_list, mapping_days] = CodeCalculation.generate_aging_backorder_list(exception_list)
        print("---Aging Backorder List within %s days---" % mapping_days)
        print(tabulate(aging_backorder_list, headers="firstrow", tablefmt="psql"))

    # display inventory alert with low inventory
    def display_low_inventory_alert(self):
        print("!!Warning. This function is not available for %s." % self.__class__.bu_name)

    def display_current_inventory(self):
        # CodeCalculation = CIC(self.__class__.bu_name)
        print("===Current Inventory List by Hierarchy_5===")
        # 获取日期
        date_input = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        # table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        inventory_date = self.oneclickcalculation.get_newest_date() if date_input == '' else date_input
        print("===== <Result of %s> =====" % inventory_date)
        # inventory_result, summary_result = CodeCalculation.get_current_inventory(table_name)
        [inventory_result, summary_result] = self.oneclickcalculation.get_current_inventory(inventory_date)
        print(tabulate(inventory_result, headers="firstrow", tablefmt="psql",
                       showindex=range(1, len(inventory_result)), floatfmt=",.0f"))
        total_available_stock_value, total_useful_stock_value, total_stock_value = summary_result
        print("Total Available Stock Value: RMB - %s, USD - %s"
              % (format(total_available_stock_value, ",.0f"),
                 format(total_available_stock_value / self.__class__.currency_rate, ",.0f")))
        print("Total Useful Stock Value: RMB - %s, USD - %s"
              % (format(total_useful_stock_value, ',.0f'),
                 format(total_useful_stock_value / self.__class__.currency_rate, ',.0f')))
        print("Total Stock Value: RMB - %s, USD - %s"
              % (format(total_stock_value, ',.0f'), format(total_stock_value / self.__class__.currency_rate, ',.0f')))

    def export_inventory_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        # print title
        print("===Export Inventory Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        df = CodeCalculation.export_inventory_data(table_name)
        if isinstance(df, pd.DataFrame):
            inventory_file = self.__class__.inventory_path + self.__class__.bu_name \
                             + "_Inventory_" + table_name[3:] + ".xlsx"
            df.to_excel(inventory_file, index=False)
            print("Inventory detail exported to " + inventory_file)
        else:
            print("Error. No data in that day, please choose the correct date")

    def export_backorder_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        # print title
        print("===Export Backorder Detail List===")
        # get data
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        table_name = CodeCalculation.get_newest_date() if inventory_date == "" else "INV" + inventory_date
        df = CodeCalculation.export_backorder_data(table_name)
        if isinstance(df, pd.DataFrame):
            backorder_file = self.__class__.backorder_path + self.__class__.bu_name \
                             + "_Backorder_" + table_name[3:] + ".xlsx"
            df.to_excel(backorder_file, index=False)
            print("Backorder detail exported to " + backorder_file)
        else:
            print("Error. No data in that day, please choose the correct date")

    def display_code_inventory_trend(self):
        # CodeCalculation = CIC(self.__class__.bu_name)
        print("===Single Code Available Stock Trend===")
        code_name = input("Input Material Code: ")
        # if CodeCalculation.check_code(code_name):
        #     CodeCalculation.generate_code_inv_trend(code_name)
        # else:
        #     print("!!Error - This Material Code does NOT exist, Please re-input! ")
        if self.oneclickcalculation.check_code(code_name):
            self.oneclickcalculation.generate_code_inv_trend(code_name)
        else:
            print("!!Error - This Material Code does NOT exist, Please re-input! ")

    def display_h5_inventory_trend(self, chart_type='single_line'):
        # CodeCalculation = CIC(self.__class__.bu_name)
        print("===Hierarchy_5 Available Stock Trend===")
        # 获取H5名称
        h5_input = input("Input Hierarchy_5 Name: ")
        if h5_input == "" or h5_input.upper() == "ALL":
            h5_result = "ALL"
        else:
            h5_result = pb_func.get_available_h5_name(h5_input, self.__class__.bu_name)
        # if not right h5 name, return
        if h5_result != "NULL":
            if chart_type == 'single_line':
                # CodeCalculation.generate_h5_inventory_trend(h5_result)
                self.oneclickcalculation.generate_h5_inventory_trend(h5_result)
            elif chart_type == 'double_line':
                # CodeCalculation.generate_h5_inventory_trend_two_dimension(h5_result)
                self.oneclickcalculation.generate_h5_inventory_trend_two_dimension(h5_result)
        else:
            print("!!Error, No such Hierarchy_5 name. Please try again!")
            return

    def display_pending_trend(self, chart_type='value'):
        print("===Display Pending Inventory Trend for %s===" % self.__class__.bu_name)
        # CodeCalculation = CIC(self.__class__.bu_name)
        # CodeCalculation.generate_pending_trend(chart_type)
        self.oneclickcalculation.generate_pending_trend()
        pass

    def synchronize_oneclick_data(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        lst_xcpt = ['20190118', ]
        print("===Sync Current Inventory Data from OneClick===")
        sync_result = CodeCalculation.inv_data_sync(90, lst_xcpt)
        if sync_result == "ERROR":
            print("!Error, the sharefolder cannot be opened. Make sure you've connected to JNJ network and try again.")
        else:
            print(">> Synchronization succeed!")
            print(">> %s days succeed, %s days fail. Updated to %s" % (sync_result[0], sync_result[1], sync_result[2]))
        # sync to new database
        self.oneclickcalculation.sync_days = 90
        self.oneclickcalculation.start_synchronize()

    def sync_ned_inventory(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Sync Current NED Inventory Data===")
        sync_result = CodeCalculation.sync_ned_inventory()
        if sync_result:
            print(">> Synchronization succeed!")
        else:
            print(">> Synchronization fail")
        pass

    def command_list(self):
        cmd_list_dict = {"inv": self.display_current_inventory,
                         "inv_export": self.export_inventory_data,
                         "inv_alert": self.display_low_inventory_alert,
                         "bo": self.display_current_backorder,
                         "bo_export": self.export_backorder_data,
                         "pending": self.display_pending_trend,
                         "pending -q": (self.display_pending_trend, "quantity"),
                         "check": self.display_code_status,
                         "trend": self.display_code_inventory_trend,
                         "h5_trend": self.display_h5_inventory_trend,
                         "h5_trend_q": (self.display_h5_inventory_trend, 'double_line'),
                         "h5_detail": self.display_h5_inv_detail,
                         "bo_trend": self.display_backorder_trend,
                         "mapping": self.display_mapping_inventory,
                         "aging": self.display_aging_backorder,
                         "sync": self.synchronize_oneclick_data,
                         "ned_sync":self.sync_ned_inventory,
                         "help": self.show_command_list
                         }
        cmd_code = input("cmd >> crt_inv >> ")
        while cmd_code.upper() != "EXIT":
            if cmd_code in cmd_list_dict:
                if isinstance(cmd_list_dict[cmd_code], tuple):
                    cmd_list_dict[cmd_code][0](cmd_list_dict[cmd_code][1])
                else:
                    cmd_list_dict[cmd_code]()
            else:
                print("!!ERROR: Wrong CMD code. Plz input correct cmd code, or type \"exit\" to quit.")
            cmd_code = input("cmd >> crt_inv >> ")
        print("==============================<Back to Main Menu>==============================")

    # Display command list
    @staticmethod
    def show_command_list():
        import public_function
        public_function.display_command_list("current_inventory_command")


class TraumaCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "TU"
        super().__init__()

    def display_code_status(self):
        # CodeCalculation = CIC(self.__class__.bu_name)
        # print("===Single Code Inventory===")
        # # 获取日期
        # code_name = input("Input Material Code: ").upper()
        # # check if this code exist in material master
        # while not CodeCalculation.check_code(code_name):
        #     code_name = input("Wrong code, please re-input: ").upper()
        # # start to get inventory data from oneclick database
        # str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        # table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        # # check if this date exist in newest oneclick file
        # while not CodeCalculation.check_date_availability(table_name):
        #     print("!!Error - Wrong date, Please re-input! ")
        #     str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        #     table_name = CodeCalculation.get_newest_date() if str_input == "" else "INV" + str_input
        # print("===== <Result of %s> =====" % table_name.lstrip("INV"))
        # code_inv_output = CodeCalculation.get_code_inv_with_ned(code_name, table_name)
        # print(tabulate(code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="github"))
        print("===Single Code Inventory===")
        # 获取日期
        code_name = input("Input Material Code: ").upper()
        # check if this code exist in material master
        while not self.oneclickcalculation.check_code(code_name):
            code_name = input("Wrong code, please re-input: ").upper()
        # start to get inventory data from oneclick database
        str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
        inventory_date = self.oneclickcalculation.get_newest_date() if str_input == "" else str_input
        # check if this date exist in newest oneclick file
        while not self.oneclickcalculation.check_date_availability(inventory_date):
            print("!!Error - Wrong date, Please re-input! ")
            str_input = input("Please input date (YYYYMMDD) OR press Enter to get most fresh date: ")
            inventory_date = self.oneclickcalculation.get_newest_date() if str_input == "" else str_input
        print("===== <Result of %s> =====" % inventory_date)
        code_inv_output = self.oneclickcalculation.get_code_inv_with_ned(code_name, inventory_date)
        print(tabulate(code_inv_output, headers="firstrow", floatfmt=",.0f", tablefmt="github"))

    def display_mapping_inventory(self):
        CodeCalculation = CIC(self.__class__.bu_name)
        print("===Inventory Status Mapping with Lists===")
        # get data file
        file_fullname = self.__class__.source_file_path + "Data_Mapping.txt"
        try:
            fo = open(file_fullname, "r")
        except FileNotFoundError:
            print("!Error, please make sure you have put Data_Mapping.txt under _Source_Data folder")
            return
        code_list = [item.strip() for item in fo.readlines()]
        # get the date
        inventory_date = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        if inventory_date == "":
            table_name = CodeCalculation.get_newest_date()
        else:
            table_name = "INV" + inventory_date
        if not CodeCalculation.check_date_availability(table_name):
            print("!Error, please make sure you input the correct date.")
            return
        inventory_result = CodeCalculation.inventory_mapping_with_ned_inv(code_list, table_name)
        print(tabulate(inventory_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(inventory_result))))

    def display_current_backorder(self):
        print("===Current Backorder List===")
        # 获取日期
        date_input = input("Inventory Data (YYYYMMDD, Press Enter to get newest) : ")
        inventory_date = self.oneclickcalculation.get_newest_date() if date_input == '' else date_input
        print("===== <Result of %s> =====" % date_input)
        backorder_result = self.oneclickcalculation.get_current_bo(inventory_date)
        print(tabulate(backorder_result, headers="firstrow", tablefmt="github",
                       showindex=range(1, len(backorder_result)), floatfmt=",.0f"))

    # display inventory alert with low inventory
    def display_low_inventory_alert(self):
        # print title
        print("===Display Low Inventory Alert===")
        # get low inventory result
        CodeCalculation = CIC(self.__class__.bu_name)
        low_inventory_list = CodeCalculation.get_low_inventory_alert()
        print(tabulate(low_inventory_list, headers="keys", tablefmt="psql", showindex="always",
                       floatfmt=(".0f", ".0f", ".1f", ".1f", ".0f", ".1f", ".0f", ".0f", ".0f")))

    def display_backorder_trend(self):
        # print title
        print("===Display Backorder Trend===")
        print(">> Calculation ongoing, please wait~")
        # CodeCalculation = TU_CIC()
        # [date_list, backorder_value_summary] = CodeCalculation.generate_backorder_trend()
        [date_list, backorder_value_summary] = self.oneclickcalculation.generate_backorder_trend()
        chart.backorder_trend_line_chart(date_list, backorder_value_summary, self.__class__.bu_name)
        print(">> Done, the chart is opened in web browser.")


class PowerToolCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "PT"
        super().__init__()


class CMFTCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "CMF"
        super().__init__()


class JointCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "JT"
        super().__init__()


class MitekCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "MT"
        super().__init__()


class SpineCurrentInventoryDisplay(CurrentInventoryDisplay):
    def __init__(self):
        self.__class__.bu_name = "Spine"
        super().__init__()


if __name__ == "__main__":
    test = TraumaCurrentInventoryDisplay()
    test.display_current_backorder()
    # test.inv_data_sync(50)
