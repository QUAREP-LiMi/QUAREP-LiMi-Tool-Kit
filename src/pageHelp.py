import os
import subprocess, shlex
import wx
from forms import *
from wxApp import *
import webbrowser


class pageHelp(formHelp):

    def __init__(self, parent):
        formHelp.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'measureFrame')
        self.m_htmlHelp.LoadFile(os.path.join(os.path.dirname(__file__), "Help.html"))
        self.m_htmlHelp.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.m_htmlHelpOnHtmlLinkClicked)

    # saveModified method is called by the mainFrame before destroying this page: return wx.CANCEL to cancel
    def saveModified(self,options):
        return wx.YES


    # StopWatch method is called by the mainFrame before destroying this page: no cancel possible anymore
    def stopWatch(self):
        return


    def m_htmlHelpOnHtmlLinkClicked(self,event):
        linkinfo = event.GetLinkInfo()
        webbrowser.open(linkinfo.Href, new=2)


