import os
import wx
from forms import *
from wxApp import *

class pageNoPage(panelNone):

    def __init__(self, formBrowse, parent):
        panelNone.__init__(self, parent,id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 300), style=wx.TAB_TRAVERSAL, name=wx.EmptyString)
        self.m_parent = formBrowse
        formBrowse.m_treeDates.DeleteAllItems()

    def onDestroy(self):
        pass

    # saveModified method is called by the mainFrame before destroying this page: return wx.CANCEL to cancel
    def saveModified(self,options):
        return wx.YES

    # StopWatch method is called by the mainFrame before destroying this page: no cancel possible anymore
    def stopWatch(self):
        return

    def onDataFileChange(self, event):
        return

    def onSelectDevice(self, ti):
        tree = self.m_parent.m_treeDevices
        text = ""
        while ti != tree.GetRootItem():
            text = tree.GetItemText(ti) + "\\" + text
            ti = tree.GetItemParent(ti)
        text = self.m_parent.folder + "\\" + text
        if not os.path.isdir(text):
            text = "The folder '" + text + "' does not exist"
        elif tree.GetChildrenCount(ti):
            text = "Select a device in the list on the left"
        else:
            text = "The folder '" + text + "' has no data to show"
        self.m_text.SetLabel(text)

