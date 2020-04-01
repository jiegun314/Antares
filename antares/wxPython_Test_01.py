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
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Oneclieck Inventory Model", pos = wx.DefaultPosition, size = wx.Size( 1024,768 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE|wx.MINIMIZE_BOX|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.ntbkOneclick = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
        self.pnlOneclick = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer4 = wx.BoxSizer( wx.VERTICAL )

        bSizer81 = wx.BoxSizer( wx.VERTICAL )

        bSizer81.SetMinSize( wx.Size( -1,30 ) )
        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )


        bSizer9.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.btnSync = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Synchronize", wx.DefaultPosition, wx.DefaultSize, wx.BORDER_NONE )
        self.btnSync.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
        self.btnSync.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

        bSizer9.Add( self.btnSync, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer9.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        rdbxBusinessUnitChoices = [ u"JOINT", u"SPINE", u"TRAUMA", u"MITEK", u"CMFT", u"PT" ]
        self.rdbxBusinessUnit = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Business Unit", wx.DefaultPosition, wx.Size( -1,-1 ), rdbxBusinessUnitChoices, 1, wx.RA_SPECIFY_ROWS )
        self.rdbxBusinessUnit.SetSelection( 2 )
        bSizer9.Add( self.rdbxBusinessUnit, 0, wx.ALL, 5 )


        bSizer9.Add( ( 50, 0), 0, wx.EXPAND, 5 )

        self.btnBUSubmit = wx.Button( self.pnlOneclick, wx.ID_ANY, u"BU Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.btnBUSubmit, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer81.Add( bSizer9, 1, wx.EXPAND, 5 )

        self.m_staticline3 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer81.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )


        bSizer4.Add( bSizer81, 0, wx.EXPAND, 5 )

        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer5.SetMinSize( wx.Size( -1,80 ) )

        bSizer5.Add( ( 10, 20), 0, wx.EXPAND, 5 )

        self.m_staticText2 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Material / H5 Name: ", wx.DefaultPosition, wx.Size( -1,20 ), 0 )
        self.m_staticText2.Wrap( -1 )

        self.m_staticText2.SetMaxSize( wx.Size( -1,30 ) )

        bSizer5.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 5, 20), 0, wx.EXPAND, 5 )

        self.txtMaterialCode = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 140,80 ), wx.TE_MULTILINE )
        bSizer5.Add( self.txtMaterialCode, 0, wx.ALL, 5 )


        bSizer5.Add( ( 20, 20), 1, wx.EXPAND, 5 )

        rdbxCalculationTypeChoices = [ u"by Code", u"by Hierarchy" ]
        self.rdbxCalculationType = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Calculation Type", wx.DefaultPosition, wx.DefaultSize, rdbxCalculationTypeChoices, 1, wx.RA_SPECIFY_ROWS )
        self.rdbxCalculationType.SetSelection( 0 )
        bSizer5.Add( self.rdbxCalculationType, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 10, 0), 1, wx.EXPAND, 5 )

        bSizer71 = wx.BoxSizer( wx.VERTICAL )

        bSizer71.SetMinSize( wx.Size( 0,60 ) )
        self.m_staticText4 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Select Date:", wx.Point( 0,0 ), wx.Size( -1,20 ), 0 )
        self.m_staticText4.Wrap( -1 )

        bSizer71.Add( self.m_staticText4, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

        self.dtpkDate = wx.adv.DatePickerCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultDateTime, wx.Point( 0,0 ), wx.Size( 100,20 ), wx.adv.DP_DEFAULT )
        bSizer71.Add( self.dtpkDate, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        bSizer5.Add( bSizer71, 0, wx.EXPAND, 5 )


        bSizer5.Add( ( 20, 0), 1, wx.EXPAND, 5 )

        self.btnSubmit = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Submit", wx.DefaultPosition, wx.Size( -1,30 ), 0 )
        self.btnSubmit.SetMaxSize( wx.Size( -1,30 ) )

        bSizer5.Add( self.btnSubmit, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


        bSizer5.Add( ( 0, 0), 1, wx.EXPAND, 5 )


        bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        bSizer6.SetMinSize( wx.Size( -1,30 ) )
        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        self.btnCurrentInventory = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Current INV", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.btnCurrentInventory, 0, wx.ALL, 5 )

        self.btnCurrentBackorder = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Current Backorder", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.btnCurrentBackorder, 0, wx.ALL, 5 )

        self.m_button5 = wx.Button( self.pnlOneclick, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button5.Hide()

        bSizer8.Add( self.m_button5, 0, wx.ALL, 5 )

        self.m_button6 = wx.Button( self.pnlOneclick, wx.ID_ANY, u"MyButton", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_button6.Hide()

        bSizer8.Add( self.m_button6, 0, wx.ALL, 5 )


        bSizer8.Add( ( 20, 0), 0, wx.EXPAND, 5 )

        self.m_staticText41 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Log:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText41.Wrap( -1 )

        bSizer8.Add( self.m_staticText41, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

        self.txtLog = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 600,-1 ), wx.TE_CENTER|wx.TE_READONLY|wx.BORDER_SUNKEN )
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

        self.listCtrlOutput = wx.ListCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 950,-1 ), wx.LC_REPORT )
        bSizer7.Add( self.listCtrlOutput, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


        bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )


        self.pnlOneclick.SetSizer( bSizer4 )
        self.pnlOneclick.Layout()
        bSizer4.Fit( self.pnlOneclick )
        self.ntbkOneclick.AddPage( self.pnlOneclick, u"Oneclick", False )

        bSizer1.Add( self.ntbkOneclick, 1, wx.EXPAND |wx.ALL, 5 )


        self.SetSizer( bSizer1 )
        self.Layout()
        self.m_statusBar1 = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
        self.m_menubar1 = wx.MenuBar( 0 )
        self.m_menu1 = wx.Menu()
        self.m_menuItem1 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Open", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.m_menuItem1 )

        self.m_menuItem2 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu1.Append( self.m_menuItem2 )

        self.m_menubar1.Append( self.m_menu1, u"File" )

        self.m_menu2 = wx.Menu()
        self.m_menuItem3 = wx.MenuItem( self.m_menu2, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
        self.m_menu2.Append( self.m_menuItem3 )

        self.m_menubar1.Append( self.m_menu2, u"About" )

        self.SetMenuBar( self.m_menubar1 )


        self.Centre( wx.BOTH )

        # Connect Events
        self.btnBUSubmit.Bind( wx.EVT_BUTTON, self.bu_submit )
        self.btnSubmit.Bind( wx.EVT_BUTTON, self.codeSubmit )
        self.btnCurrentInventory.Bind( wx.EVT_BUTTON, self.get_current_inventory_list )
        self.btnCurrentBackorder.Bind( wx.EVT_BUTTON, self.get_current_bo_list )
        self.btnSync.Bind(wx.EVT_BUTTON, self.sync_inventory)

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def bu_submit( self, event ):
        event.Skip()

    def codeSubmit( self, event ):
        event.Skip()

    def get_current_inventory_list( self, event ):
        event.Skip()

    def get_current_bo_list( self, event ):
        event.Skip()

    def sync_inventory(self, event):
        event.Skip()
