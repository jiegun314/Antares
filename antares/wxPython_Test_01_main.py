import wxPython_Test_01
import wx

if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = wxPython_Test_01.MyFrame1(None)
    frm.Show()
    app.MainLoop()
