from wxPython_Test_01 import MyFrame1
import wx
from crt_inv_calculation import CurrentInventoryCalculation as CIC

bookdata = {
    1: ("钢铁是怎样炼成的练成的", "2017-05-31"),
    2: ("秦腔", "2017-04-12"),
    3: ("西游记", "1987-08-12")
}


class wxDemo(MyFrame1):
    # Virtual event handlers, overide them in your derived class
    def codeSubmit(self, event):
        self.listCtrlOutput.InsertColumn(0, "ID")
        self.listCtrlOutput.InsertColumn(1, "Item")
        self.listCtrlOutput.InsertColumn(2, "Value")
        code_name = self.txtMaterialCode.Value.upper()
        CodeCalculation = CIC("TU")
        table_name = CodeCalculation.get_newest_date()
        code_inv_output = CodeCalculation.get_code_inv(code_name, table_name)
        for i in range(1, len(code_inv_output)):
            index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(i))
            self.listCtrlOutput.SetItem(index, 1, str(code_inv_output[i][0]))
            self.listCtrlOutput.SetItem(index, 2, str(code_inv_output[i][1]))
        # items = bookdata.items()
        # for key, data in items:
        #     index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(key))
        #     self.listCtrlOutput.SetItem(index, 1, data[0])
        #     self.listCtrlOutput.SetItem(index, 2, data[1])


if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    wxDemo(None).Show()
    app.MainLoop()
