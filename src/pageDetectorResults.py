#import csv
import math
import sys
import os
import locale
import re
import csv
from datetime import datetime
from pathlib import Path, WindowsPath
import tempfile

import win32security
import win32api
import wx.lib.agw.persist as PM
import wx.grid
import wxmplot
import matplotlib.pyplot as mpl;
import subprocess

from FolderWatch import *  # requires pyWin32
from forms import *
from wxApp import *
from DetectorPhotonCalibration import *

import ctypes
from ctypes import wintypes as w

import math
import os
import glob
import logging
import numpy as np

# The pyvips module does not include the libvips binaries: they must be installed separately
#vipshome = r'L:\local\Tools\libvips\vips-dev-8.15\bin'
vipshome = os.path.join(os.path.dirname(__file__), "vips")
os.environ['PATH'] = vipshome + ';' + os.environ['PATH']
import pyvips
logging.info("vips version: " + str(pyvips.version(0))+"."+str(pyvips.version(1))+"."+str(pyvips.version(2)))

# the noise brightness analysis generates images with size (1023,590).
# show them scaled with g_widgetScale/10.
g_widgetScale = 3.
def get_widget_scale():
    return g_widgetScale
def get_widget_size():
    return wx.Size((1023*g_widgetScale)/10,(590*g_widgetScale)/10)

#import wx.svg
# the wx.svg module renders svg files poorly: use the lunasvg library instead
# todo: wrap this in a wx.lunaSvg pacakge
lunasvgpath = os.path.join(os.path.dirname(__file__), r"lunasvg\lunasvg.dll")
lunasvg = ctypes.cdll.LoadLibrary(lunasvgpath)
svg2png = lunasvg.svg2png
svg2png.restype = ctypes.c_long
svg2png.argtypes = [ctypes.c_wchar_p,ctypes.c_double,ctypes.c_double,ctypes.c_uint32,ctypes.c_wchar_p]
lunasvg_tmpdir = tempfile.TemporaryDirectory()
lunasvg_tmppng = os.path.join(lunasvg_tmpdir.name,"tmp.png")
def loadSvg(svg, width, height, backgroundcolor):
    lunasvg.svg2png(svg,width,height,backgroundcolor,lunasvg_tmppng)
    return wx.Bitmap(lunasvg_tmppng, wx.BITMAP_TYPE_ANY)

def dictToTooltip(dict):
    text = ""
    for key in dict.keys():
        text += key + "\t" + dict[key] + "\n"
    return text

class SvgImage(wx.StaticBitmap):
    def __init__( self, parent, id = wx.ID_ANY, svg_filename = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style=0, name = wx.StaticBitmapNameStr ):
        self.bitmap = wx.NullBitmap
        if len(svg_filename):
            self.svg_filename = svg_filename
            self.bitmap = loadSvg(self.svg_filename,get_widget_scale()/10.,-1,0xFFFFFFFF)# a height of -1 means that width is a scale
        wx.StaticBitmap.__init__ ( self, parent, id, self.bitmap, pos,  self.bitmap.GetSize(),  style, name )

class SvgPhotonCalibrationImage(wx.StaticBitmap):
    def __init__( self, parent, id = wx.ID_ANY, svg_filename = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style=0, name = wx.StaticBitmapNameStr ):
        self.bitmap = wx.NullBitmap
        if len(svg_filename):
            self.svg_filename = svg_filename
            bitmap = loadSvg(self.svg_filename,get_widget_scale()/10.,-1,0xFFFFFFFF)# a height of -1 means that width is a scale
            size = bitmap.GetSize()
            if size.x > size.y:
                margin = size.y * 50 / 100
                bitmap = bitmap.GetSubBitmap(wx.Rect(margin,0,size.x-margin, size.y))
            self.bitmap = bitmap
        wx.StaticBitmap.__init__ ( self, parent, id, self.bitmap, pos,  self.bitmap.GetSize(),  style, name )


# the text frame is shown to display the info.txt file
class TextFrame(wx.TextCtrl):

    def __init__(self, parent, title, txtfile):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                             wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_RICH | wx.WANTS_CHARS)  # |wx.TAB_TRAVERSAL)
        self.txtfile = txtfile
        self.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Calibri'))
        # set tab width
        pixel_width_in_mm = 25.4 / wx.ScreenDC().GetPPI()[0]
        space_width_in_pixels = self.GetTextExtent(" ")[0]
        tab_width_in_tenth_of_mm = (40 * 10 * space_width_in_pixels * pixel_width_in_mm)
        attr = wx.TextAttr()
        attr.SetTabs([tab_width_in_tenth_of_mm])
        self.SetDefaultStyle(attr)
        wx.TextCtrl.SetEditable(self, True)
        wx.TextCtrl.SetModified(self, False)
        self.SetMinSize(wx.Size(space_width_in_pixels*110,get_widget_size().height))
        self.LoadFile(str(self.txtfile))

    def IsModified(self):
        modified = wx.TextCtrl.IsModified(self)
        return modified

    def SaveModified(self):
        if self.IsModified():
            self.SaveFile(str(self.txtfile))

class ResultsFrame(wx.TextCtrl):

    def __init__(self, parent, title, txtfile):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                             wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_RICH | wx.TE_READONLY)  # |wx.TAB_TRAVERSAL)
        self.txtfile = txtfile
        self.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Calibri'))
        # set tab width
        pixel_width_in_mm = 25.4 / wx.ScreenDC().GetPPI()[0]
        space_width_in_pixels = self.GetTextExtent(" ")[0]
        tab_width_in_tenth_of_mm = (80 * 10 * space_width_in_pixels * pixel_width_in_mm)
        attr = wx.TextAttr()
        attr.SetTabs([tab_width_in_tenth_of_mm])
        self.SetDefaultStyle(attr)
        with open(txtfile) as file:
            for line in file:
                if len(line) and line[0] != '#':
                    # quated vfilealues
                    match = re.match("(.*): '(.+?)'",line)
                    if match:
                        key = match.groups()[0]
                        value = match.groups()[1]
                        self.WriteText(key + "\t" + value + "\n")
                    else:
                        match = re.match("(.*): (.+)", line)
                        if match:
                            key = match.groups()[0]
                            value = match.groups()[1]
                            self.WriteText(key + "\t" + value + "\n")
        self.SetMinSize(wx.Size(space_width_in_pixels*110,get_widget_size().height))


class TiffFrame(wx.StaticBitmap):

    def __init__(self, parent, title, filename):
        self.filename = filename
        """ build in wx tiff support cannot handle mono 16-bits images
        self.tiff = wx.Image()
        noLog = wx.LogNull()
        count = self.tiff.GetImageCount(filename,wx.BITMAP_TYPE_TIFF)
        self.tiff.LoadFile(filename,wx.BITMAP_TYPE_TIFF, 0)
        width = self.tiff.GetWidth()
        height = self.tiff.GetHeight()
        del noLog
        #data = self.tiff.GetDataBuffer()
        self.bitmap = self.tiff.ConvertToBitmap()
        wx.StaticBitmap.__init__ ( self, parent, wx.ID_ANY, self.bitmap, wx.DefaultPosition,  get_widget_size(), 0, wx.StaticBitmapNameStr)
        """
        image = pyvips.Image.tiffload(filename, page=0).scaleimage()
        rgba = image.colourspace("srgb")
        data = np.asarray(rgba)
        bitmap = wx.Bitmap.FromBuffer(image.width,image.height,data)
        size = get_widget_size()
        size.width = (image.width * size.height) / image.height
        wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, bitmap, wx.DefaultPosition, size, 0, wx.StaticBitmapNameStr)


class MultiPageTiffFrame(panelWithSlider):

    def __init__(self, parent, title, filename):
        panelWithSlider.__init__(self, parent)
        self.filename = filename
        self.m_name.SetLabel(os.path.basename(filename))
        self.pages = 1
        self.LoadPage(0)
        self.m_slider.SetRange(0,self.pages-1)
        self.m_slider.SetValue(0)
        wxResizePanelToContent(self)

    def LoadPage(self,page):
        image = pyvips.Image.tiffload(self.filename, page=page).scaleimage()
        self.pages = image.get("n-pages")
        rgba = image.colourspace("srgb")
        data = np.asarray(rgba)
        bitmap = wx.Bitmap.FromBuffer(image.width,image.height,data)
        size = get_widget_size()
        slider_height = self.m_slider.GetSize().height
        size.height -= slider_height
        size.width = (image.width * size.height) / image.height
        self.bitmap = wx.StaticBitmap(self, wx.ID_ANY, bitmap, wx.DefaultPosition, size, 0, wx.StaticBitmapNameStr)
        self.GetSizer().Insert(0, self.bitmap)
        self.Layout()
        del rgba
        del data
        del image

    def m_sliderOnScroll(self, event):
        self.Freeze()
        page = self.m_slider.GetValue()
        self.bitmap.Destroy()
        del self.bitmap
        self.LoadPage(page)
        self.Thaw()


# the info file has on every line <key><tab><value>
def ReadInfo(file):
    reader = csv.reader(open(file,), delimiter='\t', quoting=csv.QUOTE_NONE)
    info = {}
    for line in reader:
        full_line = ' '.join(line)
        match = re.match(r"\s*([^:]+):\s*(.+)",full_line)
        if match:
            key = match.groups()[0]
            value = match.groups()[1]
            if key and value:
                info[key] = value
    return info

# the results file has on every line <key>:  <value>
def ReadResults(file):
    reader = csv.reader(open(file,), delimiter=':', quoting=csv.QUOTE_NONE)
    results = {}
    for line in reader:
        if len(line) > 1:
            key = line.pop(0)
            results[key] = ' '.join(line).strip(" '")
    return results

# panelDetectorResults is a panel with two sizers: a top one for buttons/filters, a main one for the results
# the difference with panel in pageDetectorResults is that this one has a FlexGridSizer in the main panel
class panelDetectorResults ( wx.Panel ):

    def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
        wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )
        self.m_folder = ""
        self.m_autoProcess = wxGetApp().config.ReadInt("detectorAutoProcess", 1)

        rightSizer = wx.BoxSizer( wx.VERTICAL )

        self.m_rightTopPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        m_rightTopSizer = wx.WrapSizer( wx.HORIZONTAL, wx.WRAPSIZER_DEFAULT_FLAGS )

        self.m_rightTopPanel.SetSizer( m_rightTopSizer )
        self.m_rightTopPanel.Layout()
        m_rightTopSizer.Fit( self.m_rightTopPanel )
        rightSizer.Add( self.m_rightTopPanel, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_rightMainPanel = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
        self.m_rightMainPanel.SetScrollRate( 5, 5 )
        m_rightMainSizer = wx.FlexGridSizer(0, 1, 0, 0)
        m_rightMainSizer.AddGrowableCol(0)
        m_rightMainSizer.SetFlexibleDirection(wx.BOTH)
        m_rightMainSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_rightMainPanel.SetSizer( m_rightMainSizer )
        self.m_rightMainPanel.Layout()
        m_rightMainSizer.Fit( self.m_rightMainPanel )
        rightSizer.Add( self.m_rightMainPanel, 1, wx.EXPAND |wx.ALL, 5 )

        self.SetSizer( rightSizer )
        self.Layout()

        # Connect Events
        self.Bind( wx.EVT_SIZE, self.panelDetectorResultsOnSize )

    def __del__( self ):
        pass

    # Virtual event handlers, override them in your derived class
    def panelDetectorResultsOnSize( self, event ):
        event.Skip()

# a 'Widget' shows all results in a sub-folder. Images are scaled with g_widgetScale/10.0
# the Noise Analysis Script creates bitmaps with size (1023,590), so that is the origin.
# when the scale is changed, all widgets are recreated

class pageDetectorResults(panelDetectorResults):

    def __init__(self, formBrowse, parent):
        panelDetectorResults.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'pageDetectorResults')
        self.m_parent = formBrowse
        self.widgets = {}
        self.widget_state = {}
        self.deviceFolder = ""
        self.deviceDate = ""
        self.dateTi = None
        self.dates = set()
        self.m_buttonPanel = self.m_rightTopPanel
        self.m_buttonSizer = self.m_rightTopPanel.GetSizer()
        # the filter states stores which graphs are visible
        self.filterState = {}
        self.ReadFilterStates()
        self.filters = {}
        self.SetWidgetScale(wxGetApp().config.Read("detectorWidgetScale"))
        self.InitTrees()
        self.timer = wx.Timer(self,1)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(1000)

    def onDestroy(self):
        self.timer.Stop()
        self.Unbind(wx.EVT_TIMER)
        del self.timer

    def ReadFilterStates(self):
        states = wxGetApp().config.Read("detectorFilterStates")
        for s in states.split(';'):
            key_value = s.split(':')
            if len(key_value) == 2:
                self.filterState[key_value[0]] = int(key_value[1])

    def WriteFilterStates(self):
        tmp = ""
        for key in self.filterState.keys():
            tmp += key + ":" + str(int(self.filterState[key])) + ";"
        wxGetApp().config.Write("detectorFilterStates",tmp)

    def m_toolAlgorithmClicked(self,event):
        win32api.ShellExecute(0, "open", os.path.join(os.path.dirname(__file__), r"caltool\Algorithm.pdf"), None, ".", 1)

    def m_toolReadmeClicked(self,event):
        win32api.ShellExecute(0, "open", os.path.join(os.path.dirname(__file__), r"caltool\readme.txt"), None, ".", 1)

    def SetWidgetScale(self, scale):
        try:
            scale = int(scale)
        except:
            return
        if scale < 1:
            scale = 1
        if scale > 10:
            scale = 10
        global g_widgetScale
        g_widgetScale = scale

    def ChangeWidgetScale(self, direction):
        if direction < 0:
            self.SetWidgetScale(g_widgetScale + 1)
        if direction > 0:
            self.SetWidgetScale(g_widgetScale - 1)

    def m_toolBiggerClicked(self, event):
        self.ChangeWidgetScale(-1)
        self.m_treeDatesOnTreelistSelectionChanged(None)
        wxGetApp().config.Write("detectorWidgetScale", str(get_widget_scale()))

    def m_toolSmallerClicked(self, event):
        self.ChangeWidgetScale(1)
        self.m_treeDatesOnTreelistSelectionChanged(None)
        wxGetApp().config.Write("detectorWidgetScale", str(get_widget_scale()))

    def m_toolProcessAllClicked(self,event):
        for widget in self.widgets.values():
            self.autoProcess(widget)

    def m_toolAutoProcessClicked(self,event):
        self.m_autoProcess = self.m_btnAuto.GetValue()
        wxGetApp().config.WriteInt("detectorAutoProcess", self.m_autoProcess)

    def SetFilterCategory(self, filter, graph):
        if filter not in self.filterState.keys():
            self.filterState[filter] = 1
        if filter not in self.filters.keys():
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, filter)
            button.SetValue(self.filterState[filter])
            self.m_buttonSizer.Add(button, 0, wx.ALL, 5)
            self.filters[filter] = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onFilterToggle)
        graph.category = filter
        graph.GetParent().GetSizer().Show(graph,self.filterState[filter])

    def onFilterToggle(self, event):
        self.Freeze()
        category = event.EventObject.GetLabel()
        show = event.EventObject.GetValue()
        self.filterState[category] = show
        self.WriteFilterStates()
        for name in self.widgets:
            widget = self.widgets[name]
            graphs = widget.m_graphPanel
            sizer = graphs.GetSizer()
            for graph in graphs.GetChildren():
                if graph.category == category:
                    sizer.Show(graph,show)
            wxResizePanelToContent(graphs)
            wxResizePanelToContent(widget)

        wxResizePanelToContent(self.m_rightMainPanel) # the panelNoiseBrightness panel must be resized to show all content
        self.m_rightMainPanel.GetParent().Layout() # this makes the scrolled window show the scrollbars
        self.Thaw()

    def InitTrees(self):
        tree = self.m_parent.m_treeDates
        tree.DeleteAllItems()
        tree.ClearColumns()
        tree.AppendColumn("Dates")

    def onSelectDevice(self, ti):
        tree = self.m_parent.m_treeDevices
        data = tree.GetItemData(ti)
        folder = data["folder"]
        self.m_parent.m_treeDates.DeleteAllItems()
        self.deviceFolder = folder
        self.dates = set()
        for file in os.listdir(folder):
            date = re.search(r"^\d\d\d\d\d\d\d\d", file)
            if date is not None:
                self.dates.add(date.group())
        tree = self.m_parent.m_treeDates
        root = tree.GetRootItem()
        last_date = None
        self.dateTi = None
        for date in sorted(self.dates):
            ti = tree.AppendItem(root, date)
            tree.SetItemData(ti, {'folder': folder, 'date': date})
            last_date = ti
        if last_date is not None:
            tree.Select(last_date)
        self.onSelectDate(last_date)

    def m_treeDatesOnTreelistSelectionChanged(self, event):
        if event != None:
            event.Skip()
        tree = self.m_parent.m_treeDates
        ti = tree.GetSelection()
        self.onSelectDate(ti)

    def onSelectDate(self, ti):
        self.saveModified(wx.YES_NO)
        tree = self.m_parent.m_treeDates

        wait = wx.BusyCursor()
        self.Freeze()
        panel = self.m_rightMainPanel
        panel.DestroyChildren()
        self.widgets.clear()
        self.widget_sizer = panel.GetSizer()
        self.widget_sizer.Clear()
        self.button_panel = self.m_rightTopPanel
        self.button_panel.DestroyChildren()
        self.button_sizer = self.m_rightTopPanel.GetSizer()
        self.button_sizer.Clear()
        self.filters = {}
        panel.GetParent().Layout()

        self.dateTi = ti

        # button = wx.Button( self.m_buttonPanel, wx.ID_ANY, u"Print")
        # button.Bind(wx.EVT_BUTTON, self.onPrint)
        # button_sizer.Add(button, 0, wx.ALL, 5)
        self.zoom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.zoom_sizer, 0, 0, 0)
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "<>")
        button_size = button.GetDefaultSize(self)
        button.Destroy()

        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "Algorithm", wx.DefaultPosition, button_size)
        button.Layout()
        button.SetToolTip("Open Algorithm.pdf")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolAlgorithmClicked)
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "Read Me", wx.DefaultPosition, button_size)
        button.Layout()
        button.SetToolTip("Open ReadMe.txt")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolReadmeClicked)

        button_size.x /= 2
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "<>", wx.DefaultPosition, button_size)
        button.Layout()
        button.SetToolTip("make the graphs larger")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolBiggerClicked)
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "><", wx.DefaultPosition, button_size)
        button.SetToolTip("make the graphs smaller")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolSmallerClicked)
        button_size.x *= 2
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "Process All", wx.DefaultPosition, button_size)
        button.SetToolTip("Process all pending data")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolProcessAllClicked)
        button = wx.CheckBox(self.m_buttonPanel, wx.ID_ANY, "Auto Process", wx.DefaultPosition, button_size)
        button.SetToolTip("Automatically process new data")
        button.SetValue(self.m_autoProcess)
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_CHECKBOX, self.m_toolAutoProcessClicked)
        self.m_btnAuto = button
        
        if ti is not None:
            name = tree.GetItemText(ti)
            item_data = tree.GetItemData(ti)
            self.m_folder = Path(item_data['folder'])
            self.deviceDate = item_data['date']
            for o in os.listdir(self.m_folder):
                folder = os.path.join(self.m_folder, o)
                if o.startswith(self.deviceDate) and os.path.isdir(folder):
                    self.AddWidget(folder, o)

        panel.GetParent().Layout()

        for name in self.widget_state:
            if name in self.widgets:
                self.ExpandWidget(self.widgets[name])

        if self.CheckLabels():
            wxResizePanelToContent(panel)  # the m_graphPanel panel must be resized to show all content
            wxResizePanelToContent(self.m_rightMainPanel)  # the right panel must be resized to show all content
            self.m_rightMainPanel.GetParent().Layout()  # this makes the scrolled window show the scrollbars

        self.Thaw()
        del wait

    def AddDate(self, date):
        if date in self.dates:
            return
        self.dates.add(date)
        tree = self.m_parent.m_treeDates
        root = tree.GetRootItem()
        ti = tree.AppendItem(root, date)
        tree.SetItemData(ti, {'folder': self.m_folder, 'date': date})
        tree.Select(ti)
        self.onSelectDate(ti)

    def AddWidget(self, folder, name):
        widget = panelNoiseBrightness(self.m_rightMainPanel)
        self.widgets[name] = widget
        widget.name = name
        widget.delayedUpdate = 0
        widget.m_folder = folder
        widget.m_bright = "bright.tif"
        widget.m_dark = "dark.tif"
        widget.m_args = ""
        widget.m_btnExpand.SetBitmap(wxGetApp().LoadBitmap("RightArrow.png"))
        widget.m_btnExpand.SetBitmapPressed(wxGetApp().LoadBitmap("DownArrow.png"))
        widget.m_btnExpand.Bind(wx.EVT_TOGGLEBUTTON, self.m_btnExpandOnButtonClick)
        widget.m_btnStart.SetValue(0)
        widget.m_btnStart.Bind(wx.EVT_TOGGLEBUTTON, self.m_btnStartOnButtonClick)
        self.widget_sizer.Add(widget, 1, wx.EXPAND | wx.ALL, 0)
        self.UpdateWidget(widget)

    def SetInfoText(self, control, dict, keys, add_key=0):
        values = []
        for key in keys:
            if key in dict.keys():
                if add_key:
                    values.append(key + ": " + dict[key])
                else:
                    values.append(dict[key])
        control.SetLabel(', '.join(values))

    def UpdateWidget(self,widget):
        widget.m_info = {}
        infopath = os.path.join(widget.m_folder, "info.txt")
        brightpath = os.path.join(widget.m_folder, "bright.tif")
        if not os.path.isfile(brightpath):
            brightpath = os.path.join(widget.m_folder, "bright.ome.tif")
        # use nd2info to create info.txt
        if not os.path.isfile(infopath) and os.path.isfile(brightpath):
            nd2info = os.path.join(os.path.dirname(__file__), r"NkNd2Info\NkNd2Info.exe")
            if os.path.isfile(nd2info):
                args = [nd2info, 'textinfo', brightpath]
                r = subprocess.run(args, capture_output=True)
                info = r.stdout.decode("utf-8")
                info = info.replace(r"\r\n", "\n")
                info = info.replace(r"\r", "")
                info = info.replace(r'"', "")
                info = info.replace(r"{", "")
                info = info.replace(r"}", "")
                info = info.replace(r"\t", "\t")
                info = info.replace("\tPMT Offset", "\nPMT Offset")
                with open(infopath, 'w', encoding='utf-8') as file:
                    file.write(info)
        if os.path.exists(infopath):
            widget.m_info = ReadInfo(infopath)
        widget.m_results = {}
        path = os.path.join(widget.m_folder, "calibration_results.txt")
        if os.path.exists(path):
            widget.m_results = ReadResults(path)
        widget.m_name.SetLabel(widget.name)
        self.SetInfoText(widget.m_conditions,widget.m_info,('Exposure','Mode','Dwell Time', 'Gain', 'PMT HV'),1)
        widget.m_conditions.SetToolTip(dictToTooltip(widget.m_info))
        self.SetInfoText(widget.m_background,widget.m_results,('Background [ADU]',))
        gain = ""
        if 'Gain [e- / ADU]' in widget.m_results.keys():
            gain = widget.m_results['Gain [e- / ADU]']
            try:
                gain = "{:.2f}".format(1.0 / float(gain))
            except:
                pass
        widget.m_gain.SetLabel(gain)
        #self.SetInfoText(widget.m_gain,widget.m_results,('Gain [e- / ADU]',))
        self.SetInfoText(widget.m_noise,widget.m_results,('Readnoise, RMS [e-]',))
        self.SetInfoText(widget.m_capacity,widget.m_results,('Saturation capacity [e-]',))
        self.SetInfoText(widget.m_linearity,widget.m_results,('Linearity Error',))
        widget.m_dark = ""
        path = os.path.join(widget.m_folder, "dark.tif");
        if not os.path.isfile(path):
            path = os.path.join(widget.m_folder, "dark.ome.tif");
        if os.path.isfile(path):
            widget.m_dark = os.path.basename(path)
        widget.m_bright = ""
        path = os.path.join(widget.m_folder, "bright.tif");
        if not os.path.isfile(path):
            path = os.path.join(widget.m_folder, "bright.ome.tif");
        if os.path.isfile(path):
            widget.m_bright = os.path.basename(path)
        #print("UpdateWidget: " + widget.name + " '" + widget.m_bright + "' '" + widget.m_dark + "'")
        path = os.path.join(widget.m_folder, "out.txt");
        out_present = os.path.isfile(path)
        if len(widget.m_bright) and len(widget.m_dark):
            #widget.m_btnStart.Enable(1)
            if out_present:
                widget.delayedUpdate = 0
            elif self.m_btnAuto.GetValue():
                widget.delayedUpdate = 1
        if widget.m_btnExpand.GetValue():
            self.ExpandWidget(widget)
        self.SetStartButton(widget,g_detphocalProcesses.isRunning(widget.m_folder))

    def SetStartButton(self, widget, state):
        widget.m_btnStart.SetValue(state)
        if state:
            widget.m_btnStart.SetLabel("Busy...")
        else:
            widget.m_btnStart.SetLabel("Start")

    def StartAnalysis(self, widget, args):
        dark = os.path.join(widget.m_folder, widget.m_dark)
        bright = os.path.join(widget.m_folder, widget.m_bright)
        if not os.path.isfile(dark) or not os.path.isfile(bright):
            return
        try:
            f = open(dark, "r+")
            f.close()
            f = open(bright, "r+")
            f.close()
        except:
            return
        widget.m_btnStart.SetLabel("Busy...")
        widget.m_btnStart.SetValue(1)
        widget.m_args = args
        g_detphocalProcesses.start(widget.m_folder, widget.m_args, widget.m_bright, widget.m_dark)

    def m_btnStartOnButtonClick(self, event):
        button = event.EventObject
        widget = button.Parent
        if not button.GetValue():
            g_detphocalProcesses.kill(widget.m_folder)
            button.SetLabel("Start")
            return
        dlg = dialogDetectorPhotonCalibration(self, widget.m_folder)
        if dlg.ShowModal() != wx.ID_OK:
            button.SetValue(False)
            return
        self.StartAnalysis(widget,dlg.formatArgs())

    def onTimer(self, event):
        # check running processes
        while 1:
            proc = g_detphocalProcesses.checkAll()
            if not proc:
                break
            key = os.path.basename(proc.folder)
            if not key in self.widgets.keys():
                continue
            widget = self.widgets[key]
            widget.m_btnStart.SetValue(False)
            widget.m_btnStart.SetLabel("Start")
            tt = widget.m_args
            if len(proc.errors):
                tt += "\n" + proc.errors
            else:
                tt += "\n" + proc.output
            widget.m_btnStart.SetToolTip(tt)
            self.UpdateWidget(widget)
        # check pending updates
        frozen = 0
        for widget in self.widgets.values():
            if widget.delayedUpdate:
                #print("onTimer: "  + widget.name + "" + str(widget.delayedUpdate))
                if not frozen:
                    frozen = 1
                    self.Freeze()
                self.UpdateWidget(widget)
                if self.m_btnAuto.GetValue() and len(widget.m_dark) and len(widget.m_bright):
                    # check for exclusive access
                    try:
                        f = open(os.path.join(widget.m_folder,widget.m_dark), "r+")
                        f.close()
                        f = open(os.path.join(widget.m_folder,widget.m_bright), "r+")
                        f.close()
                    except:
                        continue
                    self.autoProcess(widget)
        if frozen:
            self.Thaw()

    def autoProcess(self,widget):
        if not widget.m_btnStart.GetValue() and not os.path.exists(os.path.join(widget.m_folder, "out.txt")):
            if g_detphocalAutoOptions.load(os.path.join(widget.m_folder,"caltool.txt")):
                self.StartAnalysis(widget,g_detphocalAutoOptions.format())
                widget.delayedUpdate = 0

    def m_btnExpandOnButtonClick(self, event):
        button = event.EventObject
        widget = button.Parent
        self.widget_state[widget.name] = button.GetValue()
        self.ExpandWidget(widget)

    def ExpandWidget(self, widget):
        panel = widget.m_graphPanel
        sizer = panel.GetSizer()
        state = 0
        if widget.name in self.widget_state:
            state = self.widget_state[widget.name]
        widget.m_btnExpand.SetValue(state)

        panel.DestroyChildren()
        sizer.Clear()

        if state:
            path = os.path.join(widget.m_folder, "dark.tif");
            if not os.path.isfile(path):
                path = os.path.join(widget.m_folder, "dark.ome.tif");
            if os.path.isfile(path):
                widget.m_dark = os.path.basename(path)
                bitmap = MultiPageTiffFrame(panel, widget.name, path)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Dark",bitmap)
            path = os.path.join(widget.m_folder, "bright.tif");
            if not os.path.isfile(path):
                path = os.path.join(widget.m_folder, "bright.ome.tif");
            if os.path.isfile(path):
                widget.m_bright = os.path.basename(path)
                bitmap = MultiPageTiffFrame(panel, widget.name, path)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Bright", bitmap)
            infopath = os.path.join(widget.m_folder, "info.txt");
            if os.path.isfile(infopath):
                bitmap = TextFrame(panel, widget.name, infopath)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Info", bitmap)
            path = os.path.join(widget.m_folder, "calibration_results.txt");
            if os.path.isfile(path):
                bitmap = ResultsFrame(panel, widget.name, path)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Results", bitmap)
            path = os.path.join(widget.m_folder,"Photon_Calibration.svg");
            if os.path.isfile(path):
                bitmap = SvgPhotonCalibrationImage(panel, wx.ID_ANY, path, wx.DefaultPosition, (1023,590), 0)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Photon Calibration", bitmap)
            path = os.path.join(widget.m_folder,"linearityError.svg")
            if os.path.isfile(path):
                bitmap = SvgImage(panel, wx.ID_ANY, path, wx.DefaultPosition, (1023,590), 0)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Lineary Error", bitmap)
            path = os.path.join(widget.m_folder,"Brightness_Fluctuation.svg")
            if os.path.isfile(path):
                bitmap = SvgImage(panel, wx.ID_ANY, path, wx.DefaultPosition, (1023,590), 0)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Brightness Fluctuation", bitmap)
            path = os.path.join(widget.m_folder,"correctOffsetDrift.svg")
            if os.path.isfile(path):
                bitmap = SvgImage(panel, wx.ID_ANY, path, wx.DefaultPosition, (1023,590), 0)
                sizer.Add(bitmap, 0, wx.ALL, 5)
                self.SetFilterCategory("Offset Drift", bitmap)
                self.widget_state[widget.name] = 1
        else:
            self.widget_state[widget.name] = 0

        self.CheckLabels()
        wxResizePanelToContent(panel) # the m_graphPanel panel must be resized to show all content
        wxResizePanelToContent(panel.GetParent()) # the panelNoiseBrightness panel must be resized to show all content
        wxResizePanelToContent(self.m_rightMainPanel) # the right panel must be resized to show all content
        self.m_rightMainPanel.GetParent().Layout() # this makes the scrolled window show the scrollbars

    def DeleteWidget(self, widget):
        self.widgets.pop(widget.name)
        widget.Destroy()
        self.CheckLabels()
        wxResizePanelToContent(self.m_rightMainPanel) # the right panel must be resized to show all content
        self.m_rightMainPanel.GetParent().Layout() # this makes the scrolled window show the scrollbars

    def DeleteDateItem(self, date):
        tree = self.m_parent.m_treeDates
        root = tree.GetRootItem()
        item, cookie = tree.GetFirstChild(root)
        while item.IsOk():
            if tree.GetItemText(item) == date:
                item.Delete(item)
                return
            item, cookie = tree.GetNextChild(root, cookie)

    def CheckDate(self, date):
        if date in self.dates:
            # check if there is still a folder with this date prefix
            for folder in os.listdir(self.m_folder):
                if folder.startswith(date):
                    return 0
            # remove the date
            self.dates.remove(date)
            ti = self.DeleteDateItem(date)
            tree = self.m_parent.m_treeDates
            item = tree.GetSelection()
            if not item.IsOk():
                item = tree.GetLastChild(tree.GetRootItem)
                if item.IsOk():
                    tree.Select(item)
                self.onSelectDate(item)
            return 0
        else:
            self.AddDate(date)
            return 1

    def CheckLabels(self):
        changed = False
        previous_expanded = True
        children = self.widget_sizer.GetChildren()
        for child in children:
            widget = child.GetWindow()
            if widget.m_lblToggle.IsShown() != previous_expanded:
                sizer = widget.GetSizer().GetChildren()[0].GetSizer()
                labels = sizer.GetChildren()
                for label in labels:
                    sizer.Show(label.GetWindow(),previous_expanded)
                sizer.Layout()
                widget.GetSizer().Layout()
                wxResizePanelToContent(widget)
                changed = True
            previous_expanded = widget.m_btnExpand.GetValue()
        return changed

    def onDataFileChange(self, event):
        action = event.action
        path = str(os.path.join(self.m_parent.folder, event.file))
        if not path.startswith(str(self.m_folder)):
            return
        subpath = path[len(str(self.m_folder))+1:]
        pathlist = subpath.split('\\')
        if not len(pathlist) or pathlist[0] == '': # why does splitting an empty string yields a list with one empty element ?
            return
        file = pathlist[-1]
        folder = pathlist[0]
        folder_path = str(os.path.join(str(self.m_folder),folder))
        widgetPresent = folder in self.widgets.keys()

        # handle subfolder creation/rename/deletion
        if len(pathlist) == 1:
            #if action == FolderWatch.Deleted:
            if not os.path.isdir(path):
                if widgetPresent:
                    self.DeleteWidget(self.widgets[folder])
                    self.CheckLabels()
                return
            if action == FolderWatch.Renamed:
                old_path = str(os.path.join(self.m_parent.folder, event.old_name))
                old_subpath = old_path[len(str(self.m_folder))+1:]
                old_folder = old_subpath.split("\\")[0]
                if old_folder in self.widgets.keys():
                    self.DeleteWidget(self.widgets[old_folder])
                    self.CheckLabels()
                action = FolderWatch.Created
                # no return
            if action == FolderWatch.Created:
                date = re.search(r"^\d\d\d\d\d\d\d\d", folder)
                if date:
                    if self.CheckDate(date.group()):
                        return
                    if not widgetPresent:
                        self.AddWidget(folder_path, folder)
                        self.CheckLabels()
                        wxResizePanelToContent(self.m_rightMainPanel)  # the right panel must be resized to show all content
                        self.m_rightMainPanel.GetParent().Layout()  # this makes the scrolled window show the scrollbars
                return
            return

        # handle file creation/rename/deletion in subfolder
        if len(pathlist) == 2:
            if not widgetPresent:
                return
            if file == "caltool.txt" or file == "info.txt" or file == "out.txt":
                return
            if (action == FolderWatch.Updated) or (action == FolderWatch.Created):
                if g_detphocalProcesses.isRunning(folder_path):
                    return
                if widgetPresent:
                    self.widgets[folder].delayedUpdate = 1
                    return
                return
            return

        return

    # Virtual event handlers, override them in your derived class
    def panelDetectorResultsOnSize(self, event):
        event.Skip()
        self.m_rightMainPanel.SetVirtualSize(self.m_rightMainPanel.GetClientSize())

    def saveModified(self, options):
        modified = False
        for name in self.widgets:
            widget = self.widgets[name]
            if hasattr(widget, 'IsModified') and widget.IsModified():
                modified = True
        answer = wx.YES
        if modified:
            answer = wx.MessageBox(u"The information has changed.\nSave the changes ?", u"QuaRep data browser", options)
            if answer == wx.YES:
                for name in self.widgets:
                    widget = self.widgets[name]
                    if hasattr(widget, 'SaveModified'):
                        widget.SaveModified()
        return answer

