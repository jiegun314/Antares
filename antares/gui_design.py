# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv

ID_EXPORT_INVENTORY = 1000

###########################################################################
## Class DragonFrame
###########################################################################

class DragonFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Project Dragon GUI v0404", pos = wx.DefaultPosition, size = wx.Size( 1280,800 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.ntbkOneclick = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
        self.pnlOneclick = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer5.SetMinSize( wx.Size( -1,80 ) )

        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.btnSync = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Synchronize", wx.DefaultPosition, wx.Size( 160,45 ), wx.BORDER_NONE|wx.BU_EXACTFIT )
        self.btnSync.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
        self.btnSync.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

        bSizer5.Add( self.btnSync, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.m_staticline7 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizer5.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        rdbxCalculationTypeChoices = [ u"by Code", u"by Hierarchy" ]
        self.rdbxCalculationType = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Calculation Type", wx.DefaultPosition, wx.Size( -1,80 ), rdbxCalculationTypeChoices, 1, wx.RA_SPECIFY_COLS )
        self.rdbxCalculationType.SetSelection( 0 )
        bSizer5.Add( self.rdbxCalculationType, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 10, 20), 0, wx.EXPAND, 5 )

        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        bSizer101 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Material / H5 Name: ", wx.DefaultPosition, wx.Size( -1,15 ), wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText2.Wrap( -1 )

        self.m_staticText2.SetMaxSize( wx.Size( -1,30 ) )

        bSizer101.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer101.Add( ( 280, 0), 0, wx.EXPAND, 5 )

        self.chkbxWholeBU = wx.CheckBox( self.pnlOneclick, wx.ID_ANY, u"BU Level", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer101.Add( self.chkbxWholeBU, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer9.Add( bSizer101, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        self.txtMaterialCode = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,80 ), wx.TE_MULTILINE )
        bSizer11.Add( self.txtMaterialCode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        lstbxCodeSelectionChoices = []
        self.lstbxCodeSelection = wx.ListBox( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 350,80 ), lstbxCodeSelectionChoices, wx.LB_NEEDED_SB|wx.LB_SINGLE )
        bSizer11.Add( self.lstbxCodeSelection, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer9.Add( bSizer11, 0, wx.EXPAND, 5 )


        bSizer5.Add( bSizer9, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 25, 0), 0, wx.EXPAND, 5 )

        bSizer71 = wx.BoxSizer( wx.VERTICAL )

        bSizer71.SetMinSize( wx.Size( 0,60 ) )

        bSizer71.Add( ( 1, 25), 0, wx.EXPAND, 5 )

        self.m_staticText4 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Select Date", wx.Point( 0,0 ), wx.Size( -1,15 ), 0 )
        self.m_staticText4.Wrap( -1 )

        bSizer71.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.dtpkDate = wx.adv.DatePickerCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultDateTime, wx.Point( 0,0 ), wx.Size( 110,30 ), wx.adv.DP_DROPDOWN|wx.BORDER_SUNKEN )
        bSizer71.Add( self.dtpkDate, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizer5.Add( bSizer71, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 25, 0), 0, wx.EXPAND, 5 )

        bSizer10 = wx.BoxSizer( wx.VERTICAL )


        bSizer10.Add( ( 1, 25), 0, wx.EXPAND, 5 )

        self.bntClear = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.Size( 120,-1 ), 0|wx.BORDER_NONE )
        self.bntClear.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
        self.bntClear.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DDKSHADOW ) )

        bSizer10.Add( self.bntClear, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.btnSubmit = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Submit", wx.DefaultPosition, wx.Size( 120,-1 ), 0 )
        self.btnSubmit.SetMaxSize( wx.Size( -1,30 ) )

        bSizer10.Add( self.btnSubmit, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( bSizer10, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )


        bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        bSizer6.SetMinSize( wx.Size( -1,30 ) )
        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        self.btnExportInv = wx.Button( self.pnlOneclick, wx.ID_ANY, u"INV Exp.", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.btnExportInv, 0, wx.ALL, 5 )

        self.btnBOExp = wx.Button( self.pnlOneclick, wx.ID_ANY, u"BO Exp.", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.btnBOExp, 0, wx.ALL, 5 )

        self.m_staticline6 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        self.m_staticline6.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

        bSizer8.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer8.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.m_staticText41 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Log:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText41.Wrap( -1 )

        bSizer8.Add( self.m_staticText41, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtLog = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 800,-1 ), wx.TE_CENTER|wx.TE_READONLY|wx.BORDER_SUNKEN )
        self.txtLog.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )
        self.txtLog.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

        bSizer8.Add( self.txtLog, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer6.Add( bSizer8, 1, wx.EXPAND, 5 )


        bSizer4.Add( bSizer6, 0, wx.EXPAND, 5 )

        self.m_staticline2 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticText3 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Result", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )

        bSizer7.Add( self.m_staticText3, 0, wx.ALL, 5 )

        self.listCtrlOutput = wx.ListCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 1275,-1 ), wx.LC_REPORT|wx.LC_VRULES )
        bSizer7.Add( self.listCtrlOutput, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )


        self.pnlOneclick.SetSizer( bSizer4 )
        self.pnlOneclick.Layout()
        bSizer4.Fit( self.pnlOneclick )
        self.ntbkOneclick.AddPage( self.pnlOneclick, u"Oneclick", False )

        bSizer1.Add( self.ntbkOneclick, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        self.statusBar = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.systemExit = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.systemExit )

        self.m_menubar1.Append( self.m_menu1, u"File" )

        self.buDefine = wx.Menu()
        self.mTrauma = wx.MenuItem( self.buDefine, ID_EXPORT_INVENTORY, u"Trauma", wx.EmptyString, wx.ITEM_RADIO )
        self.buDefine.Append( self.mTrauma )

        self.mCMFT = wx.MenuItem( self.buDefine, wx.ID_ANY, u"CMFT", wx.EmptyString, wx.ITEM_RADIO )
        self.buDefine.Append( self.mCMFT )

        self.mPT = wx.MenuItem( self.buDefine, wx.ID_ANY, u"PT", wx.EmptyString, wx.ITEM_NORMAL )
        self.buDefine.Append( self.mPT )

        self.m_menubar1.Append( self.buDefine, u"Business Unit" )

        self.m_menu2 = wx.Menu()
        self.showAbout = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu2.Append( self.showAbout )

        self.m_menubar1.Append( self.m_menu2, u"About" )

        self.SetMenuBar( self.m_menubar1 )

        self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.m_toolBar1.SetToolBitmapSize( wx.Size( 20,20 ) )
        self.m_toolBar1.SetToolPacking( 0 )
        self.m_toolBar1.AddSeparator()

        self.mDisplayCurrentInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/current_day.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current inventory", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mCurrentBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/backorder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current backorder", wx.EmptyString, None )

        self.mAgingBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/aging_backorder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"display aging backorder", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mPendingInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/pending.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mCodeTrend = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/code_trend.ico", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display inventory trend by code", wx.EmptyString, None )

        self.mH5Trend = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/h5_trend.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display inventory trend of one hierarchy", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.Realize()


        self.Centre( wx.BOTH )

        # Connect Events
        self.btnSync.Bind( wx.EVT_BUTTON, self.sync_inventory )
        self.chkbxWholeBU.Bind( wx.EVT_CHECKBOX, self.bu_level_selected )
        self.lstbxCodeSelection.Bind( wx.EVT_LEFT_DCLICK, self.display_h5_inventory )
        self.bntClear.Bind( wx.EVT_BUTTON, self.clear_input )
        self.btnSubmit.Bind( wx.EVT_BUTTON, self.codeSubmit )
        self.btnExportInv.Bind( wx.EVT_BUTTON, self.export_inventory )
        self.btnBOExp.Bind( wx.EVT_BUTTON, self.export_backorder )
        self.Bind( wx.EVT_MENU, self.select_bu_TU, id = self.mTrauma.GetId() )
        self.Bind( wx.EVT_MENU, self.select_bu_CMFT, id = self.mCMFT.GetId() )
        self.Bind( wx.EVT_MENU, self.select_bu_PT, id = self.mPT.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_inventory_list, id = self.mDisplayCurrentInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_bo_list, id = self.mCurrentBackorder.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_aging_backorder, id = self.mAgingBackorder.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_pending_inventory, id = self.mPendingInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_code_trend, id = self.mCodeTrend.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_h5_trend, id = self.mH5Trend.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def sync_inventory( self, event ):
        event.Skip()

    def bu_level_selected( self, event ):
        event.Skip()

    def display_h5_inventory( self, event ):
        event.Skip()

    def clear_input( self, event ):
        event.Skip()

    def codeSubmit( self, event ):
        event.Skip()

    def export_inventory( self, event ):
        event.Skip()

    def export_backorder( self, event ):
        event.Skip()

    def select_bu_TU( self, event ):
        event.Skip()

    def select_bu_CMFT( self, event ):
        event.Skip()

    def select_bu_PT( self, event ):
        event.Skip()

    def get_current_inventory_list( self, event ):
        event.Skip()

    def get_current_bo_list( self, event ):
        event.Skip()

    def display_aging_backorder( self, event ):
        event.Skip()

    def display_pending_inventory( self, event ):
        event.Skip()

    def display_code_trend( self, event ):
        event.Skip()

    def display_h5_trend( self, event ):
        event.Skip()


