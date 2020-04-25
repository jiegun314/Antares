import crt_inv_display as dpl


class CurrentInventoryMenu:
    bu_name = ""
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu
    
    @staticmethod
    def __welcome_page():
        import public_function
        public_function.display_ascii_graph("crt_inv")

    def crt_inv_entrance(self):
        self.__welcome_page()
        crt_inv_display = dpl.CurrentInventoryDisplay(self.__class__.bu_name)
        cmd_code = input("cmd >> crt_inv >> ")
        while cmd_code != "exit":
            if cmd_code == "inv":
                crt_inv_display.display_current_inventory()
            elif cmd_code == "inv_export":
                crt_inv_display.export_inventory_data()
            elif cmd_code == "inv_alert":
                crt_inv_display.display_low_inventory_alert()
            elif cmd_code == "bo":
                crt_inv_display.display_current_backorder()
            elif cmd_code == "bo_export":
                crt_inv_display.export_backorder_data()
            elif cmd_code == "pending":
                crt_inv_display.display_pending_trend()
            elif cmd_code == "pending -q":
                crt_inv_display.display_pending_trend("quantity")
            elif cmd_code == "check":
                crt_inv_display.display_code_status()
            elif cmd_code == "trend":
                crt_inv_display.display_code_inventory_trend()
            elif cmd_code == "bu_trend":
                crt_inv_display.display_h5_inventory_trend()
            elif cmd_code == "h5_detail":
                crt_inv_display.display_h5_inv_detail()
            elif cmd_code == "bo_trend":
                crt_inv_display.display_backorder_trend()
            elif cmd_code == "mapping":
                crt_inv_display.display_mapping_inventory()
            elif cmd_code == "aging":
                crt_inv_display.display_aging_backorder()
            elif cmd_code == "sync":
                crt_inv_display.synchronize_oneclick_data()
            elif cmd_code == "help":
                dpl.CurrentInventoryDisplay.show_command_list()
            else:
                print("!!ERROR: Wrong CMD code. Plz input correct cmd code, or type \"exit\" to quit.")
            cmd_code = input("cmd >> crt_inv >> ")
        print("==============================<Back to Main Menu>==============================")


if __name__ == "__main__":
    bu_name = input("输入BU：")
    crt_inv = CurrentInventoryMenu(bu_name)
    crt_inv.crt_inv_entrance()


