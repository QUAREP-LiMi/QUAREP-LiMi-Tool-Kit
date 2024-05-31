#import csv
import math
import sys
import os
import locale
import re
#import tempfile
from datetime import datetime
from pathlib import Path, WindowsPath

import win32security
#import wx
import wx.lib.agw.persist as PM
#from wx.lib.plot import PlotCanvas, PlotGraphics, PolyLine, PolyMarker
import wxmplot
import numpy as np
import matplotlib.pyplot as mpl;

from FolderWatch import *  # requires pyWin32
from forms import *
from wxApp import *

g_showTemperature = 1

g_widgetScale = 3
g_widgetSize = wx.Size(400, 400)

def get_widget_scale():
    return g_widgetScale

class win32csvReader:
    def __init__(self, handle, delim='\t'):
        self.size = win32file.GetFileSize(handle)
        (result, buffer) = win32file.ReadFile(handle, self.size)
        unicode = buffer.decode('utf-8')
        self.pointer = 0
        self.delim = delim
        self.lines = unicode.splitlines()

    def peak(self):
        if self.pointer < len(self.lines):
            return self.lines[self.pointer].split(self.delim)
        return ['']

    def current_line(self):
        if (self.pointer == 0) or (self.pointer > len(self.lines)):
            return ""
        return self.lines[self.pointer - 1]

    def __next__(self):
        if self.pointer < len(self.lines):
            self.pointer = self.pointer + 1
            return self.lines[self.pointer - 1].split(self.delim)
        else:
            raise StopIteration

    def __iter__(self):
        return self


def parseFloat(element) -> float:
    try:
        return float(element)
    except ValueError:
        return -1000.


class TextFrame(wx.TextCtrl):

    def __init__(self, parent, title, txtfile):
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                             wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_RICH | wx.WANTS_CHARS)  # |wx.TAB_TRAVERSAL)
        self.SetMinSize(g_widgetSize)
        self.txtfile = txtfile
        self.protocol = "info"
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
        self.Draw()

    def Draw(self):
        self.LoadFile(str(self.txtfile))

    def IsModified(self):
        modified = wx.TextCtrl.IsModified(self)
        return modified

    def SaveModified(self):
        if self.IsModified():
            self.SaveFile(str(self.txtfile))


class PowerData:

    def __init__(self):
        self.info = ""
        self.x_data = []
        self.y_data = []
        self.t_data = []

        self.x_label = "time"
        self.x_unit = "AU"
        self.y_label = "power"
        self.y_unit = "mW"

        self.line = 1

    def scale_time(self):
        if (len(self.x_data) == 0) or (self.x_label != "time"):
            return
        self.x_unit = "ms"
        if len(self.x_data) == 1:
            self.x_data[0] = 0
            return
        ms_start = self.x_data[0]
        range = self.x_data[-1] - ms_start
        scale = 1
        if range > 1000.:
            if range < (60. * 1000.):
                self.x_unit = "s"
                scale = 1000.
            else:
                if range < (60. * 60. * 1000.):
                    self.x_unit = "min"
                    scale = (60. * 1000.)
                else:
                    if range < (24. * 60. * 60. * 1000.):
                        self.x_unit = "hr"
                        scale = (60. * 60. * 1000.)
                    else:
                        self.x_unit = "day"
                        scale = (24. * 60. * 60. * 1000.)
        tmp_data = self.x_data
        self.x_data = [(t - ms_start) / scale for t in tmp_data]


def ParsePowerText(panel, data, filename):
    # kees: could not find a Python way to open the files with share_write mode so NIS can continue to write ...
    # so use the win32file API
    # with open(self.datafile, "r") as file:
    # reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_NONE)
    file = win32file.CreateFile(str(filename), win32con.GENERIC_READ,
                                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                                win32security.SECURITY_ATTRIBUTES(),
                                win32con.OPEN_EXISTING, 0, 0)
    reader = win32csvReader(file, '\t')
    win32file.CloseHandle(file)
    headers = next(reader, None)
    data.line += 1
    x_col = 0
    if hasattr(panel, 'protocol') and panel.protocol == 'linear':
        x_col = headers.index('setting')
        data.x_label = "power setting"
        data.x_unit = "%"
    else:
        x_col = headers.index('timestamp')
        data.x_label = "time"
    y_col = headers.index('power')
    t_col = 0
    if 'temperature' in headers:
        t_col = headers.index('temperature')
        panel.temperature = 'temperature'
    min_cols = max(y_col, t_col)
    # read away line with formats / units: YYYY-MM-DD HH:MM:SS	nm	s	W
    row = reader.peak()
    if len(row) and len(row[0]) and not row[0][0].isdigit():
        reader.__next__()
        data.line += 1
    for row in reader:
        if len(row) > min_cols:
            if data.x_label == "time":
                x = datetime.strptime(row[x_col], '%Y-%m-%d %H:%M:%S.%f').timestamp() * 1000
            else:
                x = parseFloat(row[x_col])
            y = parseFloat(row[y_col])
            if y > -1000.:
                data.x_data.append(x)
                data.y_data.append(y)
            if t_col != 0:
                t = parseFloat(row[t_col])
                data.t_data.append(t)
        data.line += 1
    # file.close()


def ParsePowerCsv(panel, data, filename):
    # kees: could not find a Python way to open the files with share_write mode so NIS can continue to write ...
    # so use the win32file API
    # with open(self.datafile, "r") as file:
    # reader = csv.reader(file, delimiter='\t', quoting=csv.QUOTE_NONE)
    file = win32file.CreateFile(str(filename), win32con.GENERIC_READ,
                                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                                win32security.SECURITY_ATTRIBUTES(),
                                win32con.OPEN_EXISTING, 0, 0)
    reader = win32csvReader(file, ',')
    win32file.CloseHandle(file)
    headers = []
    for headers in reader:
        data.line = reader.pointer
        if (len(headers) > 0) and (headers[0] != "Samples "):
            data.info += reader.current_line() + "\r\n"
        else:
            break

    day_col = headers.index('Date (MM/dd/yyyy) ')
    time_col = headers.index('Time of day (hh:mm:ss) ')
    data.x_label = "time"

    y_col = headers.index('Power (W)')
    t_col = 0
    if 'Temperature (°C)' in headers:
        t_col = headers.index('Temperature (°C)')
        panel.temperature = 'temperature'
    min_cols = max(y_col, t_col)
    for row in reader:
        data.line = reader.pointer
        if len(row) > min_cols:
            x = datetime.strptime(row[day_col].strip() + " " + row[time_col].strip(),
                                  '%m/%d/%Y %H:%M:%S.%f').timestamp() * 1000
            y = parseFloat(row[y_col]) * 1000.
            if y > -1000.:
                data.x_data.append(x)
                data.y_data.append(y)
            if t_col != 0:
                t = parseFloat(row[t_col])
                data.t_data.append(t)
    # file.close()


def calcNormalizedStandardDeviation(data):
     return 100. * np.std(data) / np.mean(data)


class GraphFrame(wx.Panel):

    def __init__(self, parent, title, datafile):
        wx.Panel.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, wx.EmptyString)
        self.SetName(title)
        self.SetMinSize(g_widgetSize)
        self.title = title
        if isinstance(datafile, WindowsPath):
            self.datafile = datafile
        else:
            self.datafile = WindowsPath(datafile)
        self.parsePowerFileName(title)
        self.SetBackgroundColour(wx.WHITE)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.first_time = 1
        self.x_unit = ""
        self.show_temperature = 0
        """
        self.canvas = PlotCanvas(self)
        self.canvas.enableLegend = False
        self.canvas.axesPen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_SOLID)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 10)
        """
        self.plot = wxmplot.PlotPanel(self)
        self.sizer.Add(self.plot, 1, wx.EXPAND | wx.ALL, 0)
        self.results = wx.StaticText(self, wx.ID_ANY, "results:", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        self.results.SetFont(
            wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString))
        self.sizer.Add(self.results, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, 0)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Draw()

    def Draw(self):
        data = PowerData()
        try:
            if self.datafile.name.endswith(".txt"):
                ParsePowerText(self, data, self.datafile)

            if self.datafile.name.endswith(".csv"):
                ParsePowerCsv(self, data, self.datafile)

        except Exception as e:
            if 'pdb' in sys.modules:
                debugbreak();
            else:
                self.results.SetLabel("error reading file " + self.title)
                wx.MessageBox("Exception {0} during reading file {1} line {2}".format(e, self.title, data.line))
            return

        if (len(data.x_data) < 1) or ((len(data.y_data) != len(data.x_data))):
            return

        data.scale_time()

        """
        data = list(zip(x_data, y_data))
        lines = []
        if len(data) > 20:
            markers = PolyMarker(data, marker='circle', size=1)
            lines.append(markers)
        line = PolyLine(data)
        lines.append(line)
        if t_col != 0:
            tdata = list(zip(x_data,t_data))
            tline = PolyLine(tdata)
            lines.append(tline)
        graphics = PlotGraphics(lines, self.title, x_label + " [" + x_unit + "]", y_label + " [" + y_unit + "]")

        self.canvas.Draw(graphics)
        """
        if (self.first_time == 0) and ((self.x_unit != data.x_unit) or (g_showTemperature != self.show_temperature)):
            # did not find a way to change the units in the plot: just recreated the widget from scratch
            self.plot.Destroy();
            self.plot = wxmplot.PlotPanel(self)
            self.sizer.Insert(0, self.plot, 1, wx.EXPAND | wx.ALL, 0)
            self.Layout()
            self.first_time = 1

        self.show_temperature = g_showTemperature
        if self.first_time:
            self.x_unit = data.x_unit
            params = dict(delay_draw=True, fullbox=False, bgcolor="#FFFFFF", framecolor="#FFFFFF", titlefontsize=6,
                          labelfontsize=4, linewidth=1)
            if len(data.x_data) < 20:
                params['marker'] = '+'
            self.plot.plot(data.x_data, data.y_data, title=self.title, xlabel=data.x_label + " [" + data.x_unit + "]",
                           ylabel=data.y_label + " [" + data.y_unit + "]", **params)
            if len(data.t_data) and g_showTemperature:
                if len(data.x_data) < 20:
                    params['linewidth'] = 0
                self.plot.oplot(data.x_data, data.t_data, side='right', y2label='Temperature', **params)
            self.first_time = 0
        else:
            # the only way to update a wxmplot seems to be through 'update_line'
            # but a change of axis unit (e.g. from ms to s) is not processed ?
            self.plot.update_line(0, data.x_data, data.y_data, update_limits=True, draw=True)
            if len(data.t_data) and g_showTemperature:
                self.plot.update_line(1, data.x_data, data.t_data, update_limits=True, draw=True)

        # internally the axis tick label format is set before the axis range is available
        # resetting the formats will ensure that the formats are re-initialized based on the correct axis ranges
        self.plot.reset_formats()

        self.Analyse(data.x_data, data.y_data)

        if len(data.info):
            self.results.SetToolTip(data.info)

    def parsePowerFileName(self, name):
        if name.endswith(".txt"):
            splitted = name.removesuffix('.txt').split('_')
        else:
            splitted = name.removesuffix('.csv').split('_')
        if len(splitted) > 1:
            self.date_time = splitted[0]
        if len(splitted) > 2:
            self.line_name = splitted[1]
        more_ports = 0
        if (len(splitted) > 4) or ((len(splitted) == 4) and (splitted[3] == "linear")):
            more_ports = 1
            self.port = splitted[2]
        if len(splitted) > (2 + more_ports):
            self.protocol = splitted[2 + more_ports]
        if len(splitted) > (3 + more_ports):
            self.power = splitted[3 + more_ports] + " %"

    def Analyse(self, x_data, y_data):
        if hasattr(self, 'protocol') and self.protocol == 'linear':
            try:
                model = np.polyfit(x_data, y_data, 1)
                a = model[0]
                b = model[1]
                chi2 = 0
                for i, t in enumerate(x_data):
                    v = a * x_data[i] + b
                    chi2 += pow(y_data[i] - v,2) / v
                self.results.SetLabel("linearity chi2: " + "{:f}".format(chi2))
            except Exception:
                self.results.SetLabel("linearity fit failed")
        else:
            minVal = float(min(y_data))
            maxVal = float(max(y_data))
            stability = 100. * (1. - ((maxVal - minVal) / (maxVal + minVal)))
            #cv = np.cov(y_data)
            nsd = calcNormalizedStandardDeviation(y_data)
            self.results.SetLabel("N: " + "{:d}".format(len(y_data)) + ", min: " + "{:.1f}".format(minVal) +
                ", max: " + "{:.1f}".format(maxVal) + ", stability: " + "{:.0f}".format(stability) +
                "%, nsd: " + "{:.2f}".format(nsd) + "%")
        self.GetSizer().Layout()


class pageLightSourceResults(panelTwoPanes):

    def __init__(self, formBrowse, parent):
        panelTwoPanes.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'pageLightSourceResults')
        self.m_parent = formBrowse
        self.widgets = {}
        self.deviceFolder = ""
        self.deviceDate = ""
        self.dateTi = None
        self.dates = set()
        self.m_buttonPanel = self.m_rightTopPanel
        self.m_buttonSizer = self.m_rightTopPanel.GetSizer()
        self.m_buttonTemperature = None
        self.filterLine = {}
        self.filterPort = {}
        self.filterProtocol = {}
        self.filterPower = {}
        self.set_widget_scale(wxGetApp().config.Read("widgetScale"))
        self.initTrees()

    def onDestroy(self):
        pass

    def set_widget_scale(self, scale):
        try:
            scale = int(scale)
        except:
            return
        if scale < 1:
            scale = 1
        if scale > 40:
            scale = 40
        global g_widgetScale, g_widgetSize
        g_widgetScale = scale
        g_widgetSize = wx.Size(120 * scale, 90 * scale)
        for widget in self.widgets:
            self.widgets[widget].SetSize(g_widgetSize)

    def change_widget_scale(self, direction):
        if direction < 0:
            self.set_widget_scale(g_widgetScale + 1)
        if direction > 0:
            self.set_widget_scale(g_widgetScale - 1)

    def m_toolBiggerClicked(self, event):
        self.change_widget_scale(-1)
        self.m_treeDatesOnTreelistSelectionChanged(None)
        wxGetApp().config.Write("widgetScale", str(get_widget_scale()))

    def m_toolSmallerClicked(self, event):
        self.change_widget_scale(1)
        self.m_treeDatesOnTreelistSelectionChanged(None)
        wxGetApp().config.Write("widgetScale", str(get_widget_scale()))

    def initTrees(self):
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
            date = re.search(r"^\d\d\d\d\d\d\d\d-\d\d\d\d", file)
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
        self.m_parent.StartWatch(self.deviceFolder)

    def m_treeDatesOnTreelistSelectionChanged(self, event):
        if event != None:
            event.Skip()
        tree = self.m_parent.m_treeDates
        ti = tree.GetSelection()
        self.onSelectDate(ti)

    def addWidget(self, name, widget, border):
        self.widgets[name] = widget
        self.widget_sizer.Add(widget, 1, wx.EXPAND | wx.ALL, border)

        if hasattr(widget, 'temperature') and self.m_buttonTemperature == None:
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, "Temperature")
            button.SetValue(g_showTemperature)
            self.temperature_sizer.Add(button, 0, wx.ALL, 5)
            self.m_buttonTemperature = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onTemperatureToggle)

        if hasattr(widget, 'line_name') and not widget.line_name in self.filterLine.keys():
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, widget.line_name)
            button.SetValue(1)
            self.line_sizer.Add(button, 0, wx.ALL, 5)
            self.filterLine[widget.line_name] = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onFilterToggle)

        if hasattr(widget, 'port') and not widget.port in self.filterPort.keys():
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, widget.port)
            button.SetValue(1)
            self.port_sizer.Add(button, 0, wx.ALL, 5)
            self.filterPort[widget.port] = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onFilterToggle)

        if hasattr(widget, 'protocol') and not widget.protocol in self.filterProtocol.keys():
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, widget.protocol)
            button.SetValue(1)
            self.protocol_sizer.Add(button, 0, wx.ALL, 5)
            self.filterProtocol[widget.protocol] = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onFilterToggle)

        if hasattr(widget, 'power') and not widget.power in self.filterPower.keys():
            button = wx.ToggleButton(self.m_buttonPanel, wx.ID_ANY, widget.power)
            button.SetValue(1)
            self.power_sizer.Add(button, 0, wx.ALL, 5)
            self.filterPower[widget.power] = button
            button.Bind(wx.EVT_TOGGLEBUTTON, self.onFilterToggle)

    def onSelectDate(self, ti):
        self.saveModified(wx.YES_NO)
        tree = self.m_parent.m_treeDates
        if ti is None:
            return
        if not ti.IsOk():
            if self.dateTi != None and self.dateTi.IsOk():
                tree.Select(self.dateTi)
            return
        self.dateTi = ti

        self.Freeze()
        panel = self.m_rightMainPanel
        panel.DestroyChildren()
        self.widget_sizer = panel.GetSizer()
        self.widget_sizer.Clear()
        self.button_panel = self.m_rightTopPanel
        self.button_panel.DestroyChildren()
        self.button_sizer = self.m_rightTopPanel.GetSizer()
        self.button_sizer.Clear()
        self.m_buttonTemperature = None
        self.filterLine = {}
        self.filterPort = {}
        self.filterProtocol = {}
        self.filterPower = {}
        panel.GetParent().Layout()

        wait = wx.BusyCursor()

        # button = wx.Button( self.m_buttonPanel, wx.ID_ANY, u"Print")
        # button.Bind(wx.EVT_BUTTON, self.onPrint)
        # button_sizer.Add(button, 0, wx.ALL, 5)
        self.zoom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.zoom_sizer, 0, 0, 0)
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "<>")
        button_size = button.GetDefaultSize(self)
        button_size.x /= 2
        button.Destroy()
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "<>", wx.DefaultPosition, button_size)
        button.Layout()
        button.SetToolTip("make the graphs larger")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolBiggerClicked)
        button = wx.Button(self.m_buttonPanel, wx.ID_ANY, "><", wx.DefaultPosition, button_size)
        button.SetToolTip("make the graphs smaller")
        self.zoom_sizer.Add(button, 0, wx.ALL, 5)
        button.Bind(wx.EVT_BUTTON, self.m_toolSmallerClicked)
        self.temperature_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.temperature_sizer, 0, 0, 0)
        self.protocol_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.protocol_sizer, 0, 0, 0)
        self.port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.port_sizer, 0, 0, 0)
        self.power_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.power_sizer, 0, 0, 0)
        self.line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_sizer.Add(self.line_sizer, 0, 0, 0)

        name = tree.GetItemText(ti)
        item_data = tree.GetItemData(ti)
        path = Path(item_data['folder'])
        self.deviceDate = item_data['date']
        self.widgets = {}
        for file in path.glob(item_data['date'] + "*.txt"):
            if file.name.endswith("info.txt"):
                border = 5
                graph = TextFrame(panel, file.name, file)
            else:
                border = 0
                graph = GraphFrame(panel, file.name, file)
            self.addWidget(file.name, graph, border)
        for file in path.glob(item_data['date'] + "*.csv"):
            graph = GraphFrame(panel, file.name, file)
            self.addWidget(file.name, graph, 0)

        panel.GetParent().Layout()
        self.Thaw()
        del wait

    def AddDate(self, date):
        self.dates.add(date)
        tree = self.m_parent.m_treeDates
        root = tree.GetRootItem()
        ti = tree.AppendItem(root, date)
        tree.SetItemData(ti, {'folder': self.deviceFolder, 'date': date})
        tree.Select(ti)
        self.onSelectDate(ti)

    def onDataFileChange(self, event):
        if self.m_parent.dataFileWatch is None:
            return
        self.m_parent.dataFileWatch.rearm(event.action, event.file)
        panel = self.m_rightMainPanel
        sizer = panel.GetSizer()
        action = event.action
        if action == FolderWatch.Renamed:
            if event.old_name in self.widgets:
                widget = self.widgets[event.old_name]
                panel.RemoveChild(widget)
                del self.widgets[event.old_name]
                widget.Destroy()
                action = FolderWatch.Created
                # no return
        if action == FolderWatch.Deleted:
            if event.file in self.widgets:
                widget = self.widgets[event.file]
                panel.RemoveChild(widget)
                del self.widgets[event.file]
                widget.Destroy()
                panel.GetParent().Layout()
                return
        if action == FolderWatch.Created:
            if event.file.startswith(self.deviceDate) and (event.file.endswith(".txt") or event.file.endswith(".csv")):
                self.Freeze()
                border = 5
                if event.file.endswith("info.txt"):
                    widget = TextFrame(panel, event.file, os.path.join(event.source.folder, event.file))
                    border = 0
                else:
                    widget = GraphFrame(panel, event.file, os.path.join(event.source.folder, event.file))
                self.addWidget(event.file, widget, border)
                panel.GetParent().Layout()
                panel.Scroll(-1, panel.GetClientSize()[1])
                self.Thaw()
                return
            else:
                date = re.search(r"^\d\d\d\d\d\d\d\d-\d\d\d\d", event.file)
                if date is not None:
                    date = date.group()
                    if date not in self.dates:
                        self.AddDate(date)
        if action == FolderWatch.Updated:
            if event.file in self.widgets:
                self.widgets[event.file].Draw()
                return

    def onDeviceFolderChange(self, event):
        if self.m_parent.deviceFolderWatch is None:
            return
        # print(FolderWatch.ActionName(event.action) + ": " + event.file + "\n")
        action = event.action
        if action != FolderWatch.Thread:
            self.m_parent.populateTrees()

    def onFilterToggle(self, event):
        self.Freeze()
        panel = self.m_rightMainPanel
        sizer = panel.GetSizer()
        for filename in self.widgets:
            graph = self.widgets[filename]
            visible = 1
            if hasattr(graph, 'line_name') and graph.line_name in self.filterLine.keys() and not self.filterLine[
                graph.line_name].GetValue():
                visible = 0
            if visible and hasattr(graph, 'port') and graph.port in self.filterPort.keys() and not self.filterPort[
                graph.port].GetValue():
                visible = 0
            if visible and hasattr(graph, 'protocol') and graph.protocol in self.filterProtocol.keys() and not \
            self.filterProtocol[graph.protocol].GetValue():
                visible = 0
            if visible and hasattr(graph, 'power') and graph.power in self.filterPower.keys() and not self.filterPower[
                graph.power].GetValue():
                visible = 0
            sizer.Show(graph, visible)

        sizer.Layout()
        panel.Layout()
        self.Thaw()

    def onTemperatureToggle(self, event):
        global g_showTemperature
        g_showTemperature = self.m_buttonTemperature.GetValue()
        wait = wx.BusyCursor()
        self.Freeze()
        panel = self.m_rightMainPanel
        sizer = panel.GetSizer()
        for filename in self.widgets:
            graph = self.widgets[filename]
            if hasattr(graph, 'temperature') and graph.IsShown():
                graph.Draw()
        sizer.Layout()
        panel.Layout()
        self.Thaw()
        del wait

    # Virtual event handlers, override them in your derived class
    def panelTwoPanesOnSize(self, event):
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

