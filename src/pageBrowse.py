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
import matplotlib.pyplot as mpl

from FolderWatch import *  # requires pyWin32
from forms import *
from wxApp import *
from pageLightSourceResults import *

class pageBrowse(formBrowse):

    def __init__(self, parent):
        formBrowse.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'browseFrame')
        self.categories = {"Light Sources": {"name": "Light Sources", "folder":"Light Sources", "class": pageLightSourceResults }}
        self.m_rightPanel = None
        self.dataFileWatch = None
        self.deviceFolderWatch = None
        self.folder = wxGetApp().config.Read("folder")
        self.category = ""
        while len(self.folder) == 0:
            dlg = wx.DirDialog(None, "QuaRep Main Data Folder", "c:\\QuaRep",
                               wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if wx.ID_OK != dlg.ShowModal():
                return
            self.CheckFolder(dlg.GetPath())
        self.m_mainSplitter.SetName("browseSplitter")

        self.initDeviceTree()

        self.init_type = ""
        self.init_device = ""
        self.SetFolder(self.folder)
        # self.canvas = Canvas(self.m_rightPanel, size=(0, 0))
        # self.CreatePrintData()


    def SetActiveFolder(self, folder):
        folder, unit = os.path.split(folder)
        folder, model = os.path.split(folder)
        folder, category = os.path.split(folder)
        for cat in self.categories:
            if self.categories[cat]["folder"].lower() == category.lower():
                self.init_type = cat
                self.init_device = model + " " + unit
                self.SetFolder(folder)
                return

    def CheckFolder(self, folder):
        lsdir = os.path.join(folder, "Light Sources")
        if not os.path.isdir(lsdir):
            result = wx.MessageBox("This folder does not have a sub-folder 'Light Sources.\nCreate it ?",
                                   "QuaRep Folder", wx.OK | wx.CANCEL | wx.ICON_WARNING)
            if result == wx.OK:
                os.makedirs(lsdir)
                if not os.path.isdir(lsdir):
                    wx.MessageBox("Could not make a folder 'Light Sources.", "QuaRep Folder", wx.OK | wx.ICON_WARNING)
                    return
        self.folder = folder
        wxGetApp().config.Write("folder", self.folder)

    def initDeviceTree(self):
        tree = self.m_treeDevices
        tree.AppendColumn(u"Devices")

    def SetFolder(self, folder):
        self.folder = folder
        # self.folder = self.folder.replace("\\", "/")
        self.m_folder.SetPath(self.folder)
        self.populateDeviceTree()

    def populateDeviceTree(self):
        self.deviceTi = None
        self.m_treeDevices.DeleteAllItems()
        for cat in self.categories:
            self.populateDevices(self.m_treeDevices, self.categories[cat])
        self.init_type = ""

    def m_folderOnDirChanged(self, event):
        event.Skip()
        folder = self.m_folder.GetPath()
        self.CheckFolder(folder)
        self.SetFolder(self.folder)

    def StartWatch(self, folder):
        self.stopWatch()
        self.dataFileWatch = FolderWatch(self, 1, folder,
                                         win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
                                         False)
        self.Bind(EVT_FOLDER_CHANGE_EVENT, self.onDataFileChange, self.dataFileWatch)
        devFolder = os.path.split(folder)[0]
        devFolder = os.path.split(devFolder)[0]
        self.deviceFolderWatch = FolderWatch(self, 2, devFolder, win32con.FILE_NOTIFY_CHANGE_DIR_NAME, True)
        self.Bind(EVT_FOLDER_CHANGE_EVENT, self.onDeviceFolderChange, self.deviceFolderWatch)

    def stopWatch(self):
        if self.dataFileWatch:
            self.dataFileWatch.abort()
            self.dataFileWatch = None
        if self.deviceFolderWatch:
            self.deviceFolderWatch.abort()
            self.deviceFolderWatch = None

    def SelectDeviceTreeItem(self,ti):
        self.ignoreDeviceTreeEvent = 1

    def populateDevices(self, tree, category):
        name = category["name"]
        devices = tree.AppendItem(tree.GetRootItem(), name)
        first_device = None
        folder = category["folder"]
        path = os.path.join(self.folder,folder)
        if not os.path.isdir(path):
            wx.MessageBox("The folder " + path + " does not exists", "", wx.OK | wx.ICON_WARNING)
            return
        for model in os.listdir(path):
            model_folder = os.path.join(path, model)
            if os.path.isdir(model_folder):
                units = []
                for unit in os.listdir(model_folder):
                    unit_folder = os.path.join(model_folder, unit)
                    if os.path.isdir(unit_folder):
                        units.append(unit)
                if len(units) == 0:
                    pass
                elif len(units) == 1:
                    label = model + " " + units[0]
                    uti = tree.AppendItem(devices, label)
                    tree.SetItemData(uti, {"folder": os.path.join(model_folder, units[0]), "category": category})
                    if label == self.init_device:
                        first_device = uti
                    if first_device is None:
                        first_device = uti
                else:
                    mti = tree.AppendItem(devices, model)
                    for unit in units:
                        label = model + " " + unit
                        uti = tree.AppendItem(mti, label)
                        tree.SetItemData(uti, {"folder": os.path.join(model_folder, unit), "category": category})
                        if label == self.init_device:
                            first_device = uti
                        if first_device is None:
                            first_device = uti
                    tree.Expand(mti)
        tree.Expand(devices)
        if first_device is not None:
            tree.Select(first_device)
            self.onSelectDevice(first_device)
        self.init_device = ""

    def m_treeDevicesOnTreelistSelectionChanged(self, event):
        event.Skip()
        tree = self.m_treeDevices
        ti = tree.GetSelection()
        self.onSelectDevice(ti)

    def onSelectDevice(self, ti):
        self.saveModified(wx.YES_NO)
        tree = self.m_treeDevices
        if ti is None:
            return
        if not ti.IsOk():
            if self.deviceTi != None and self.deviceTi.IsOk():
                tree.Select(self.deviceTi)
            return

        data = tree.GetItemData(ti)
        category = data["category"]
        if self.category != category["name"]:
            # todo: delete m_rightPanel if not None ?
            self.m_rightPanel = category["class"](self, self.m_mainSplitter)
            self.m_mainSplitter.SplitVertically(self.m_leftPanel, self.m_rightPanel, 300)
            self.Layout()
            self.Update()
            self.category = category["name"]
        self.deviceTi = ti
        self.deviceFolder = data["folder"]
        self.m_rightPanel.onSelectDevice(ti)
        self.StartWatch(self.deviceFolder)

    def m_treeDatesOnTreelistSelectionChanged(self, event):
        if event != None:
            event.Skip()
        tree = self.m_treeDates
        ti = tree.GetSelection()
        self.onSelectDate(ti)

    def onSelectDate(self, ti):
        if self.m_rightPanel == None:
            return
        self.m_rightPanel.onSelectDate(ti)

    def onDataFileChange(self, event):
        if self.m_rightPanel == None:
            return
        self.m_rightPanel.onDataFileChange(event)

    def onDeviceFolderChange(self, event):
        if self.deviceFolderWatch is None:
            return
        # print(FolderWatch.ActionName(event.action) + ": " + event.file + "\n")
        action = event.action
        if action != FolderWatch.Thread:
            self.populateDeviceTree()

    def saveModified(self, options):
        if self.m_rightPanel == None:
            return
        return self.m_rightPanel.saveModified(options)
