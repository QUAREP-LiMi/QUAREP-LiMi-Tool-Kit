import os
import wx
import re
from forms import *
from wxApp import *

class pageStageResults(panelStageResults):

    def __init__(self, formBrowse, parent):
        panelStageResults.__init__(self, parent,id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL, name=wx.EmptyString)
        self.m_formBrowse = formBrowse
        formBrowse.m_treeDates.DeleteAllItems()
        self.m_folder = ""
        self.m_files = {}
        self.m_tooltips = {}
        self.m_curRow = -1
        self.m_limit = 0.5
        self.m_ti = None
        self.m_grid.GetGridWindow().Bind(wx.EVT_MOTION, self.m_gridOnMotion)

    def onDestroy(self):
        pass

    # saveModified method is called by the mainFrame before destroying this page: return wx.CANCEL to cancel
    def saveModified(self,options):
        return wx.YES

    # StopWatch method is called by the mainFrame before destroying this page: no cancel possible anymore
    def stopWatch(self):
        return

    def onDataFileChange(self, event):
        path = self.m_formBrowse.folder + "\\" + event.file
        datetime = self.matchFilename(os.path.basename(path))
        if datetime == "":
            return
        row = -1
        if path in self.m_files:
            row = self.m_files[path]
        self.LoadFile(path,datetime,row)

    def onSelectDevice(self, ti):
        if not ti:
            return
        self.m_ti = ti
        tree = self.m_formBrowse.m_treeDevices
        rows = self.m_grid.GetNumberRows()
        if rows > 0:
            self.m_grid.DeleteRows(0,rows,True)
        self.m_files = {}
        self.m_tooltips = {}
        self.m_caption.SetLabel("")
        self.m_curRow = -1
        self.m_grid.GetGridWindow().SetToolTip("")
        text = ""
        while ti != tree.GetRootItem():
            text = tree.GetItemText(ti) + "\\" + text
            ti = tree.GetItemParent(ti)
        text = self.m_formBrowse.folder + "\\" + text
        self.m_folder = text
        if not os.path.isdir(text):
            text = "The folder '" + text + "' does not exist"
            self.m_caption.SetLabel(text)
        self.UpdateData()

    def matchFilename(self, file):
        match = re.match(r"^(\d\d\d\d\d\d\d\d-\d\d\d\d)_stage_repeatability.tif_analysis.txt$", file)
        if not match:
            match = re.match(r"^(\d\d\d\d\d\d\d\d-\d\d\d\d)_stage_repeatability_analysis.txt$", file)
        if not match:
            return ""
        return match.group(1)

    def UpdateData(self):
        self.LoadSettings()
        for file in os.listdir(self.m_folder):
            datetime = self.matchFilename(file)
            if datetime == "":
                continue
            path = self.m_folder + file
            if path in self.m_files:
                continue
            self.LoadFile(path, datetime, -1)

    def LoadFile(self, path, datetime, row):
        result,data,info = self.ReadFile(path)
        if not result or len(data) != 20:
            return
        if row == -1:
            row = self.m_grid.NumberRows
            self.m_grid.AppendRows(1,True)
        self.m_files[path] = row
        self.m_tooltips[row] = info["desc"]
        self.m_grid.SetCellValue(row, 0, str(info["repeat"]))
        self.m_grid.SetCellValue(row, 1, str(info["small"]))
        self.m_grid.SetCellValue(row, 2, str(info["large"]))
        self.m_grid.SetCellValue(row, 3, str(info["speed"]))
        for col in range(0,20):
            self.m_grid.SetCellValue(row,col+4,str(data[col]))
            if float(data[col]) > self.m_limit:
                self.m_grid.SetCellBackgroundColour(row,col+4,wx.RED)
            else:
                self.m_grid.SetCellBackgroundColour(row,col+4,wx.WHITE)
        self.m_grid.SetRowLabelValue(row,datetime)
        self.m_grid.SetRowLabelSize(-1)
        self.m_grid.AutoSize()

    def ReadFile(self, path):
        #  0       1       2       3       4       5       6       7       8       9       10      11      12      13      14      15      16      17      18      29
        # "x-s-a" "x-s-l" "x-s-r" "x-s-b" "x-s-f" "y-s-a" "y-s-l" "y-s-r" "y-s-b" "y-s-f" "x-l-a" "x-l-l" "x-l-r" "x-l-b" "x-l-f" "y-l-a" "y-l-l" "y-l-r" "y-l-b" "y-l-f"
        data = [0.0] * 20
        info = {"small": "", "large": "", "repeat": "", "speed": "", "desc" : ""}
        with open(path, 'r') as file:
            lines = file.readlines()
        if(len(lines)) < 14:
            self.m_caption.SetLabel("unexpected number of lines in file " + path)
            return (False,data,info)
        line = 0
        while line < len(lines):
            if (len(lines[line]) > 0) and (lines[line][0] == 'x'):
                break
            if lines[line].startswith("Repetition:"):
                fields = lines[line].split()
                if len(fields) > 1:
                    info["repeat"] = fields[1]
            elif lines[line].startswith("Stage Speed:"):
                fields = lines[line].split()
                if len(fields) > 2:
                    info["speed"] = fields[2]
            else:
                info["desc"] += lines[line]
            line = line + 1
        if (len(lines[line]) < 1) or (lines[line][0] != 'x'):
            self.m_caption.SetLabel("unexpected line " + str(line) + "without x in file " + path)
            return (False, data, info)
        fields = lines[line].split()
        if(len(fields) > 2):
            info["small"] = fields[1]
            info["large"] = fields[2]
        line = line + 1
        # x (small, large) in (all, left, right, back, front)
        for direction in range(0,4):
            fields = lines[line+direction].split()
            if len(fields) != 3:
                self.m_caption.SetLabel("unexpected line " + str(line) + " in file " + path)
                return (False, data, info)
            data[direction] = fields[1]
            data[direction+10] = fields[2]
        line = line + 6
        # y (small, large) in (all, left, right, back, front)
        for direction in range(0,4):
            fields = lines[line + direction].split()
            if len(fields) != 3:
                self.m_caption.SetLabel("unexpected line " + str(line) + " in file " + path)
                return (False, data, info)
            data[direction + 5] = fields[1]
            data[direction + 15] = fields[2]
        return (True, data, info)

    def m_gridOnMotion(self, event):
        event.Skip()
        x, y = self.m_grid.CalcUnscrolledPosition(event.GetPosition())
        row = self.m_grid.YToRow(y)
        #col = self.m_grid.XToCol(x)
        if row != self.m_curRow:
            self.m_curRow = row
            if row in self.m_tooltips:
                self.m_grid.GetGridWindow().SetToolTip(self.m_tooltips[row])
            else:
                self.m_grid.GetGridWindow().SetToolTip("")

    def m_bntSetToleranceOnButtonClick(self, event):
        event.Skip()
        dlg = dlgSetTolerance(self)
        dlg.m_txtTolerance.SetValue(str(self.m_limit))
        if dlg.ShowModal() == wx.ID_OK:
            self.m_limit = float(dlg.m_txtTolerance.GetValue())
            self.SaveSettings()
            self.onSelectDevice(self.m_ti)

    def SaveSettings(self):
        with open(self.m_folder + "\\settings.txt", 'w') as file:
            file.write("limit: " + str(self.m_limit))

    def LoadSettings(self):
        m_limit = 0.5
        path = self.m_folder + "\\settings.txt"
        if os.path.isfile(path):
            with open(path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    fields = line.split()
                    if len(fields) < 2:
                        continue
                    if fields[0] == "limit:":
                        self.m_limit = float(fields[1])
        self.m_bntSetTolerance.SetLabel("Warning limit: " + str(self.m_limit))







