# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui
import wx.dataview
import wx.html

###########################################################################
## Class mainFrame
###########################################################################

class mainFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"QUAREP-LiMi Tool Kit", pos = wx.DefaultPosition, size = wx.Size( 598,364 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )

		m_mainSizer = wx.BoxSizer( wx.VERTICAL )

		self.m_toolbar = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT )
		self.m_toolbar.SetToolBitmapSize( wx.Size( 32,32 ) )
		self.m_toolbar.Realize()

		m_mainSizer.Add( self.m_toolbar, 0, wx.ALL, 5 )

		self.m_mainPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		m_panelSizer = wx.BoxSizer( wx.VERTICAL )


		self.m_mainPanel.SetSizer( m_panelSizer )
		self.m_mainPanel.Layout()
		m_panelSizer.Fit( self.m_mainPanel )
		m_mainSizer.Add( self.m_mainPanel, 1, wx.EXPAND |wx.ALL, 0 )


		self.SetSizer( m_mainSizer )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


###########################################################################
## Class formBrowse
###########################################################################

class formBrowse ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 565,378 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		m_pageSizer = wx.BoxSizer( wx.VERTICAL )

		self.m_mainSplitter = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.m_mainSplitter.SetSashGravity( 0 )
		self.m_mainSplitter.Bind( wx.EVT_IDLE, self.m_mainSplitterOnIdle )

		self.m_leftPanel = wx.Panel( self.m_mainSplitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		m_leftSizer = wx.BoxSizer( wx.VERTICAL )

		self.m_panel6 = wx.Panel( self.m_leftPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.BORDER_SIMPLE|wx.TAB_TRAVERSAL )
		bSizer20 = wx.BoxSizer( wx.VERTICAL )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_folder = wx.StaticText( self.m_panel6, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_folder.Wrap( -1 )

		bSizer17.Add( self.m_folder, 1, wx.ALL, 5 )

		self.m_browse = wx.Button( self.m_panel6, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 40,20 ), 0 )
		bSizer17.Add( self.m_browse, 0, wx.RIGHT|wx.TOP, 2 )


		bSizer20.Add( bSizer17, 0, wx.EXPAND, 5 )

		self.m_treeDevices = wx.TreeCtrl( self.m_panel6, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT|wx.TR_LINES_AT_ROOT|wx.TR_NO_LINES|wx.TR_SINGLE|wx.TR_TWIST_BUTTONS|wx.BORDER_NONE )
		bSizer20.Add( self.m_treeDevices, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		self.m_panel6.SetSizer( bSizer20 )
		self.m_panel6.Layout()
		bSizer20.Fit( self.m_panel6 )
		m_leftSizer.Add( self.m_panel6, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_treeDates = wx.dataview.TreeListCtrl( self.m_leftPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.TL_DEFAULT_STYLE )

		m_leftSizer.Add( self.m_treeDates, 1, wx.EXPAND |wx.ALL, 5 )


		self.m_leftPanel.SetSizer( m_leftSizer )
		self.m_leftPanel.Layout()
		m_leftSizer.Fit( self.m_leftPanel )
		self.m_mainSplitter.Initialize( self.m_leftPanel )
		m_pageSizer.Add( self.m_mainSplitter, 1, wx.EXPAND, 5 )


		self.SetSizer( m_pageSizer )
		self.Layout()

		# Connect Events
		self.m_browse.Bind( wx.EVT_BUTTON, self.m_browseOnButtonClick )
		self.m_treeDevices.Bind( wx.EVT_TREE_SEL_CHANGED, self.m_treeDevicesOnTreeSelChanged )
		self.m_treeDates.Bind( wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.m_treeDatesOnTreelistSelectionChanged )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def m_browseOnButtonClick( self, event ):
		event.Skip()

	def m_treeDevicesOnTreeSelChanged( self, event ):
		event.Skip()

	def m_treeDatesOnTreelistSelectionChanged( self, event ):
		event.Skip()

	def m_mainSplitterOnIdle( self, event ):
		self.m_mainSplitter.SetSashPosition( 300 )
		self.m_mainSplitter.Unbind( wx.EVT_IDLE )


###########################################################################
## Class formMeasure
###########################################################################

class formMeasure ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		m_pageSizer = wx.BoxSizer( wx.VERTICAL )

		bSizer40 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Microscope Brand:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		bSizer40.Add( self.m_staticText1, 0, wx.ALL, 5 )

		m_brandChoiceChoices = [ u"please select microscope brand", u"Evident/Olympus", u"Leica", u"Nikon", u"Zeiss" ]
		self.m_brandChoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_brandChoiceChoices, 0 )
		self.m_brandChoice.SetSelection( 0 )
		bSizer40.Add( self.m_brandChoice, 0, wx.ALL, 5 )


		m_pageSizer.Add( bSizer40, 0, wx.EXPAND, 5 )

		self.m_mainPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		m_mainSizer = wx.BoxSizer( wx.VERTICAL )


		self.m_mainPanel.SetSizer( m_mainSizer )
		self.m_mainPanel.Layout()
		m_mainSizer.Fit( self.m_mainPanel )
		m_pageSizer.Add( self.m_mainPanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( m_pageSizer )
		self.Layout()

		# Connect Events
		self.m_brandChoice.Bind( wx.EVT_CHOICE, self.m_brandChoiceOnChoice )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def m_brandChoiceOnChoice( self, event ):
		event.Skip()


###########################################################################
## Class panelTwoPanes
###########################################################################

class panelTwoPanes ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		rightSizer = wx.BoxSizer( wx.VERTICAL )

		self.m_rightTopPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		m_rightTopSizer = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )


		self.m_rightTopPanel.SetSizer( m_rightTopSizer )
		self.m_rightTopPanel.Layout()
		m_rightTopSizer.Fit( self.m_rightTopPanel )
		rightSizer.Add( self.m_rightTopPanel, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_rightMainPanel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.m_rightMainPanel.SetScrollRate( 5, 5 )
		m_rightMainSizer = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )


		self.m_rightMainPanel.SetSizer( m_rightMainSizer )
		self.m_rightMainPanel.Layout()
		m_rightMainSizer.Fit( self.m_rightMainPanel )
		rightSizer.Add( self.m_rightMainPanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( rightSizer )
		self.Layout()

		# Connect Events
		self.Bind( wx.EVT_SIZE, self.panelTwoPanesOnSize )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def panelTwoPanesOnSize( self, event ):
		event.Skip()


###########################################################################
## Class formHelp
###########################################################################

class formHelp ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer9 = wx.BoxSizer( wx.VERTICAL )

		self.m_htmlHelp = wx.html.HtmlWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.html.HW_SCROLLBAR_AUTO )
		bSizer9.Add( self.m_htmlHelp, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer9 )
		self.Layout()

	def __del__( self ):
		pass


###########################################################################
## Class panelNoiseBrightness
###########################################################################

class panelNoiseBrightness ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 699,68 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer10 = wx.BoxSizer( wx.VERTICAL )

		headerSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_lblToggle = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 35,-1 ), 0 )
		self.m_lblToggle.Wrap( -1 )

		headerSizer.Add( self.m_lblToggle, 0, wx.ALL, 5 )

		self.m_lblName = wx.StaticText( self, wx.ID_ANY, u"name", wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		self.m_lblName.Wrap( -1 )

		self.m_lblName.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblName, 0, wx.ALL, 5 )

		self.m_lblConditions = wx.StaticText( self, wx.ID_ANY, u"conditions", wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_lblConditions.Wrap( -1 )

		self.m_lblConditions.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblConditions, 0, wx.ALL, 5 )

		self.m_lblStart = wx.StaticText( self, wx.ID_ANY, u"analyze", wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
		self.m_lblStart.Wrap( -1 )

		self.m_lblStart.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblStart, 0, wx.ALL, 5 )

		self.m_lblBackground = wx.StaticText( self, wx.ID_ANY, u"background", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_lblBackground.Wrap( -1 )

		self.m_lblBackground.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblBackground, 0, wx.ALL, 5 )

		self.m_lblGain = wx.StaticText( self, wx.ID_ANY, u"gain", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_lblGain.Wrap( -1 )

		self.m_lblGain.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblGain, 0, wx.ALL, 5 )

		self.m_lblNoise = wx.StaticText( self, wx.ID_ANY, u"noise", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_lblNoise.Wrap( -1 )

		self.m_lblNoise.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblNoise, 0, wx.ALL, 5 )

		self.m_lblCapacity = wx.StaticText( self, wx.ID_ANY, u"capacity", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_lblCapacity.Wrap( -1 )

		self.m_lblCapacity.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblCapacity, 0, wx.ALL, 5 )

		self.m_lblLinearity = wx.StaticText( self, wx.ID_ANY, u"linearity", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_lblLinearity.Wrap( -1 )

		self.m_lblLinearity.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		headerSizer.Add( self.m_lblLinearity, 0, wx.ALL, 5 )


		bSizer10.Add( headerSizer, 0, wx.EXPAND, 5 )

		dataSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_btnExpand = wx.ToggleButton( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 35,20 ), wx.CHK_2STATE )
		dataSizer.Add( self.m_btnExpand, 0, wx.ALL, 5 )

		self.m_name = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		self.m_name.Wrap( -1 )

		dataSizer.Add( self.m_name, 0, wx.ALL, 5 )

		self.m_conditions = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		self.m_conditions.Wrap( -1 )

		dataSizer.Add( self.m_conditions, 0, wx.ALL, 5 )

		self.m_btnStart = wx.ToggleButton( self, wx.ID_ANY, u"Start", wx.DefaultPosition, wx.Size( 50,-1 ), 0 )
		dataSizer.Add( self.m_btnStart, 0, wx.ALL, 5 )

		self.m_background = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_background.Wrap( -1 )

		dataSizer.Add( self.m_background, 0, wx.ALL, 5 )

		self.m_gain = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_gain.Wrap( -1 )

		dataSizer.Add( self.m_gain, 0, wx.ALL, 5 )

		self.m_noise = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_noise.Wrap( -1 )

		dataSizer.Add( self.m_noise, 0, wx.ALL, 5 )

		self.m_capacity = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_capacity.Wrap( -1 )

		dataSizer.Add( self.m_capacity, 0, wx.ALL, 5 )

		self.m_linearity = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		self.m_linearity.Wrap( -1 )

		dataSizer.Add( self.m_linearity, 0, wx.ALL, 5 )


		bSizer10.Add( dataSizer, 0, wx.EXPAND, 5 )

		m_graphSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_graphPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		wSizer3 = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )


		self.m_graphPanel.SetSizer( wSizer3 )
		self.m_graphPanel.Layout()
		wSizer3.Fit( self.m_graphPanel )
		m_graphSizer.Add( self.m_graphPanel, 1, wx.EXPAND |wx.ALL, 5 )


		bSizer10.Add( m_graphSizer, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer10 )
		self.Layout()

	def __del__( self ):
		pass


###########################################################################
## Class panelWithSlider
###########################################################################

class panelWithSlider ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 175,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer14 = wx.BoxSizer( wx.VERTICAL )

		fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer1.AddGrowableCol( 1 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_name = wx.StaticText( self, wx.ID_ANY, u"bright", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_name.Wrap( -1 )

		fgSizer1.Add( self.m_name, 0, wx.ALIGN_TOP|wx.LEFT|wx.RIGHT, 5 )

		self.m_slider = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		fgSizer1.Add( self.m_slider, 0, wx.ALL|wx.EXPAND, 0 )


		bSizer14.Add( fgSizer1, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer14 )
		self.Layout()

		# Connect Events
		self.m_slider.Bind( wx.EVT_SCROLL, self.m_sliderOnScroll )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def m_sliderOnScroll( self, event ):
		event.Skip()


###########################################################################
## Class formDetectorPhotonCalibration
###########################################################################

class formDetectorPhotonCalibration ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Detector Photon Calibration", pos = wx.DefaultPosition, size = wx.Size( 314,263 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )

		fgSizer2 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )


		bSizer16.Add( fgSizer2, 1, wx.EXPAND, 5 )

		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_button1 = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_button1, 0, wx.ALL, 5 )


		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_btnOK = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_btnOK.SetDefault()
		bSizer18.Add( self.m_btnOK, 0, wx.ALL, 5 )


		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer16.Add( bSizer18, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.m_btnOK.Bind( wx.EVT_BUTTON, self.m_btnOKOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def m_btnOKOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class panelNone
###########################################################################

class panelNone ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer18 = wx.BoxSizer( wx.VERTICAL )

		self.m_text = wx.StaticText( self, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_text.Wrap( -1 )

		bSizer18.Add( self.m_text, 1, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer18 )
		self.Layout()

	def __del__( self ):
		pass


