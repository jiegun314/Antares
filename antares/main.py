# import info_show
# import data_update as update
# import crt_inv_cmd as crt
# import statis_fcst as fcst
# import mi
# import re


class SystemIndex:
    bu_name = None
    user_name = None
    bu_name_lst = {
        "Jeffrey": "TU",
        "Cecilia": "CMFT",
        "Yuanzhi": "PT",
        "Raymond": "JT",
        "Doris": "Spine",
        "Tina": "MT"
    }
    
    def __init__(self):
        pass

    # 程序入口
    def __entrance(self):
        self.__welcome_page()
        self.__command_center()

    # 欢迎页面/home/jeffrey
    def __welcome_page(self):
        import public_function
        public_function.display_ascii_graph("welcome")
        print("** Welcome %s. Now you are handling %s **" % (self.__class__.user_name, self.__class__.bu_name))

    def __exit_page(self):
        import public_function
        public_function.display_ascii_graph("goodbye")

    # 命令接收及跳转中心
    # 命令设计逻辑：
    # 前缀（1位）+ 命令种类（1位） + 命令详细（1位）
    # 前缀，0 - 整个骨科BU，1 -- BU Level, 3 - H5, 4 - Code Level, 8 - ESO, 9 - FCST, 000 - 转到Oneclick分析
    # 命令种类：
    # 1 - 销售情况， 2 - 库存情况， 3 - FCST， 5 - ESO， 9 - MI， 0 - 整体详细信息
    # 1. 销售情况
    # X11 - GTS，X12 - LP Sales, X13 - IMS, X14 - 三个数据同时显示
    # 2. 库存
    # X21： JNJ INV， X22 - LP INV， X24 - 所有库存
    # 8. FCST
    # X81 - Statistical FCST
    # X89 - Final FCST
    # 9. MI
    # X99 - MI调整
    # 0. Overall Information

    def __command_center(self):
        print("===Please wait a few seconds for module loading===")
        import data_display
        # Get cmd_code and cmd_extension with split character "-"
        cmd_info_index = data_display.DataDisplay(self.__class__.bu_name, self.__class__.user_name)
        cmd_input = input("cmd >> ").replace(' ', '').upper().split('-')
        [cmd_code, cmd_extension] = [cmd_input[0], '0'] if len(cmd_input) == 1 else [cmd_input[0], cmd_input[1]]
        # define different cmd code by cmd_code
        while cmd_code != "EXIT" and cmd_code != "SWITCH":
            if cmd_code == "410":
                cmd_info_index.show_code_sales_data()
            elif cmd_code == "400G":
                cmd_info_index.show_code_chart()
            elif cmd_code == "400":
                if cmd_extension.isdecimal() and int(cmd_extension) <= 24:
                    month_number = int(cmd_extension) if int(cmd_extension) else 12
                    cmd_info_index.show_code_all_info(month_number)
                else:
                    print("!!ERROR: Please input correct month number below 24")
            elif cmd_code == "420":
                cmd_info_index.show_code_historical_inventory()
            elif cmd_code == "310":
                cmd_info_index.show_h5_sales_data()
            elif cmd_code == "320":
                cmd_info_index.show_h5_inventory()
            elif cmd_code == "300G":
                cmd_info_index.show_h5_chart()
            elif cmd_code[0:3] == "300":
                if cmd_extension.isdecimal() and int(cmd_extension) <= 24:
                    month_number = int(cmd_extension) if int(cmd_extension) else 12
                    cmd_info_index.show_h5_all_info(month_number)
                else:
                    print("!!ERROR: Please input correct month number below 24")
            elif cmd_code in ["901", "902", "903", "905", "906", "908", "909"]:
                import data_update as update
                data_input = update.MonthlyUpdate(self.__class__.bu_name)
                data_input.data_update_entrance(cmd_code)
            elif cmd_code == "919":
                from data_update import MasterDataUpdate
                data_input = MasterDataUpdate(self.__class__.bu_name)
                data_input.import_public_master_data()
            elif cmd_code == "911":
                from data_update import MasterDataUpdate
                data_input = MasterDataUpdate(self.__class__.bu_name)
                data_input.import_master_data()
            elif cmd_code == "915":
                from data_update import MasterDataConsolidation
                data_input = MasterDataConsolidation()
                data_input.bu_name = "TU"
                data_input.master_data_update_entrance()
            elif cmd_code == "450":
                cmd_info_index.show_code_eso()
            elif cmd_code == "500":
                from hospital_sales_calculation import HospitalSalesCalculation
                hospital_sale_review = HospitalSalesCalculation(self.__class__.bu_name)
                hospital_sale_review.start_generate_AIO_chart()
            elif cmd_code == "000":
                import crt_inv_cmd as crt
                cmd_crt_inv = crt.CurrentInventoryMenu(self.__class__.bu_name)
                cmd_crt_inv.crt_inv_entrance()
            elif cmd_code == '777':
                import snop_export_v2 as snop
                data_export = snop.SNOPExportEntrance(self.__class__.bu_name)
                data_export.start_snop_export()
            elif cmd_code == "888":
                import statis_fcst as fcst
                forecast_view = fcst.GetStatisticalForecast(self.__class__.bu_name)
                forecast_view.get_forecast_entrance()
            elif cmd_code == "999":
                import mi
                add_mi = mi.MI(self.__class__.bu_name)
                add_mi.mi_start()
            elif cmd_code == "111" or cmd_code == "help":
                cmd_info_index.show_command_list()
            else:
                print("!!ERROR: Wrong CMD code. Plz input right cmd code, or input exit to quit.")
            cmd_input = input("cmd >> ").replace(' ', '').upper().split('-')
            [cmd_code, cmd_extension] = [cmd_input[0], '0'] if len(cmd_input) == 1 else [cmd_input[0], cmd_input[1]]
        if cmd_code == "SWITCH":
            self.__class__.bu_name, self.__class__.user_name = None, None
            self.login_control()
        else:
            self.__exit_page()

    def login_control(self):
        name = input("Please input your name: ")
        try:
            self.__class__.bu_name = self.bu_name_lst[name.capitalize()]
        except KeyError:
            print("!!Error: wrong user name, please restart the program.")
        else:
            self.__class__.user_name = name.capitalize()
            self.__entrance()


if __name__ == "__main__":
    new_login = SystemIndex()
    new_login.login_control()

    # 方法2获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail_v2()
    # info_check.export_to_excel(result)
    # 方法1获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail()
    # info_check.export_to_excel(result)
