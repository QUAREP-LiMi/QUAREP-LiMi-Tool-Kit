import os
import subprocess, shlex
import win32com.shell.shell as shell
import wx
import glob
from forms import *
from wxApp import *

ZeissMacroName = "LPM-Zen_Blue.exe"
ZeissMacroTitle = "Zeiss Zen Blue macros"
ZeissMacroVersion = "1"

NikonMacroName = "NikonQuarepMacros30.exe"
NikonMacroTitle = "Nikon NIS-Elements macros"
NikonMacroVersion = "30"

def installZeissMacros():
    command = os.path.join(os.path.dirname(__file__), "macros\\" + ZeissMacroName)
    shell.ShellExecuteEx(lpVerb='runas', lpFile=command)
    wxGetApp().config.Write("ZeissMacroVersion", ZeissMacroVersion)

def installNikonMacros():
    command = os.path.join(os.path.dirname(__file__), "macros\\" + NikonMacroName)
    shell.ShellExecuteEx(lpVerb='runas', lpFile=command)
    wxGetApp().config.Write("NikonMacroVersion", NikonMacroVersion)

def checkMacros():
    brand = wxGetApp().config.Read("brand")
    if (brand == "Nikon") and (wxGetApp().config.Read("NikonMacroVersion") != NikonMacroVersion):
        installNikonMacros()
    if (brand == "Zeiss") and (wxGetApp().config.Read("ZeissMacroVersion") != ZeissMacroVersion):
        installZeissMacros()

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

    # Virtual event handlers, override them in your derived class
    def m_buttonSmartLPMOnButtonClick(self, event):
        folder = os.path.dirname(__file__)
        args = [os.path.join(folder, "python\\pythonw.exe"),os.path.join(folder, "SmartLPM\\SmartLPM.py")]
        subprocess.Popen(args)

    def m_buttonSmartLPMmanualOnButtonClick(self, event):
        pdf = os.path.join(os.path.dirname(__file__), "SmartLPM\\SmartLPM_manual.pdf")
        shell.ShellExecuteEx(lpVerb='open', lpFile=pdf)

    def m_brandChoiceOnChoice(self, event):
        #event.Skip()
        index = self.m_brandChoice.GetCurrentSelection()
        brand = self.m_brandChoice.GetString(index)
        if brand == "Nikon":
            if wx.MessageDialog(self, "install " + NikonMacroTitle +" ?", wx.MessageBoxCaptionStr, wx.YES_NO).ShowModal() == wx.ID_YES:
                installNikonMacros()
        if brand == "Zeiss":
            if wx.MessageDialog(self, "install " + ZeissMacroTitle + "  ?", wx.MessageBoxCaptionStr, wx.YES_NO).ShowModal() == wx.ID_YES:
                installZeissMacros()
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
            scripts = glob.glob(r"C:\Users\Public\Documents\Carl Zeiss\ZEN\Documents\Macros\QUAREP-LPM*.py")
            if len(scripts):
                sizer.Add(wx.StaticText(self.m_mainPanel, wx.ID_ANY,r"Run the QUAREP-LPM script in C:\Users\Public\Documents\Carl Zeiss\ZEN\Documents\Macros"), 0, wx.ALL, 5)
            else:
                sizer.Add(wx.StaticText(self.m_mainPanel, wx.ID_ANY,r"Install the " + ZeissMacroTitle + r" from " + os.path.join(os.path.dirname(__file__), "Macros") + r" or check https://github.com/QUAREP-LiMi for other scripts."), 0, wx.ALL, 5)
        else:
            sizer.Add(wx.StaticText(self.m_mainPanel, wx.ID_ANY,r"no scripts/macros available yet - work in process ..."), 0, wx.ALL, 5)
        self.Layout()


    def m_lampButtonOnButtonClick(self, event):
        command = '"c:\\program files\\nis-elements\\nis_ar.exe" -m "c:\\program files\\nis-elements\\macros\\MeasurePowerStability.mac"'
        subprocess.Popen(shlex.split(command))

    def m_eyeButtonOnButtonClick(self, event):
        command = '"c:\\program files\\nis-elements\\nis_ar.exe" -m "c:\\program files\\nis-elements\\macros\\MeasureDetectorGain.mac"'
        subprocess.Popen(shlex.split(command))



