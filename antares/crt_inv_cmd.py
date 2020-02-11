import crt_inv_calculation as cclt


class CurrentInventoryMenu:
    bu_name = ""
    db_path = "../data/_DB/"

    def __init__(self, bu):
        self.__class__.bu_name = bu
    
    def __welcome_page(self):
        print("_______                  __________      ______      ________     ")
        print("__  __ \____________________  /__(_)________  /__    ___  __ \____________    ")
        print("_  / / /_  __ \  _ \  ___/_  /__  /_  ___/_  //_/    __  /_/ /_  ___/  __ \   ")
        print("/ /_/ /_  / / /  __/ /__ _  / _  / / /__ _  ,<       _  ____/_  /   / /_/ /__ ")
        print("\____/ /_/ /_/\___/\___/ /_/  /_/  \___/ /_/|_|      /_/     /_/    \____/_(_)")       
        print("=========================<Please Input CMD Code>=============================")

    def crt_inv_entrance(self):
        # self.db_name = self.__class__.db_path + self.__class__.bu_name + "_CRT_INV.db"
        self.__welcome_page()
        crt_inv_cclt = cclt.CurrentInventory(self.__class__.bu_name)

        cmd_code = input ("cmd >> crt_inv >> ")
        while cmd_code != "exit":
            if cmd_code == "inv":
                crt_inv_cclt.today_inv()
            elif cmd_code == "bo":
                crt_inv_cclt.get_current_bo()
            elif cmd_code == "bo_export":
                crt_inv_cclt.export_backorder_data()
            elif cmd_code == "pending":
                crt_inv_cclt.get_pending_trend()
            elif cmd_code == "check":
                crt_inv_cclt.get_code_inv()
            elif cmd_code == "trend":
                crt_inv_cclt.code_inv_trend()
            elif cmd_code == "bu_trend":
                crt_inv_cclt.h5_inv_trend()
            elif cmd_code == "sync":
                crt_inv_cclt.inv_data_sync(50)
            else:
                print("!!ERROR: Wrong CMD code. Plz input correct cmd code, or type \"exit\" to quit.")
            cmd_code = input("cmd >> crt_inv >> ")
        print("==================================<Back to Main Menu>==================================")
        pass


if __name__ == "__main__":
    bu_name = input("输入BU：")
    crt_inv = CurrentInventoryMenu(bu_name)
    crt_inv.crt_inv_entrance()


