import os
import subprocess, shlex
import win32com.shell.shell as shell
import wx
from forms import *
from wxApp import *

def installNikonMacros():
    command = os.path.join(os.path.dirname(__file__), "macros\\NikonQuarepMacros21.exe")
    shell.ShellExecuteEx(lpVerb='runas', lpFile=command)
    wxGetApp().config.Write("NikonMacroVersion", "21")

def checkMacros():
    brand = wxGetApp().config.Read("brand")
    if (brand == "Nikon") and (wxGetApp().config.Read("NikonMacroVersion") != "21"):
        installNikonMacros()


class pageMeasure(formMeasure):

    def __init__(self, parent):
        formMeasure.__init__(self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL, 'measureFrame')
        self.brand = wxGetApp().config.Read("brand")
        self.brand_index = self.m_brandChoice.FindString(self.brand)
        if self.brand_index == -1:
            self.brand_index = 0
        self.setBrand(self.brand_index)

    def onDestroy(self):
        pass

    # saveModified method is called by the mainFrame before destroying this page: return wx.CANCEL to cancel
    def saveModified(self,options):
        return wx.YES


    # StopWatch method is called by the mainFrame before destroying this page: no cancel possible anymore
    def stopWatch(self):
        return


    # Virtual event handlers defined in forms.py, override them here
    def m_brandChoiceOnChoice(self, event):
        #event.Skip()
        index = self.m_brandChoice.GetCurrentSelection()
        brand = self.m_brandChoice.GetString(index)
        if brand == "Nikon":
            if wx.MessageDialog(self, "install Nikon macros ?", wx.MessageBoxCaptionStr, wx.YES_NO).ShowModal() == wx.ID_YES:
                installNikonMacros()
        wxGetApp().config.Write("brand",brand)
        self.brand = brand
        self.brand_index = index
        self.setBrand(index)


    def setBrand(self, index):
        panel = self.m_mainPanel
        panel.DestroyChildren()
        sizer = panel.GetSizer()
        sizer.Clear()

        self.m_brandChoice.SetSelection(index)
        brand = self.m_brandChoice.GetString(index)
        if index == 0:
            pass
        elif brand == "Nikon":
            self.m_lampButton = wx.Button(self.m_mainPanel, wx.ID_ANY,"Measure Illuminator Linearity and Stability\r\n(not for point-scanning confocals)", wx.DefaultPosition, wx.DefaultSize, 0)
            self.m_lampButton.SetBitmap(wxGetApp().LoadBitmap("Lamp64.png"))
            sizer.Add(self.m_lampButton, 0, wx.ALL, 5)
            self.m_lampButton.Bind(wx.EVT_BUTTON, self.m_lampButtonOnButtonClick)
            self.m_eyeButton = wx.Button(self.m_mainPanel, wx.ID_ANY,"Measure Detector Gain\r\n(Noise-Brightness Analysis)", wx.DefaultPosition, wx.DefaultSize, 0)
            self.m_eyeButton.SetBitmap(wxGetApp().LoadBitmap("Camera64.png"))
            sizer.Add(self.m_eyeButton, 0, wx.ALL, 5)
            self.m_eyeButton.Bind(wx.EVT_BUTTON, self.m_eyeButtonOnButtonClick)
        elif brand == "Zeiss":
            sizer.Add(wx.StaticText(self.m_mainPanel, wx.ID_ANY,"download Zeiss Zen scripts from https://github.com/QUAREP-LiMi/WG1-Automation/tree/main/Microscope_Systems."), 0, wx.ALL, 5)
        else:
            sizer.Add(wx.StaticText(self.m_mainPanel, wx.ID_ANY,"no scripts/macros available yet - work in process ..."), 0, wx.ALL, 5)
        self.Layout()


    def m_lampButtonOnButtonClick(self, event):
        command = '"c:\\program files\\nis-elements\\nis_ar.exe" -m "c:\\program files\\nis-elements\\macros\\MeasurePowerStability.mac"'
        subprocess.Popen(shlex.split(command))

    def m_eyeButtonOnButtonClick(self, event):
        command = '"c:\\program files\\nis-elements\\nis_ar.exe" -m "c:\\program files\\nis-elements\\macros\\MeasureDetectorGain.mac"'
        subprocess.Popen(shlex.split(command))



