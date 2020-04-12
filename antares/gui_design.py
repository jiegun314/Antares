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
import wx.dataview

###########################################################################
## Class DragonFrame
###########################################################################

class DragonFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Project Dragon GUI v0411", pos = wx.DefaultPosition, size = wx.Size( 1280,800 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.ntbkOneclick = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
        self.pnlOneclick = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer5.SetMinSize( wx.Size( -1,80 ) )

        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.btnSync = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnSync.SetBitmap( wx.Bitmap( u".icon/sync_black.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSync.SetBitmapCurrent( wx.Bitmap( u".icon/sync_blue.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSync.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnSync.SetToolTip( u"Sync Inventory with oneclick file" )

        bSizer5.Add( self.btnSync, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.m_staticline7 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizer5.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        rdbxCalculationTypeChoices = [ u"by Code", u"by Hierarchy" ]
        self.rdbxCalculationType = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Calculation Type", wx.DefaultPosition, wx.Size( -1,88 ), rdbxCalculationTypeChoices, 1, wx.RA_SPECIFY_COLS )
        self.rdbxCalculationType.SetSelection( 0 )
        bSizer5.Add( self.rdbxCalculationType, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )


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


        bSizer5.Add( ( 30, 0), 0, wx.EXPAND, 5 )

        bSizer71 = wx.BoxSizer( wx.VERTICAL )

        bSizer71.SetMinSize( wx.Size( 0,60 ) )

        bSizer71.Add( ( 1, 25), 0, wx.EXPAND, 5 )

        self.chkbxToday = wx.CheckBox( self.pnlOneclick, wx.ID_ANY, u"Today", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer71.Add( self.chkbxToday, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer71.Add( ( 0, 5), 0, wx.EXPAND, 5 )

        self.dtpkDate = wx.adv.DatePickerCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultDateTime, wx.Point( 0,0 ), wx.Size( 110,30 ), wx.adv.DP_DROPDOWN|wx.BORDER_SUNKEN )
        bSizer71.Add( self.dtpkDate, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizer5.Add( bSizer71, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 25, 0), 0, wx.EXPAND, 5 )

        self.btnCodeSubmit = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnCodeSubmit.SetBitmap( wx.Bitmap( u".icon/submit.png", wx.BITMAP_TYPE_ANY ) )
        self.btnCodeSubmit.SetBitmapCurrent( wx.Bitmap( u".icon/submit_green.png", wx.BITMAP_TYPE_ANY ) )
        self.btnCodeSubmit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnCodeSubmit.SetToolTip( u"Submit" )

        bSizer5.Add( self.btnCodeSubmit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.btnReset = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnReset.SetBitmap( wx.Bitmap( u".icon/reset.png", wx.BITMAP_TYPE_ANY ) )
        self.btnReset.SetBitmapCurrent( wx.Bitmap( u".icon/reset_red.png", wx.BITMAP_TYPE_ANY ) )
        self.btnReset.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnReset.SetToolTip( u"Reset Input" )

        bSizer5.Add( self.btnReset, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        bSizer6.SetMinSize( wx.Size( -1,30 ) )
        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        self.btnInventoryExport = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnInventoryExport.SetBitmap( wx.Bitmap( u".icon/inventory_export.png", wx.BITMAP_TYPE_ANY ) )
        self.btnInventoryExport.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnInventoryExport.SetToolTip( u"Export Inventory" )

        bSizer8.Add( self.btnInventoryExport, 0, wx.ALL, 5 )

        self.btnBackorderExport = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnBackorderExport.SetBitmap( wx.Bitmap( u".icon/backorder_export.png", wx.BITMAP_TYPE_ANY ) )
        self.btnBackorderExport.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnBackorderExport.SetToolTip( u"Export Backorder" )

        bSizer8.Add( self.btnBackorderExport, 0, wx.ALL, 5 )

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


        bSizer8.Add( ( 200, 0), 0, wx.EXPAND, 5 )

        self.btnOutputDownload = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnOutputDownload.SetBitmap( wx.Bitmap( u".icon/data_download.png", wx.BITMAP_TYPE_ANY ) )
        bSizer8.Add( self.btnOutputDownload, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer8, 1, wx.EXPAND, 5 )


        bSizer4.Add( bSizer6, 0, wx.EXPAND, 5 )

        self.m_staticline2 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer7 = wx.BoxSizer( wx.VERTICAL )

        self.listCtrlOutput = wx.ListCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 1275,-1 ), wx.LC_REPORT|wx.LC_VRULES )
        bSizer7.Add( self.listCtrlOutput, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )


        self.pnlOneclick.SetSizer( bSizer4 )
        self.pnlOneclick.Layout()
        bSizer4.Fit( self.pnlOneclick )
        self.ntbkOneclick.AddPage( self.pnlOneclick, u"Oneclick", True )
        self.pnlSummary = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.pnlSummary.SetToolTip( u"Show historical data summary" )

        bSizer15 = wx.BoxSizer( wx.VERTICAL )

        bSizer51 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer51.SetMinSize( wx.Size( -1,80 ) )
        rdbxSumaryCalculationTypeChoices = [ u"by Code", u"by Hierarchy" ]
        self.rdbxSumaryCalculationType = wx.RadioBox( self.pnlSummary, wx.ID_ANY, u"Calculation Type", wx.DefaultPosition, wx.Size( -1,88 ), rdbxSumaryCalculationTypeChoices, 1, wx.RA_SPECIFY_COLS )
        self.rdbxSumaryCalculationType.SetSelection( 0 )
        bSizer51.Add( self.rdbxSumaryCalculationType, 0, wx.ALL|wx.ALIGN_BOTTOM, 5 )


        bSizer51.Add( ( 10, 20), 0, wx.EXPAND, 5 )

        bSizer91 = wx.BoxSizer( wx.VERTICAL )

        bSizer1011 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText21 = wx.StaticText( self.pnlSummary, wx.ID_ANY, u"Material / H5 Name: ", wx.DefaultPosition, wx.Size( -1,15 ), wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText21.Wrap( -1 )

        self.m_staticText21.SetMaxSize( wx.Size( -1,30 ) )

        bSizer1011.Add( self.m_staticText21, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer1011.Add( ( 150, 0), 0, wx.EXPAND, 5 )

        self.chkbxSummaryWholeBU = wx.CheckBox( self.pnlSummary, wx.ID_ANY, u"BU Level", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer1011.Add( self.chkbxSummaryWholeBU, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer91.Add( bSizer1011, 1, wx.EXPAND, 5 )

        bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

        self.txtSummaryMaterialCode = wx.TextCtrl( self.pnlSummary, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 120,80 ), wx.TE_MULTILINE )
        bSizer111.Add( self.txtSummaryMaterialCode, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        lstbxSummaryListSelectionChoices = []
        self.lstbxSummaryListSelection = wx.ListBox( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.Size( 250,80 ), lstbxSummaryListSelectionChoices, wx.LB_NEEDED_SB|wx.LB_SINGLE )
        bSizer111.Add( self.lstbxSummaryListSelection, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer91.Add( bSizer111, 0, wx.EXPAND, 5 )


        bSizer51.Add( bSizer91, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer51.Add( ( 10, 0), 0, wx.EXPAND, 5 )

        self.btnSummarySubmit = wx.BitmapButton( self.pnlSummary, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnSummarySubmit.SetBitmap( wx.Bitmap( u".icon/submit.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSummarySubmit.SetBitmapCurrent( wx.Bitmap( u".icon/submit_green.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSummarySubmit.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
        self.btnSummarySubmit.SetToolTip( u"Submit" )

        bSizer51.Add( self.btnSummarySubmit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer51.Add( ( 10, 0), 0, wx.EXPAND, 5 )

        self.btnSummaryReset = wx.BitmapButton( self.pnlSummary, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnSummaryReset.SetBitmap( wx.Bitmap( u".icon/reset.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSummaryReset.SetBitmapCurrent( wx.Bitmap( u".icon/reset_red.png", wx.BITMAP_TYPE_ANY ) )
        self.btnSummaryReset.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
        self.btnSummaryReset.SetToolTip( u"Reset Input" )

        bSizer51.Add( self.btnSummaryReset, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer51.Add( ( 15, 0), 0, wx.EXPAND, 5 )

        self.m_staticline9 = wx.StaticLine( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        bSizer51.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer36 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText9 = wx.StaticText( self.pnlSummary, wx.ID_ANY, u"Basic\nInfo.", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )

        bSizer36.Add( self.m_staticText9, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.dtViewCtrlBasicInfo = wx.dataview.DataViewCtrl( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.Size( 530,100 ), 0 )
        bSizer36.Add( self.dtViewCtrlBasicInfo, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer51.Add( bSizer36, 1, wx.EXPAND, 5 )


        bSizer15.Add( bSizer51, 1, wx.EXPAND, 5 )

        self.m_staticline8 = wx.StaticLine( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer15.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer16 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer34 = wx.BoxSizer( wx.VERTICAL )

        bSizer29 = wx.BoxSizer( wx.HORIZONTAL )

        rdbxSummaryUnitChoices = [ u"by Quantity", u"by Std. Cost", u"by SAP Price" ]
        self.rdbxSummaryUnit = wx.RadioBox( self.pnlSummary, wx.ID_ANY, u"Unit", wx.DefaultPosition, wx.DefaultSize, rdbxSummaryUnitChoices, 1, wx.RA_SPECIFY_ROWS )
        self.rdbxSummaryUnit.SetSelection( 0 )
        bSizer29.Add( self.rdbxSummaryUnit, 0, wx.ALL, 5 )


        bSizer29.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        rdbxSummaryCategoryChoices = [ u"Historical", u"Forecast", u"ESO" ]
        self.rdbxSummaryCategory = wx.RadioBox( self.pnlSummary, wx.ID_ANY, u"Category", wx.DefaultPosition, wx.DefaultSize, rdbxSummaryCategoryChoices, 1, wx.RA_SPECIFY_ROWS )
        self.rdbxSummaryCategory.SetSelection( 0 )
        bSizer29.Add( self.rdbxSummaryCategory, 0, wx.ALL, 5 )


        bSizer34.Add( bSizer29, 1, wx.EXPAND, 5 )

        self.dtvwlstctrlSummaryOutput = wx.dataview.DataViewListCtrl( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.Size( 1300,380 ), 0 )
        bSizer34.Add( self.dtvwlstctrlSummaryOutput, 0, wx.ALL, 5 )


        bSizer16.Add( bSizer34, 0, wx.EXPAND, 5 )


        bSizer15.Add( bSizer16, 1, wx.EXPAND, 5 )

        bSizer24 = wx.BoxSizer( wx.VERTICAL )

        bSizer361 = wx.BoxSizer( wx.VERTICAL )

        self.m_staticline71 = wx.StaticLine( self.pnlSummary, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer361.Add( self.m_staticline71, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer28 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText91 = wx.StaticText( self.pnlSummary, wx.ID_ANY, u"Log", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText91.Wrap( -1 )

        bSizer28.Add( self.m_staticText91, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtSummaryLog = wx.TextCtrl( self.pnlSummary, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 700,-1 ), wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_READONLY )
        bSizer28.Add( self.txtSummaryLog, 0, wx.ALL, 5 )


        bSizer361.Add( bSizer28, 1, wx.EXPAND, 5 )


        bSizer24.Add( bSizer361, 1, wx.EXPAND, 5 )


        bSizer15.Add( bSizer24, 1, wx.EXPAND, 5 )


        self.pnlSummary.SetSizer( bSizer15 )
        self.pnlSummary.Layout()
        bSizer15.Fit( self.pnlSummary )
        self.ntbkOneclick.AddPage( self.pnlSummary, u"Summary", False )

        bSizer1.Add( self.ntbkOneclick, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        self.statusBar = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.menuFile = wx.Menu()
        self.mExit = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.Append( self.mExit )

        self.m_menubar1.Append( self.menuFile, u"File" )

        self.menuDefineBU = wx.Menu()
        self.mTrauma = wx.MenuItem( self.menuDefineBU, wx.ID_ANY, u"Trauma", wx.EmptyString, wx.ITEM_RADIO )
        self.menuDefineBU.Append( self.mTrauma )

        self.mCMFT = wx.MenuItem( self.menuDefineBU, wx.ID_ANY, u"CMFT", wx.EmptyString, wx.ITEM_RADIO )
        self.menuDefineBU.Append( self.mCMFT )

        self.mPT = wx.MenuItem( self.menuDefineBU, wx.ID_ANY, u"PT", wx.EmptyString, wx.ITEM_RADIO )
        self.menuDefineBU.Append( self.mPT )

        self.m_menubar1.Append( self.menuDefineBU, u"Business Unit" )

        self.menuAbout = wx.Menu()
        self.showAbout = wx.MenuItem( self.menuAbout, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuAbout.Append( self.showAbout )

        self.m_menubar1.Append( self.menuAbout, u"About" )

        self.SetMenuBar( self.m_menubar1 )

        self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.m_toolBar1.SetToolBitmapSize( wx.Size( 20,20 ) )
        self.m_toolBar1.SetToolPacking( 0 )
        self.m_toolBar1.AddSeparator()

        self.mDisplayCurrentInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/current_day.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current inventory", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mCurrentBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/backorder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current backorder", wx.EmptyString, None )

        self.mBackorderTrend = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bo_trend.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"display trend of backorder value", wx.EmptyString, None )

        self.mAgingBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/aging_backorder.ico", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"display aging backorder", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mPendingInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/pending.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display trend for pending inventory value", wx.EmptyString, None )

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
        self.chkbxToday.Bind( wx.EVT_CHECKBOX, self.set_date_as_today )
        self.dtpkDate.Bind( wx.adv.EVT_DATE_CHANGED, self.set_checking_date )
        self.btnCodeSubmit.Bind( wx.EVT_BUTTON, self.codeSubmit )
        self.btnReset.Bind( wx.EVT_BUTTON, self.clear_input )
        self.btnInventoryExport.Bind( wx.EVT_BUTTON, self.export_inventory )
        self.btnBackorderExport.Bind( wx.EVT_BUTTON, self.export_backorder )
        self.btnOutputDownload.Bind( wx.EVT_BUTTON, self.export_listed_data )
        self.chkbxSummaryWholeBU.Bind( wx.EVT_CHECKBOX, self.summary_bu_level_selected )
        self.lstbxSummaryListSelection.Bind( wx.EVT_LEFT_DCLICK, self.display_h5_summary )
        self.btnSummarySubmit.Bind( wx.EVT_BUTTON, self.summary_view_submit )
        self.btnSummaryReset.Bind( wx.EVT_BUTTON, self.summary_view_reset )
        self.Bind( wx.EVT_MENU, self.exit_dragon, id = self.mExit.GetId() )
        self.Bind( wx.EVT_MENU, self.select_bu_TU, id = self.mTrauma.GetId() )
        self.Bind( wx.EVT_MENU, self.select_bu_CMFT, id = self.mCMFT.GetId() )
        self.Bind( wx.EVT_MENU, self.select_bu_PT, id = self.mPT.GetId() )
        self.Bind( wx.EVT_MENU, self.show_about_dialog, id = self.showAbout.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_inventory_list, id = self.mDisplayCurrentInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_bo_list, id = self.mCurrentBackorder.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_backorder_trend, id = self.mBackorderTrend.GetId() )
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

    def set_date_as_today( self, event ):
        event.Skip()

    def set_checking_date( self, event ):
        event.Skip()

    def codeSubmit( self, event ):
        event.Skip()

    def clear_input( self, event ):
        event.Skip()

    def export_inventory( self, event ):
        event.Skip()

    def export_backorder( self, event ):
        event.Skip()

    def export_listed_data( self, event ):
        event.Skip()

    def summary_bu_level_selected( self, event ):
        event.Skip()

    def display_h5_summary( self, event ):
        event.Skip()

    def summary_view_submit( self, event ):
        event.Skip()

    def summary_view_reset( self, event ):
        event.Skip()

    def exit_dragon( self, event ):
        event.Skip()

    def select_bu_TU( self, event ):
        event.Skip()

    def select_bu_CMFT( self, event ):
        event.Skip()

    def select_bu_PT( self, event ):
        event.Skip()

    def show_about_dialog( self, event ):
        event.Skip()

    def get_current_inventory_list( self, event ):
        event.Skip()

    def get_current_bo_list( self, event ):
        event.Skip()

    def display_backorder_trend( self, event ):
        event.Skip()

    def display_aging_backorder( self, event ):
        event.Skip()

    def display_pending_inventory( self, event ):
        event.Skip()

    def display_code_trend( self, event ):
        event.Skip()

    def display_h5_trend( self, event ):
        event.Skip()


###########################################################################
## Class dlgAbout
###########################################################################

class dlgAbout ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"About", pos = wx.DefaultPosition, size = wx.Size( 400,260 ), style = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )


        bSizer13.Add( ( 0, 10), 0, wx.EXPAND, 5 )

        bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

        self.bitmapLogo = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u".icon/logo.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
        bSizer14.Add( self.bitmapLogo, 0, wx.ALL, 5 )

        bSizer15 = wx.BoxSizer( wx.VERTICAL )

        self.txtCtrlAbout = wx.TextCtrl( self, wx.ID_ANY, u"The program is GUI only for Project Dragon, to collect and centralize data from oneclick and display historical business information.", wx.DefaultPosition, wx.Size( 200,120 ), wx.TE_MULTILINE|wx.TE_NO_VSCROLL|wx.TE_READONLY|wx.BORDER_NONE )
        self.txtCtrlAbout.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

        bSizer15.Add( self.txtCtrlAbout, 0, wx.ALL, 5 )


        bSizer15.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.txtAuthor = wx.StaticText( self, wx.ID_ANY, u"by Jeffrey Zhou", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txtAuthor.Wrap( -1 )

        bSizer15.Add( self.txtAuthor, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )


        bSizer15.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.btnAboutClose = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer15.Add( self.btnAboutClose, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer14.Add( bSizer15, 1, wx.EXPAND, 5 )


        bSizer13.Add( bSizer14, 1, wx.EXPAND, 5 )


        bSizer13.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        bSizer11.Add( bSizer13, 1, wx.EXPAND, 5 )


        self.SetSizer( bSizer11 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btnAboutClose.Bind( wx.EVT_BUTTON, self.close_about_dialog )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def close_about_dialog( self, event ):
        event.Skip()


