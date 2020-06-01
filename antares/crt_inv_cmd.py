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
        if self.bu_name == "TU":
            crt_inv_display = dpl.TraumaCurrentInventoryDisplay()
        elif self.bu_name == "CMFT":
            crt_inv_display = dpl.CMFTCurrentInventoryDisplay()
        elif self.bu_name == "PT":
            crt_inv_display = dpl.PowerToolCurrentInventoryDisplay()
        elif self.bu_name == "JT":
            crt_inv_display = dpl.JointCurrentInventoryDisplay()
        elif self.bu_name == "MT":
            crt_inv_display = dpl.MitekCurrentInventoryDisplay()
        elif self.bu_name == "SP":
            crt_inv_display = dpl.DepuySpineCurrentInventoryDisplay()
        elif self.bu_name == "SPINE":
            crt_inv_display = dpl.SyntheSpineCurrentInventoryDisplay()
        else:
            pass
        crt_inv_display.command_list()


if __name__ == "__main__":
    bu_name = input("输入BU：")
    crt_inv = CurrentInventoryMenu(bu_name)
    crt_inv.crt_inv_entrance()


