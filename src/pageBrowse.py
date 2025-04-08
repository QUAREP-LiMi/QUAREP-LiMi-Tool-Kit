#import csv
import math
import sys
import os
import locale
import re
from datetime import datetime
from pathlib import Path, WindowsPath

import win32security
import wx.lib.agw.persist as PM
import wxmplot
#import matplotlib.pyplot as mpl

from FolderWatch import *  # requires pyWin32
from forms import *
from wxApp import *
from pageLightSourceResults import *
from pageDetectorResults import *
from pageNoPage import *

def findTreeItem(tree, parent, name):
    item, cookie = tree.GetFirstChild(parent)
    while item.IsOk():
        if tree.GetItemText(item) == name:
            return item
        item = tree.GetNextSibling(item)
    return None

def findTreeItemPathList(tree, pathlist):
    item = tree.GetRootItem()
    for name in pathlist:
        item = findTreeItem(tree, item, name)
        if item is None:
            break
    return item

def findTreeItemPath(tree, path):
    return findTreeItemPathList(tree, path.split('\\'))

def findOrInsertTreeItem(tree, parent, name):
    item, cookie = tree.GetFirstChild(parent)
    while item.IsOk():
        item_text = tree.GetItemText(item)
        if item_text == name:
            return item
        item = tree.GetNextSibling(item)
    item = tree.AppendItem(parent,name)
    # work around for wxPython 4.2.1 bug https://github.com/wxWidgets/wxWidgets/issues/23718: no update to paint added toggle button when inserting first child
    if tree.GetChildrenCount(parent) == 1:
        if tree.IsExpanded(parent):
            tree.Collapse(parent)
            tree.Expand(parent)
        else:
            tree.Expand(parent)
            tree.Collapse(parent)
    #
    tree.SortChildren(parent)
    return item

def getPrevTreeSibling(tree, ti):
    #  wxPython 4.2.1  bug: wx.TreeCtrl.getPrevSibling is defined wrong: without the argument ???
    parent = tree.GetItemParent(ti)
    prev_ti = None
    next_ti, cookie = tree.GetFirstChild(parent)
    while next_ti.IsOk():
        if next_ti is ti:
            return prev_ti
        prev_ti = next_ti
        next_ti = tree.GetNextSibling(next_ti)
    return None

def treeExpandBranch(tree, item):
    parent = tree.GetItemParent(item)
    while parent.IsOk() and parent != tree.GetRootItem():
        tree.Expand(parent)
        parent = tree.GetItemParent(parent)

class pageBrowse(formBrowse):

    def __init__(self, parent):
        formBrowse.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'browseFrame')

        # widget initialization
        self.m_mainSplitter.SetName("browseSplitter")
        self.m_rightPanel = None
        self.initDeviceTree()

        # simple member variable initialization
        # todo: load categories from config() ?
        self.categories = {
            "none": {"name": "none", "folder": "", "class": pageNoPage},
            "Detectors": {"name": "Detectors", "folder": "Detectors", "class": pageDetectorResults },
            "Light Sources": {"name": "Light Sources", "folder": "Light Sources", "class": pageLightSourceResults}
        }
        self.folderWatch = None
        self.folder = ""
        self.category = ""
        self.deviceFolder = ""
        self.deviceTi = None
        self.inSelectItem = False

        folder = wxGetApp().config.Read("folder")
        if not os.path.isdir(folder):
            folder = ""
        while len(folder) == 0:
            dlg = wx.DirDialog(None, "QuaRep Main Data Folder", "C:\\QUAREP", wx.DD_DEFAULT_STYLE)
            if wx.ID_OK != dlg.ShowModal():
                return
            folder = dlg.GetPath()
            if not os.path.isdir(folder):
                os.mkdir(folder)
            if not os.path.isdir(folder):
                folder = ""

        self.SetFolder(folder,wxGetApp().config.Read("device"))

        # self.canvas = Canvas(self.m_rightPanel, size=(0, 0))
        # self.CreatePrintData()

    def onDestroy(self):
        self.clearRightPanel()
        self.stopWatch()

    def SetActiveFolder(self, path):
        folder, unit = os.path.split(path)
        folder, model = os.path.split(folder)
        folder, category = os.path.split(folder)
        if category in self.categories:
            self.SetFolder(folder, path)

    def initDeviceTree(self):
        tree = self.m_treeDevices
        #tree.AppendColumn(u"Devices")
        tree.folders = {}

    def findFirstDevice(self):
        tree = self.m_treeDevices
        category, cookie =  tree.GetFirstChild(tree.GetRootItem())
        while category.IsOk():
            model, cookie = tree.GetFirstChild(category)
            while model.IsOk():
                unit, cookie =tree.GetFirstChild(model)
                while unit.IsOk():
                    return unit
                model = tree.GetNextSibling(model)
            category = tree.GetNextSibling(category)
        return None

    def SetFolder(self, folder, device):
        ti = None
        if device.startswith(folder):
            device = device[len(folder)+1:]
        if self.folder != folder:
            self.folder = folder
            wxGetApp().config.Write("folder", self.folder)
            self.m_folder.SetLabel(self.folder)
            self.populateDeviceTree()
            self.StartWatch(self.folder)
            ti = findTreeItemPath(self.m_treeDevices, device)
            if ti is None:
                ti = self.findFirstDevice()
        if (ti is None) and len(device):
            ti = findTreeItemPath(self.m_treeDevices,device)
        if ti is None:
            ti, cookie = self.m_treeDevices.GetFirstChild(self.m_treeDevices.GetRootItem())
        if (ti is not None) and ti.IsOk() and (self.m_treeDevices.GetSelection() != ti):
            self.m_treeDevices.SelectItem(ti)
            treeExpandBranch(self.m_treeDevices, ti)
            self.m_treeDevices.EnsureVisible(ti)

    def populateDeviceTree(self):
        self.deviceTi = None
        tree = self.m_treeDevices
        tree.DeleteAllItems()
        tree.AddRoot('root')
        tree.folders = {}
        for cat in self.categories:
            if cat != "none":
                self.populateDevices(tree, self.categories[cat])

    def m_browseOnButtonClick(self, event):
        dlg = wx.DirDialog(self, "Choose data directory", self.folder, wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() != wx.ID_OK:
            return
        self.SetFolder(dlg.GetPath(), "")

    def StartWatch(self, folder):
        self.stopWatch()
        self.folderWatch = FolderWatch(self, 1, folder,
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE,
            True)
        self.Bind(EVT_FOLDER_CHANGE_EVENT, self.onFolderChange, self.folderWatch)

    def stopWatch(self):
        if self.folderWatch:
            self.folderWatch.abort()
            self.folderWatch = None

    def populateDevices(self, tree, category):
        folder = category["folder"]
        name = category["name"]
        root = tree.GetRootItem()
        devices = tree.AppendItem(tree.GetRootItem(), name)
        path = os.path.join(self.folder,folder)
        if not os.path.isdir(path):
            return
        tree.folders[path] = devices
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
                mti = tree.AppendItem(devices, model)
                tree.folders[model_folder] = mti
                for unit in units:
                    uti = tree.AppendItem(mti, unit)
                    unit_folder = os.path.join(model_folder, unit)
                    tree.SetItemData(uti, {"folder": unit_folder, "category": category["name"]})
                    tree.folders[unit_folder] = uti
                #tree.Expand(mti)
        #tree.Expand(devices)

    def insertDevice(self, pathlist):
        # this function some duplicate code with populateDevices
        # todo: refactor to eliminate the duplication
        if len(pathlist) > 3:
            pathlist = pathlist[:3]
        tree = self.m_treeDevices
        ti = tree.GetRootItem()
        path = self.folder
        for i in range(len(pathlist)):
            ti = findOrInsertTreeItem(tree, ti, pathlist[i])
            path = path + "\\" + pathlist[i]
            tree.folders[path] = ti
        if len(pathlist) == 3:
            tree.SetItemData(ti, {"folder": os.path.join(self.folder, "\\".join(pathlist)), "category": pathlist[0]})

    #def m_treeDevicesOnTreelistSelectionChanged(self, event):
    def m_treeDevicesOnTreeSelChanged(self, event):
        event.Skip()
        tree = self.m_treeDevices
        if not tree:  #https://github.com/wxWidgets/Phoenix/issues/1500: TreeCtrl sends tree events after the tree is destroyed
            return
        ti = tree.GetSelection()
        self.onSelectDevice(ti)

    def clearRightPanel(self):
        if self.m_rightPanel:
            self.m_rightPanel.onDestroy()
            self.m_rightPanel.Destroy()
        self.m_rightPanel = None

    def createRightPanel(self, category):
        self.m_mainSplitter.Unsplit(self.m_rightPanel)
        self.clearRightPanel()
        self.m_rightPanel = category["class"](self, self.m_mainSplitter)
        self.m_mainSplitter.SplitVertically(self.m_leftPanel, self.m_rightPanel, 300)
        self.Layout()
        self.Update()
        self.category = category["name"]

    def onSelectDevice(self, ti):
        self.saveModified(wx.YES_NO)
        tree = self.m_treeDevices
        self.deviceTi = ti
        tree.SelectItem(ti)
        if (ti is not None) and ti.IsOk():
            data = tree.GetItemData(ti)
            if data is not None:
                category = data["category"]
                if self.category != category:
                    self.createRightPanel(self.categories[category])
                self.deviceFolder = data["folder"]
                self.m_rightPanel.onSelectDevice(ti)
                wxGetApp().config.Write("device", self.deviceFolder)
                return
        # not a device folder: nothing to show ...
        self.createRightPanel(self.categories["none"])
        self.m_rightPanel.onSelectDevice(ti)
        return

    def m_treeDatesOnTreelistSelectionChanged(self, event):
        if event is not None:
            event.Skip()
        tree = self.m_treeDates
        ti = tree.GetSelection()
        self.onSelectDate(ti)

    def onSelectDate(self, ti):
        if self.m_rightPanel is None:
            return
        self.m_rightPanel.onSelectDate(ti)

    def insertDeviceTreeItem(self, folder):
        pathlist = folder.split('\\')
        ti = findTreeItemPathList(self.m_treeDevices,pathlist)
        if ti is not None:
            return
        if len(pathlist):
            if pathlist[0] in self.categories:
                self.insertDevice(pathlist)

    def insertOrRenameDeviceTreeItem(self, folder, old_name):
        tree = self.m_treeDevices
        pathlist = folder.split('\\')
        oldpathlist = old_name.split('\\')
        if len(pathlist) < 1:
            return
        new_name = pathlist[-1]
        pathlist[-1] = oldpathlist[-1]
        ti = findTreeItemPathList(tree,pathlist)
        if ti is None:
            self.insertDeviceTreeItem(folder)
        else:
            path = self.folder + "\\" + old_name
            if path in tree.folders.keys():
                del tree.folders[path]
            path = self.folder + "\\" + folder
            tree.folders[path] = ti
            tree.SetItemText(ti,new_name)
            if len(pathlist) == 3: # unit folder
                data = tree.GetItemData(ti)
                data["folder"] = path
                tree.SetItemData(ti, data)
                if ti is self.deviceTi:
                    self.onSelectDevice(ti)
            if len(pathlist) == 2: # model folder
                child_ti, cookie = tree.GetFirstChild(ti)
                pathlist.append("")
                while child_ti.IsOk():
                    data = tree.GetItemData(child_ti)
                    old_path = data["folder"]
                    if old_path in tree.folders.keys():
                        del tree.folders[old_path]
                    new_path = path + "\\" + tree.GetItemText(child_ti)
                    data["folder"] = new_path
                    self.m_treeDevices.SetItemData(child_ti, data)
                    tree.folders[new_path] = child_ti
                    if ti is self.deviceTi:
                        self.onSelectDevice(ti)
                    child_ti = self.m_treeDevices.GetNextSibling(child_ti)

    def removeDeviceTreeItem(self, folder):
        tree = self.m_treeDevices
        pathlist = folder.split('\\')
        path = self.folder + "\\" + folder
        ti = findTreeItemPathList(tree,pathlist)
        if ti is None:
            return
        next_ti = None
        if (self.deviceTi is not None) and self.deviceTi.IsOk():
            data = tree.GetItemData(self.deviceTi)
            if data is not None and data["folder"].startswith(path):
                next_ti = tree.GetNextSibling(ti)
                if (next_ti is None) or (not next_ti.IsOk()):
                    next_ti = getPrevTreeSibling(tree,ti)
                if (next_ti is None) or (not next_ti.IsOk()):
                    next_ti = tree.GetItemParent(ti)
        for key in list(tree.folders):
            if key.startswith(path):
                del tree.folders[key]
        tree.Delete(ti)
        if next_ti is not None:
            self.onSelectDevice(next_ti)

    def onFolderChange(self, event):
        action = event.action
        file = event.file
        #print("> onFolderChange(" + str(action) + "," + file + ")")
        if self.folderWatch:
            self.folderWatch.rearm(action, file)
        if action == FolderWatch.Thread:
            return
        fullpath = os.path.join(self.folder, file)
        # update the device tree
        if os.path.isdir(fullpath) or (fullpath in self.m_treeDevices.folders.keys()):
            if action == FolderWatch.Deleted:
                self.removeDeviceTreeItem(file)
            elif action == FolderWatch.Created:
                self.insertDeviceTreeItem(file)
            elif action == FolderWatch.Renamed:
                self.insertOrRenameDeviceTreeItem(file,event.old_name)
        # notify the panel
        pathlist = file.split('\\')
        if len(pathlist) > 3:
            pathlist = pathlist[:3]  # category/model/unit
        deviceFolder = os.path.join(self.folder,'\\'.join(pathlist))
        if (self.m_rightPanel is not None) and self.deviceFolder == deviceFolder:
            self.m_rightPanel.onDataFileChange(event)
        #print("< onFolderChange(" + str(action) + "," + file + ")")

    def saveModified(self, options):
        if self.m_rightPanel is None:
            return
        return self.m_rightPanel.saveModified(options)
