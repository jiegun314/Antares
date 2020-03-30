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

bookdata = {
    1 : ("钢铁是怎样炼成的练成的", "2017-05-31"),
    2 : ("秦腔", "2017-04-12"), 
    3 : ("西游记", "1987-08-12")
}
###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Oneclieck Inventory Model", pos = wx.DefaultPosition, size = wx.Size( 800,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.ntbkOneclick = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_TOP )
		self.pnlOneclick = wx.Panel( self.ntbkOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer4 = wx.BoxSizer( wx.VERTICAL )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer5.SetMinSize( wx.Size( -1,40 ) )

		bSizer5.Add( ( 50, 20), 0, wx.EXPAND, 5 )

		self.m_staticText2 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Material Code:", wx.DefaultPosition, wx.Size( -1,20 ), wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText2.Wrap( -1 )

		self.m_staticText2.SetMaxSize( wx.Size( -1,30 ) )

		bSizer5.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		bSizer5.Add( ( 50, 20), 0, wx.EXPAND, 5 )

		self.txtMaterialCode = wx.TextCtrl( self.pnlOneclick, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,20 ), wx.TE_CENTER )
		self.txtMaterialCode.SetMaxSize( wx.Size( -1,30 ) )

		bSizer5.Add( self.txtMaterialCode, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		bSizer5.Add( ( 50, 20), 0, wx.EXPAND, 5 )

		self.btnSubmit = wx.Button( self.pnlOneclick, wx.ID_ANY, u"Submit", wx.DefaultPosition, wx.Size( -1,25 ), 0 )
		self.btnSubmit.SetMaxSize( wx.Size( -1,30 ) )

		bSizer5.Add( self.btnSubmit, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )


		bSizer4.Add( bSizer5, 0, wx.EXPAND, 5 )

		bSizer6 = wx.BoxSizer( wx.VERTICAL )

		bSizer6.SetMinSize( wx.Size( -1,30 ) )
		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer8.Add( ( 20, 0), 0, wx.EXPAND, 5 )

		rdbxCalculationTypeChoices = [ u"by Code", u"by Hierarchy" ]
		self.rdbxCalculationType = wx.RadioBox( self.pnlOneclick, wx.ID_ANY, u"Calculation Type", wx.DefaultPosition, wx.DefaultSize, rdbxCalculationTypeChoices, 1, wx.RA_SPECIFY_COLS )
		self.rdbxCalculationType.SetSelection( 0 )
		bSizer8.Add( self.rdbxCalculationType, 0, wx.ALL, 5 )


		bSizer8.Add( ( 50, 0), 0, wx.EXPAND, 5 )

		self.m_staticText4 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Select Date:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText4.Wrap( -1 )

		bSizer8.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer8.Add( ( 10, 0), 0, wx.EXPAND, 5 )

		self.dtpkDate = wx.adv.DatePickerCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultDateTime, wx.DefaultPosition, wx.DefaultSize, wx.adv.DP_DEFAULT )
		bSizer8.Add( self.dtpkDate, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer6.Add( bSizer8, 1, wx.EXPAND, 5 )


		bSizer4.Add( bSizer6, 0, wx.EXPAND, 5 )

		self.m_staticline1 = wx.StaticLine( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer4.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer7 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText3 = wx.StaticText( self.pnlOneclick, wx.ID_ANY, u"Result", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )

		bSizer7.Add( self.m_staticText3, 0, wx.ALL, 5 )

		self.listCtrlOutput = wx.ListCtrl( self.pnlOneclick, wx.ID_ANY, wx.DefaultPosition, wx.Size( 700,-1 ), wx.LC_REPORT )
		self.listCtrlOutput.InsertColumn(0, "ID")
		self.listCtrlOutput.InsertColumn(1, "Name")
		self.listCtrlOutput.InsertColumn(2, "Date")
		bSizer7.Add( self.listCtrlOutput, 0, wx.ALL, 5 )


		bSizer4.Add( bSizer7, 1, wx.EXPAND, 5 )


		self.pnlOneclick.SetSizer( bSizer4 )
		self.pnlOneclick.Layout()
		bSizer4.Fit( self.pnlOneclick )
		self.ntbkOneclick.AddPage( self.pnlOneclick, u"Oneclick", False )

		bSizer1.Add( self.ntbkOneclick, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
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
		self.btnSubmit.Bind( wx.EVT_BUTTON, self.codeSubmit )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def codeSubmit( self, event ):
		items = bookdata.items()
		for key, data in items:
			index = self.listCtrlOutput.InsertItem(self.listCtrlOutput.GetItemCount(), str(key))
			self.listCtrlOutput.SetItem(index, 1, data[0])
			self.listCtrlOutput.SetItem(index, 2, data[1])


