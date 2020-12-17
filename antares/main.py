# import info_show
# import data_update as update
# import crt_inv_cmd as crt
# import statis_fcst as fcst
# import mi
# import re
import public_function as pb_fct


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

    # command list
    # code - show the information by code
    # h5, hierarchy, group - show the information by h5, including whole bu
    # update - update data, including master data and sales & inventory data
    # export - export to excel file
    # hospital_sales - show the chart of hospital sales
    # 000 or click - turn to oneclick page
    # mi - turn to mi page
    # help - help page
    # 888 or forecast or fcst - generate statistical forecast
    # switch - switch the user
    # exit - quit the system

    def _display_general_command_mode(self):
        print("=== Please wait a few seconds for module loading ===")
        import data_display
        # Get cmd_code and cmd_extension with split character "-"
        cmd_info_index = data_display.DataDisplay(self.__class__.bu_name, self.__class__.user_name)
        cmd_code = input("cmd >> ").strip().upper()
        # define different cmd code by cmd_code
        while cmd_code not in ['EXIT', 'SWITCH']:
            if cmd_code in ["915", 'CONSOLIDATE', 'CON']:
                from data_update import MasterDataConsolidation
                data_input = MasterDataConsolidation(self.__class__.bu_name)
                data_input.master_data_update_entrance()
            elif cmd_code == "500":
                from hospital_sales_calculation import HospitalSalesCalculation
                hospital_sale_review = HospitalSalesCalculation(self.__class__.bu_name)
                hospital_sale_review.start_generate_AIO_chart()
            elif cmd_code in ["000", 'ONECLICK', 'CLICK']:
                import crt_inv_cmd as crt
                cmd_crt_inv = crt.CurrentInventoryMenu(self.__class__.bu_name)
                cmd_crt_inv.crt_inv_entrance()
            elif cmd_code in ['777', 'SNOP']:
                import snop_export_v2 as snop
                data_export = snop.SNOPExportEntrance(self.__class__.bu_name)
                data_export.start_snop_export()
            elif cmd_code in ["888", 'FCST', 'FORECAST']:
                import statis_fcst as fcst
                forecast_view = fcst.GetStatisticalForecast(self.__class__.bu_name)
                forecast_view.get_forecast_entrance()
            elif cmd_code in ["999", 'MI']:
                import mi
                add_mi = mi.MI(self.__class__.bu_name)
                add_mi.mi_start()
            elif cmd_code in ["111", 'HELP']:
                cmd_info_index.show_command_list()
            elif cmd_code in ['CODE', 'C']:
                self._display_code_command_mode()
            elif cmd_code in ['H5', 'HIERARCHY', 'GROUP', 'H']:
                self._display_h5_command_mode()
            elif cmd_code in ['UPDATE', 'U']:
                self._display_update_command_mode()
            elif cmd_code in ['BU_UPDATE', 'BMU']:
                self._display_bu_master_data_update_command_mode()
            elif cmd_code in ['PUBLIC_UPDATE', 'PMU']:
                self._display_public_master_data_update_command_mode()
            else:
                print("!!ERROR: Wrong CMD code. Plz input right cmd code, or input exit to quit.")
            cmd_code = input("cmd >> ").strip().upper()
        if cmd_code == "SWITCH":
            self.__class__.bu_name, self.__class__.user_name = None, None
            self.login_control()
        elif cmd_code == 'EXIT':
            pb_fct.display_ascii_graph("goodbye")
        else:
            pass

    def _display_code_command_mode(self):
        from data_display import CodeDataDisplay
        code_info_display = CodeDataDisplay(self.__class__.bu_name, self.__class__.user_name)
        cmd_input = input('cmd >> code_display >> ').replace(' ', '').upper().split('-')
        code_input = cmd_input[0]
        cmd_extension = cmd_input[1] if len(cmd_input) > 1 else 'X'
        while code_input.upper() not in ['RETURN', 'EXIT']:
            if not code_input:
                pass
            elif cmd_extension == 'X':
                code_info_display.show_code_all_info(code_input)
            elif cmd_extension == 'G':
                code_info_display.show_code_chart(code_input)
            else:
                print('!! Warning - Wrong extension, please input again')
            # continue to show the command list
            cmd_input = input('cmd >> code_display >> ').replace(' ', '').upper().split('-')
            code_input = cmd_input[0]
            cmd_extension = cmd_input[1] if len(cmd_input) > 1 else 'X'

    def _display_h5_command_mode(self):
        from data_display import HierarchyDataDisplay
        h5_info_display = HierarchyDataDisplay(self.__class__.bu_name, self.__class__.user_name)
        cmd_input = input('cmd >> hierarchy5_display >> ').replace(' ', '').upper().split('-')
        h5_name_input = cmd_input[0]
        cmd_extension = cmd_input[1] if len(cmd_input) > 1 else 'X'
        mth_qty = min(int(cmd_input[2]), 24) if len(cmd_input) > 2 and cmd_input[2].isdecimal() else 12
        while h5_name_input.upper() not in ['RETURN', 'EXIT']:
            if not h5_name_input:
                pass
            elif cmd_extension == 'X':
                h5_info_display.show_h5_all_info(h5_name_input, mth_qty)
            elif cmd_extension == 'G':
                h5_info_display.show_h5_chart(h5_name_input)
            else:
                print('!! Warning - Wrong extension, please input again')
            # continue to show the command list
            cmd_input = input('cmd >> hierarchy5_display >> ').replace(' ', '').upper().split('-')
            h5_name_input = cmd_input[0]
            cmd_extension = cmd_input[1] if len(cmd_input) > 1 else 'X'
            mth_qty = min(int(cmd_input[2]), 24) if len(cmd_input) > 2 and cmd_input[2].isdecimal() else 12

    def _display_update_command_mode(self):
        from data_update import MonthlyUpdate
        monthly_update = MonthlyUpdate(self.__class__.bu_name)
        cmd_input = input('cmd >> data_update >> ').replace(' ', '').upper().split('-')
        update_item = cmd_input[0]
        while update_item.upper() not in ['RETURN', 'EXIT']:
            if update_item in ['GTS', 'G']:
                monthly_update.update_sales('GTS')
            elif update_item in ['LPSALES', 'L', 'N', 'NED', 'LP', 'NEDSALES']:
                monthly_update.update_sales('LPSales')
            elif update_item in ['IMS', 'I']:
                monthly_update.update_sales('IMS')
            elif update_item in ['JNJINV', 'JI', 'JNJ_INV']:
                monthly_update.update_jnj_inventory()
            elif update_item in ['NEDINV', 'NI', 'NED_INV', 'LPINV', 'LI']:
                monthly_update.update_lp_inv()
            elif update_item in ['FCST', 'F', 'FORECAST']:
                monthly_update.update_final_forecast()
            elif update_item in ['ESO', 'E']:
                monthly_update.update_eso()
            else:
                print('!! Warning - Wrong extension, please input again')
            cmd_input = input('cmd >> data_update >> ').replace(' ', '').upper().split('-')
            update_item = cmd_input[0]

    def _display_bu_master_data_update_command_mode(self):
        from data_update import MasterDataUpdate
        master_data_update = MasterDataUpdate(self.__class__.bu_name)
        print("-- Import BU Level Master Data for %s -- " % self.__class__.bu_name)
        print("Please Choose Master Data Type (1 - PM_List, 2 - SAP_Price, 3 - Phoenix_List, 4 - ROP_Setting, "
              "5 - ABC Ranking, 6 - NPI List)")
        dict_master_data = {'1': 'PM_List', '3': 'Phoenix_List', '4': 'ROP_Setting', '6': 'NPI_List'}
        cmd_input = input('cmd >> bu_master_data_update >> ').replace(' ', '').upper().split('-')
        update_item = cmd_input[0]
        while update_item.upper() not in ['RETURN', 'EXIT']:
            data_type = ''
            if update_item in dict_master_data:
                data_type = dict_master_data[update_item]
            elif update_item == '2':
                master_data_update.import_sap_price()
                print("SAP_Price is imported")
            elif update_item == '5':
                master_data_update.generate_tu_abc_ranking()
                print('ABC Ranking Template Done.~')
            else:
                print("!!Wrong code, please try again!")
            # if the data type is assigned, update the related data
            if data_type:
                master_data_update.import_bu_master_data(data_type)
            cmd_input = input('cmd >> bu_master_data_update >> ').replace(' ', '').upper().split('-')
            update_item = cmd_input[0]

    def _display_public_master_data_update_command_mode(self):
        from data_update import MasterDataUpdate
        public_master_data_update = MasterDataUpdate(self.__class__.bu_name)
        print("-- Import Public Master Data -- ")
        print("Please Choose Master Data Type (1 - Material Master, 2 - RAG Report, 3 - GTIN)")
        dict_public_master_data = {'1': "MATERIAL_MASTER", '2': "RAG_Report", '3': 'GTIN'}
        cmd_input = input('cmd >> bu_master_data_update >> ').replace(' ', '').upper().split('-')
        update_item = cmd_input[0]
        while update_item.upper() not in ['RETURN', 'EXIT']:
            if update_item in dict_public_master_data:
                data_type = dict_public_master_data[update_item]
                public_master_data_update.import_public_master_data(data_type)
            else:
                print("!!Wrong code, please try again!")
            cmd_input = input('cmd >> bu_master_data_update >> ').replace(' ', '').upper().split('-')
            update_item = cmd_input[0]

    def login_control(self):
        name = input("Please input your name: ")
        if name.capitalize() in self.bu_name_lst:
            self.__class__.user_name = name.capitalize()
            self.__class__.bu_name = self.bu_name_lst[self.__class__.user_name]
            pb_fct.display_ascii_graph("welcome")
            print("** Welcome %s. Now you are handling %s **" % (self.__class__.user_name, self.__class__.bu_name))
            self._display_general_command_mode()
        else:
            print("!!Error: wrong user name, please restart the program.")


if __name__ == "__main__":
    new_login = SystemIndex()
    new_login.login_control()

    # 方法2获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail_v2()
    # info_check.export_to_excel(result)
    # 方法1获取所有的代码信息并导出到excel
    # result = info_check.generate_code_detail()
    # info_check.export_to_excel(result)
