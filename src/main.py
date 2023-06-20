#!/usr/bin/env python

"""Basic application class."""

__author__ = "Kees van der Oord <Kees.van.der.Oord@nikon.com>"
__cvsid__ = "QuaRepDataBrowser.main.py"
__version__ = "0.1.15"
__date__ = "2023-06-20"

import wx

'''
history
2023-06-20: 15 Kees:
    Nikon macros version 18: included vc 2022 runtime libraries
2023-06-04: 14 Kees:
    fixed python bugs in Measure page
    added m_pages library
    moved measure page to first position
    remember selected page
2023-06-04: 13 Kees:
    avoid exception when no data was parsed from the text file: len(data.x_data) == 0
    added filter for temperature
    recreate the wxmplot when x_unit or temperature filter changes changes
    moved <> and >< buttons to filter bar
    added 'Browse' and 'Measure' to top toolbar
    moved code to wxApp.py, pageBrowse.py, pageMeasure.py
    added listing to commands on pipe and forwarding arguments to first instance
2012-04-24: 12 Kees:
    first argument is folder to activate
    changed to \ in paths to accomodate device names with /
2023-03-30: 11 Kees: 
    added support for txt files with all line terminators           
    added support for thorlabs csv files
2023-03-29: 10 Kees: changed to wxmplot to support right y-axis for temperature
2023-02-22: 9 Kees: downgraded numpy to 1.23.5 because 1.24.1 removed np.float() used in wxPython
2023-01-22: 8 Kees: added support for .txt file and resolved problem with internationalization
2022-11-07: 7 Kees: added filters and save to file
2022-05-25: 6 Kees: fixed exception when clicking in empty space of trees and file access conflict with NIS
2022-05-24: 5 Kees: added exception handling for file format anomalies
2022-05-23: 4 Kees: added wix installer
2022-05-08: 3 Kees: added automatic detection of new files/folders; changed default folder to c:\quarep
2022-05-06: 2 Kees: added minimal height for graphs, freeze/thaw and wait cursor during loading
2022-05-05: 1 Kees: born

install instructions: 
unpack a portable python 3.9 distribution to folder 'python' (3.10 and 3.11 are incompatible with wxPython)
in python39._pth, add a line with '..' below '.' and remove the # in front of import site
download get-pip.py
python\python get-pip.py
python\scripts\pip install pywin32 wxwidgets wxmplot
python\scripts\pip list
Package             Version
------------------- -------
contourpy           1.0.7
cycler              0.11.0
fonttools           4.39.3
importlib-resources 5.12.0
kiwisolver          1.4.4
matplotlib          3.7.1
numpy               1.24.2
packaging           23.0
Pillow              9.4.0
pip                 23.0.1
pyparsing           3.0.9
python-dateutil     2.8.2
pywin32             306
PyYAML              6.0
setuptools          67.6.1
six                 1.16.0
webcolors           1.13
wheel               0.40.0
wxmplot             0.9.55
wxPython            4.2.0
wxutils             0.3.0
wxwidgets           1.0.5
zipp                3.15.0

run:
python\pythonw main.py
'''

#import wx.lib.agw.persist as PM
#from wxApp import wxSetApp, wxGetApp
from pageBrowse import *
from pageMeasure import *
from pageHelp import *

# listen to a pipe for commands, such as showing a results page
from CommandPipe import *
QuaRepLiMiPipeName = 'QUAREP-LiMi-ToolKit-Pipe'

class MainFrame(mainFrame):

    def __init__(self, parent):
        mainFrame.__init__(self, parent)
        self.m_pages = {}
        self.m_page = None
        self.m_page_id = -1
        self.SetIcon(wx.Icon(os.path.join(os.path.dirname(__file__), "product.ico")))
        self.SetName("mainFrame")
        self.SetTitle("QUAREP-LiMi Tool Kit " + __version__)
        self.addPage("Measure","Measure32.png",pageMeasure)
        self.addPage("Browse Results","Results32.png",pageBrowse)
        self.addPage("Help","Help32.png",pageHelp)
        self.m_toolbar.Realize()
        activePage = wxGetApp().config.Read("page")
        if activePage == "":
            activePage = "Measure"
        self.setPage(activePage)

    def addPage(self, name, icon, func):
        tool = self.m_toolbar.AddTool(wx.ID_ANY, name,
            wxGetApp().LoadIcon(icon), wx.NullBitmap, wx.ITEM_CHECK, name, name, None)
        self.Bind(wx.EVT_TOOL, self.m_toolClicked, id=tool.GetId())
        tool.createPage = func
        tool.name = name
        self.m_pages[tool.GetId()] = tool
        self.m_pages[name] = tool

    def m_toolClicked(self, event):
        self.setPage(event.GetId())

    # page_id can be toolbar control ID or page name
    def setPage(self, page_id):
        if self.m_page != None:
            if self.m_page.saveModified(wx.YES_NO|wx.CANCEL) == wx.CANCEL:
                page_id = self.m_page_id

        if isinstance(page_id, str):
            if page_id in self.m_pages:
                page_id = self.m_pages[page_id].GetId()
            else:
                return

        for index in range(self.m_toolbar.GetToolCount()):
            id = self.m_toolbar.FindToolByIndex(index).GetId()
            self.m_toolbar.ToggleTool(id, id == page_id)

        if page_id == self.m_page_id:
            return

        if self.m_page != None:
            self.m_page.stopWatch()

        self.m_page_id = page_id

        panel = self.m_mainPanel
        panel.DestroyChildren()
        sizer = panel.GetSizer()
        sizer.Clear()
        self.m_page = None
        tool = self.m_pages[page_id]
        if tool != None:
            self.m_page = tool.createPage(panel)
        if self.m_page != None:
            sizer.Add(self.m_page, 1, wx.EXPAND, 5)
            wxGetApp().config.Write("page",tool.name)
        self.Layout()

    def onPipeCommand(self,event):
        if event.type == CommandPipe.CommandEvent:
            try:
                value = eval(event.value)
                self.DoCommands(value)
                return
            except:
                pass

    def DoCommands(self, argv):
        # just one command support now: active folder
        if len(argv) > 0:
            self.setPage("Browse Results")
            self.m_page.SetActiveFolder(argv[0])


class App(wx.App):

    def __init__(self):
        self._persistMgr = None
        self.frame = None
        self.pipe = None
        wx.App.__init__(self)


    def OnInit(self):
        wx.App.OnInit(self)
        wxSetApp(self)

        # fix for datetime.strptime exception 'unknown locale'
        locale.setlocale(locale.LC_ALL, 'en_US')

        # process command line arguments
        self.pipe = CommandPipe(QuaRepLiMiPipeName)
        args = sys.argv
        args.pop(0)
        if len(args):
            if self.pipe.send(str(args)):
                return False

        self._persistMgr = PM.PersistenceManager.Get()
        _configFile = wx.StandardPaths.Get().GetUserDataDir() + "\\QuaRep\\QuaRepDataBrowser\\QuaRepDataBrowser.ini"
        self._persistMgr.SetPersistenceFile(_configFile)
        self.config = wx.Config("QuaRepToolKit")
        self.iconFolder = os.path.join(os.path.dirname(__file__), "icons")

        self.frame = MainFrame(None)
        self.SetTopWindow(self.frame)
        self.frame.Bind(wx.EVT_CLOSE, self.OnCloseMain)

        # self._persistMgr.RegisterAndRestoreAll(self.frame)
        self._persistMgr.RegisterAndRestore(self.frame)
        self.frame.Show()

        if not self.pipe.listen(self.frame,0):
            print("error: could not open pipe " + QuaRepLiMiPipeName + "\r\n")
        self.frame.Bind(EVT_COMMANDPIPE_EVENT, self.frame.onPipeCommand, self.pipe)

        if len(args):
            self.frame.DoCommands(args)

        return True


    def OnCloseMain(self, event):
        answer = self.frame.m_page.saveModified(wx.YES_NO|wx.CANCEL)
        if answer == wx.CANCEL:
            return
        self.pipe.abort()
        self._persistMgr.SaveAndUnregister(self.frame)
        self.frame.m_page.stopWatch()
        event.Skip()


    def LoadIcon(self, name):
        return wx.Icon(os.path.join(self.iconFolder,name))


    def LoadBitmap(self, name):
        return wx.Bitmap(os.path.join(self.iconFolder,name), wx.BITMAP_TYPE_ANY)


def main():
    app = App()
    app.MainLoop()


if __name__ == '__main__':
    main()
