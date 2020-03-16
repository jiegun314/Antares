# import info_show
# import data_update as update
# import crt_inv_cmd as crt
# import statis_fcst as fcst
# import mi
import re


class SystemIndex:
    bu_name = ""
    user_name = ""
    
    def __init__(self, bu, account):
        self.__class__.bu_name = bu
        self.__class__.user_name = account

    # 程序入口
    def entrance(self):
        self.__welcome_page()
        self._command_center()

    # 欢迎页面/home/jeffrey
    def __welcome_page(self):
        import public_function
        public_function.display_ascii_graph("welcome")
        print("** Welcome %s. Now you are handling %s **" % (self.__class__.user_name, self.__class__.bu_name))

    def __exit_page(self):
        import public_function
        public_function.display_ascii_graph("goodbye")
        self.cmd_exit = input()

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

    def _command_center(self):
        print("===Please wait a few seconds for module loading===")
        import info_show
        # 实例化显示信息的类
        cmd_info_index = info_show.InfoShow(self.__class__.bu_name, self.__class__.user_name)
        cmd_code = input("cmd >> ")
        while cmd_code != "exit":
            if cmd_code == "410":
                cmd_info_index.show_code_sales_data()
            elif cmd_code in ["400g", "400G"]:
                cmd_info_index.show_code_chart()
            elif cmd_code[0:3] == "400":
                if re.match(r'^(400)\s*\-\s*(\d{1,2})$', cmd_code):
                    month_number = int(re.match(r'^(400)\s*\-\s*(\d{1,2})$', cmd_code).group(2))
                    if month_number <= 24:
                        cmd_info_index.show_code_all_info(month_number)
                    else:
                        print("!!ERROR: Too many months, the upper limit is 24")
                elif cmd_code == "400":
                    cmd_info_index.show_code_all_info()
                else:
                    print("!!ERROR: Wrong CMD code. Plz input right cmd code, or input exit to quit.")
            elif cmd_code == "420":
                cmd_info_index.show_code_hstr_inv()
            elif cmd_code == "427":
                cmd_info_index.show_code_statistical_forecast(24)
            elif cmd_code == "310":
                cmd_info_index.show_h5_sales_data()
            elif cmd_code == "320":
                cmd_info_index.show_h5_inv()
            elif cmd_code in ["300g", "300G"]:
                cmd_info_index.show_h5_chart()
            elif cmd_code[0:3] == "300":
                if re.match(r'^(300)\s*\-\s*(\d{1,2})$', cmd_code):
                    month_number = int(re.match(r'^(300)\s*\-\s*(\d{1,2})$', cmd_code).group(2))
                    if month_number <= 24:
                        cmd_info_index.show_h5_all_info(month_number)
                elif cmd_code.lstrip("300").lstrip().lstrip("-").lstrip().rstrip() == "":
                    cmd_info_index.show_h5_all_info()
                else:
                    print("!!ERROR: Wrong CMD code. Plz input right cmd code, or input exit to quit.")
            elif cmd_code in ["901", "902", "903", "905", "906", "909"]:
                import data_update as update
                data_input = update.MonthlyUpdate(self.__class__.bu_name)
                data_input.data_update_entrance(cmd_code)
            elif cmd_code == "919":
                import data_import
                data_input = data_import.DataInput(self.__class__.bu_name)
                data_input.import_public_master_data()
            elif cmd_code == "911":
                import data_import
                data_input = data_import.DataInput(self.__class__.bu_name)
                data_input.import_master_data()
            elif cmd_code == "450":
                cmd_info_index.show_code_eso()
            elif cmd_code == "000":
                import crt_inv_cmd as crt
                cmd_crt_inv = crt.CurrentInventoryMenu(self.__class__.bu_name)
                cmd_crt_inv.crt_inv_entrance()
            elif cmd_code == "888":
                import statis_fcst as fcst
                forecast_view = fcst.GetStatisticalForecast(self.__class__.bu_name)
                forecast_view.get_forecast_entrance()
            elif cmd_code == "999":
                import mi
                add_mi = mi.MI(self.__class__.bu_name)
                add_mi.mi_start()
            elif cmd_code == "111":
                cmd_info_index.show_command_list()
            else:
                print("!!ERROR: Wrong CMD code. Plz input right cmd code, or input exit to quit.")
            cmd_code = input("cmd >> ")
        self.__exit_page()


if __name__ == "__main__":
    name = input("Please input your name: ")
    if name.upper() == "JEFFREY":
        str_bu_name = "TU"
        login_status = True
        name = name.capitalize()
    else:
        login_status = False
    if login_status:
        info_check = SystemIndex(str_bu_name, name)
        info_check.entrance()
    else:
        print("!!Error: wrong user name, press Enter to exit!")
        exit_cmd = input()

    # 方法2获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail_v2()
    # info_check.export_to_excel(result)
    # 方法1获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail()
    # info_check.export_to_excel(result)
