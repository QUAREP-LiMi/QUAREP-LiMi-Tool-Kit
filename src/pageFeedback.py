import os
import subprocess, shlex
import wx
from forms import *
from wxApp import *
import webbrowser


class pageFeedback(formHTML):

    def __init__(self, parent):
        formHTML.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'feedbackFrame')
        self.m_html.LoadFile(os.path.join(os.path.dirname(__file__), "Feedback.html"))
        self.m_html.Bind(wx.html.EVT_HTML_LINK_CLICKED, self.m_htmlOnHtmlLinkClicked)

    # saveModified method is called by the mainFrame before destroying this page: return wx.CANCEL to cancel
    def saveModified(self,options):
        return wx.YES

    # onDestroy is called before the page is removed
    def onDestroy(self):
        pass

    # StopWatch method is called by the mainFrame before destroying this page: no cancel possible anymore
    def stopWatch(self):
        return

    def m_htmlOnHtmlLinkClicked(self,event):
        linkinfo = event.GetLinkInfo()
        webbrowser.open(linkinfo.Href, new=2)


