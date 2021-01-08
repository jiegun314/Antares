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

###########################################################################
## Class DragonFrame
###########################################################################

class DragonFrame ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Project Dragon GUI v1211", pos = wx.DefaultPosition, size = wx.Size( 1500,800 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.ntbkOneclick = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
        self.pnlOneclick = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer16 = wx.BoxSizer( wx.VERTICAL )

        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.dtpkDate = wx.adv.DatePickerCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultDateTime, wx.Point( 0,0 ), wx.Size( 200,30 ), wx.adv.DP_DROPDOWN|wx.BORDER_SUNKEN )
        bSizer9.Add( self.dtpkDate, 0, wx.ALL, 5 )


        bSizer9.Add( ( 50, 1), 0, wx.EXPAND, 5 )

        self.chkbxToday = wx.CheckBox( self.pnlOneclick, wx.ID_ANY, u"Today", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.chkbxToday, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( bSizer9, 0, wx.EXPAND, 5 )

        bSizer71 = wx.BoxSizer( wx.VERTICAL )

        bSizer71.SetMinSize( wx.Size( 0,60 ) )

        bSizer5.Add( bSizer71, 0, wx.EXPAND, 5 )


        bSizer5.Add( ( 15, 0), 0, wx.EXPAND, 5 )

        self.m_staticline41 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer5.Add( self.m_staticline41, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer16.Add( bSizer5, 0, wx.EXPAND, 5 )

        bSizer19 = wx.BoxSizer( wx.VERTICAL )

        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer21.SetMinSize( wx.Size( -1,5 ) )
        self.txtLog = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 315,-1 ), wx.TE_CENTER|wx.TE_READONLY|wx.BORDER_SUNKEN )
        self.txtLog.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_CAPTIONTEXT ) )
        self.txtLog.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

        bSizer21.Add( self.txtLog, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer19.Add( bSizer21, 1, wx.EXPAND, 5 )

        self.m_staticline4 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer19.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer18 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer191 = wx.BoxSizer( wx.VERTICAL )

        bSizer191.SetMinSize( wx.Size( 90,-1 ) )

        bSizer191.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        rdbxCalculationTypeChoices = [ u"Code", u"H5" ]
        self.rdbxCalculationType = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Data Type", wx.DefaultPosition, wx.Size( 85,-1 ), rdbxCalculationTypeChoices, 1, wx.RA_SPECIFY_COLS )
        self.rdbxCalculationType.SetSelection( 1 )
        bSizer191.Add( self.rdbxCalculationType, 0, wx.ALIGN_CENTER, 5 )


        bSizer191.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.btnCodeSubmit = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnCodeSubmit.SetBitmap( wx.Bitmap( u".icon/submit.png", wx.BITMAP_TYPE_ANY ) )
        self.btnCodeSubmit.SetBitmapCurrent( wx.Bitmap( u".icon/submit_green.png", wx.BITMAP_TYPE_ANY ) )
        self.btnCodeSubmit.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnCodeSubmit.SetToolTip( u"Submit" )

        bSizer191.Add( self.btnCodeSubmit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.btnReset = wx.BitmapButton( self.pnlOneclick, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|wx.BORDER_NONE )

        self.btnReset.SetBitmap( wx.Bitmap( u".icon/reset.png", wx.BITMAP_TYPE_ANY ) )
        self.btnReset.SetBitmapCurrent( wx.Bitmap( u".icon/reset_red.png", wx.BITMAP_TYPE_ANY ) )
        self.btnReset.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
        self.btnReset.SetToolTip( u"Reset Input" )

        bSizer191.Add( self.btnReset, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer191.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        bSizer18.Add( bSizer191, 1, wx.EXPAND, 5 )

        self.txtMaterialCode = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 220,240 ), wx.TE_MULTILINE )
        bSizer18.Add( self.txtMaterialCode, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer19.Add( bSizer18, 1, wx.EXPAND, 5 )

        bSizer101 = wx.BoxSizer( wx.VERTICAL )

        bSizer20 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_staticText2 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Code / H5 Name: ", wx.DefaultPosition, wx.Size( -1,-1 ), wx.ALIGN_CENTER_HORIZONTAL )
        self.m_staticText2.Wrap( -1 )

        bSizer20.Add( self.m_staticText2, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer20.Add( ( 0, 0), 1, wx.EXPAND, 5 )

        self.chkbxWholeBU = wx.CheckBox( self.pnlOneclick, wx.ID_ANY, u"BU Level", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer20.Add( self.chkbxWholeBU, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer101.Add( bSizer20, 1, wx.EXPAND, 5 )

        bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

        lstbxCodeSelectionChoices = []
        self.lstbxCodeSelection = wx.ListBox( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 320,250 ), lstbxCodeSelectionChoices, wx.LB_NEEDED_SB|wx.LB_SINGLE )
        bSizer11.Add( self.lstbxCodeSelection, 0, wx.ALL, 5 )


        bSizer101.Add( bSizer11, 0, wx.EXPAND, 5 )


        bSizer19.Add( bSizer101, 1, wx.EXPAND, 5 )


        bSizer16.Add( bSizer19, 1, wx.EXPAND, 5 )


        bSizer4.Add( bSizer16, 1, wx.EXPAND, 5 )

        bSizer17 = wx.BoxSizer( wx.VERTICAL )

        self.listCtrlOutput = wx.ListCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 1200,-1 ), wx.LC_REPORT|wx.LC_VRULES )
        bSizer17.Add( self.listCtrlOutput, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer4.Add( bSizer17, 1, wx.EXPAND, 5 )


        self.pnlOneclick.SetSizer( bSizer4 )
        self.pnlOneclick.Layout()
        bSizer4.Fit( self.pnlOneclick )
        self.ntbkOneclick.AddPage( self.pnlOneclick, u"Oneclick", False )

        bSizer1.Add( self.ntbkOneclick, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        self.statusBar = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.menuFile = wx.Menu()
        self.mExit = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuFile.Append( self.mExit )

        self.m_menubar1.Append( self.menuFile, u"File" )

        self.menuExport = wx.Menu()
        self.mInvExport = wx.MenuItem( self.menuExport, wx.ID_ANY, u"Inventory Export", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuExport.Append( self.mInvExport )

        self.mBOExport = wx.MenuItem( self.menuExport, wx.ID_ANY, u"Backorder Export", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuExport.Append( self.mBOExport )

        self.m_menubar1.Append( self.menuExport, u"Data Export" )

        self.menuAbout = wx.Menu()
        self.showAbout = wx.MenuItem( self.menuAbout, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.menuAbout.Append( self.showAbout )

        self.m_menubar1.Append( self.menuAbout, u"About" )

        self.SetMenuBar( self.m_menubar1 )

        self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY )
        self.m_toolBar1.SetToolBitmapSize( wx.Size( 20,20 ) )
        self.m_toolBar1.SetToolPacking( 0 )
        self.m_toolBar1.AddSeparator()

        self.m_DataSync = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/sync_icon.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mDisplayCurrentInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/current_day.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current inventory", wx.EmptyString, None )

        self.mCurrentBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/backorder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display current backorder", wx.EmptyString, None )

        self.mBackorderTrend = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bo_trend.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"display trend of backorder value", wx.EmptyString, None )

        self.mAgingBackorder = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/aging_backorder.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"display aging backorder", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mPendingInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/pending.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display trend for pending inventory value", wx.EmptyString, None )

        self.mLowABInventory = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/low_inventory.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display low inventory for Rank A, B products", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.mInvTrend = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/inventory_trend.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Display inventory trend with selected name", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.mTU = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_TU.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"Trauma", wx.EmptyString, None )

        self.mCMFT = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_CMFT.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"CMFT", wx.EmptyString, None )

        self.mPT = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_PT.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"PowerTool", wx.EmptyString, None )

        self.mJT = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_JT.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"Joint", wx.EmptyString, None )

        self.mSpine = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_Spine.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"Spine", wx.EmptyString, None )

        self.mMT = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/bu_MT.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_RADIO, u"Mitek", wx.EmptyString, None )

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_toolBar1.AddSeparator()

        self.m_tool15 = self.m_toolBar1.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u".icon/data_download.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Download data in the list", wx.EmptyString, None )

        self.m_toolBar1.Realize()


        self.Centre( wx.BOTH )

        # Connect Events
        self.dtpkDate.Bind( wx.adv.EVT_DATE_CHANGED, self.set_checking_date )
        self.chkbxToday.Bind( wx.EVT_CHECKBOX, self.set_date_as_today )
        self.btnCodeSubmit.Bind( wx.EVT_BUTTON, self.codeSubmit )
        self.btnReset.Bind( wx.EVT_BUTTON, self.clear_input )
        self.chkbxWholeBU.Bind( wx.EVT_CHECKBOX, self.bu_level_selected )
        self.lstbxCodeSelection.Bind( wx.EVT_LEFT_DCLICK, self.display_h5_inventory )
        self.listCtrlOutput.Bind( wx.EVT_LIST_ITEM_ACTIVATED, self.click_item_in_list )
        self.Bind( wx.EVT_MENU, self.exit_dragon, id = self.mExit.GetId() )
        self.Bind( wx.EVT_MENU, self.export_inventory, id = self.mInvExport.GetId() )
        self.Bind( wx.EVT_MENU, self.export_backorder, id = self.mBOExport.GetId() )
        self.Bind( wx.EVT_MENU, self.show_about_dialog, id = self.showAbout.GetId() )
        self.Bind( wx.EVT_TOOL, self.sync_inventory, id = self.m_DataSync.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_inventory_list, id = self.mDisplayCurrentInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.get_current_bo_list, id = self.mCurrentBackorder.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_backorder_trend, id = self.mBackorderTrend.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_aging_backorder, id = self.mAgingBackorder.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_pending_inventory, id = self.mPendingInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_low_AB_inventory, id = self.mLowABInventory.GetId() )
        self.Bind( wx.EVT_TOOL, self.display_inventory_trend, id = self.mInvTrend.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_TU, id = self.mTU.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_CMFT, id = self.mCMFT.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_PT, id = self.mPT.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_JT, id = self.mJT.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_SP, id = self.mSpine.GetId() )
        self.Bind( wx.EVT_TOOL, self.select_bu_MT, id = self.mMT.GetId() )
        self.Bind( wx.EVT_TOOL, self.export_listed_data, id = self.m_tool15.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def set_checking_date( self, event ):
        event.Skip()

    def set_date_as_today( self, event ):
        event.Skip()

    def codeSubmit( self, event ):
        event.Skip()

    def clear_input( self, event ):
        event.Skip()

    def bu_level_selected( self, event ):
        event.Skip()

    def display_h5_inventory( self, event ):
        event.Skip()

    def click_item_in_list( self, event ):
        event.Skip()

    def exit_dragon( self, event ):
        event.Skip()

    def export_inventory( self, event ):
        event.Skip()

    def export_backorder( self, event ):
        event.Skip()

    def show_about_dialog( self, event ):
        event.Skip()

    def sync_inventory( self, event ):
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

    def display_low_AB_inventory( self, event ):
        event.Skip()

    def display_inventory_trend( self, event ):
        event.Skip()

    def select_bu_TU( self, event ):
        event.Skip()

    def select_bu_CMFT( self, event ):
        event.Skip()

    def select_bu_PT( self, event ):
        event.Skip()

    def select_bu_JT( self, event ):
        event.Skip()

    def select_bu_SP( self, event ):
        event.Skip()

    def select_bu_MT( self, event ):
        event.Skip()

    def export_listed_data( self, event ):
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


