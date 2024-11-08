import os
import re
import subprocess
import ctypes
import shutil
from wxApp import *
from forms import *
from wxApp import *

# some kernel32 constants
SYNCHRONIZE = 0x00100000
INFINITE = -1
WAIT_ABANDONED = 0x00000080
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
CREATE_NO_WINDOW = 0x08000000

#g_detphocal_path = r"L:\local\QUAREP\WG2_Detectors\Tools\Analysis Software\calibration-tools-v0.7.1_x64\cli_calibration_tool.exe"
g_detphocal_path = os.path.join(os.path.dirname(__file__), r"caltool\cli_calibration_tool.exe")

class DetPhoCalOption:

	def __init__(self):
		self.name = ""
		self.type = ""
		self.desc = ""
		self.value = ""
		self.default_value = ""
		self.widget = None
		self.hidden = False

	def setValue(self, value):
		if self.type == "BOOL" or self.type == "":
			if value:
				self.value = "1"
			else:
				self.value = "0"
		elif value is None:
			self.value = ""
		else:
			self.value = str(value)

	def formatArg(self):
		if not len(self.value):
			return ""
		arg = "--" + self.name
		if self.type == "":
			if self.value == "1":
				return arg
			else:
				return ""
		arg += "="
		if " " in self.value:
			arg += '"' + self.value + '"'
		else:
			arg += self.value
		return arg


class DetPhoCalOptions(list):

	def __init__(self):
		list.__init__(self)

	def init(self):
		with open(os.path.join(os.path.dirname(__file__), r"caltool\cli_calibration_tool_help.txt")) as file:
			desc = ""
			for line in file:
				line = line.rstrip()
				if line[0:4] == "  --":
					if len(desc):
						self.add(desc)
					desc = line
				else:
					desc += " " + line.strip(" ")
			if len(desc):
				self.add(desc)
		self.set(r"export-format", "SVG", True)
		self.set(r"exportpath", "", True)

	def add(self, desc):
		match = re.match(r"  --([^ =]+)(=([^ ]+))?\s*([^\(]+)?(\(default: (.+)\))?", desc)
		if match:
			fields = match.groups()
			option = DetPhoCalOption()
			option.name = fields[0]
			if fields[2] is not None:
				option.type = fields[2]
			if fields[3] is not None:
				option.desc = fields[3]
			if fields[5] is not None:
				option.default_value = fields[5]
			option.value = option.default_value
			self.append(option)

	def set(self, name, value, hidden=None):
		for option in self:
			if option.name == name:
				option.value = value
				if hidden is not None:
					option.hidden = hidden
				return

	def format(self):
		args = []
		for option in self:
			if option.value != option.default_value:
				arg = option.formatArg()
				if len(arg):
					args.append(arg)
		return ' '.join(args)

	def load(self, filename):
		if not os.path.exists(filename):
			basename = os.path.basename(filename)
			dir = os.path.dirname(filename)
			# try unit directory
			dir = os.path.dirname(dir)
			filename = os.path.join(dir,basename)
			if not os.path.exists(filename):
				# try model directory
				dir = os.path.dirname(dir)
				filename = os.path.join(dir,basename)
				if not os.path.exists(filename):
					# try detectors directory
					dir = os.path.dirname(dir)
					filename = os.path.join(dir,basename)
					if not os.path.exists(filename):
						# give up
						return 0
		with open(filename) as file:
			for line in file:
				fields = line.rstrip().split('=',2)
				if len(fields) == 2:
					self.set(fields[0],fields[1])
		return 1
        
	def save(self,filename):
		with open(filename,"w") as file:
			for option in self:
				file.write(option.name + "=" + option.value + "\n")
		# copy to unit, model and Detector folders
		base = os.path.basename(filename)
		dir = os.path.dirname(os.path.dirname(filename))
		shutil.copy2(filename,dir)
		dir = os.path.dirname(dir)
		shutil.copy2(filename,dir)
		dir = os.path.dirname(dir)
		shutil.copy2(filename,dir)


g_detphocalOptions = DetPhoCalOptions()
g_detphocalOptions.init()

g_detphocalAutoOptions = DetPhoCalOptions()
g_detphocalAutoOptions.init()

class dialogDetectorPhotonCalibration(formDetectorPhotonCalibration):
	def __init__(self, parent, folder):
		formDetectorPhotonCalibration.__init__(self, parent)
		self.filename = os.path.join(folder,"caltool.txt")
		self.arguments = ""
		main_sizer = self.GetSizer()
		option_sizer = main_sizer.GetItem(0).GetSizer()
		g_detphocalOptions.load(self.filename)
		for option in g_detphocalOptions:
			option.widget = None
			if not option.hidden:
				label = wx.StaticText(self, wx.ID_ANY, option.name)
				option_sizer.Add(label, 0, wx.ALL, 5)
				edit = None
				if option.type == "BOOL" or option.type == "":
					edit = wx.CheckBox(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize)
					if option.value == "True" or option.value == "1":
						edit.SetValue(True)
					else:
						edit.SetValue(False)
				else:
					edit = wx.TextCtrl(self, wx.ID_ANY, option.value, wx.DefaultPosition, wx.DefaultSize)
				option_sizer.Add(edit, 0, wx.ALL, 5)
				desc = wx.StaticText(self, wx.ID_ANY, option.desc)
				option_sizer.Add(desc, 1, wx.ALL, 5)
				option.widget = edit
		option_sizer.Layout()
		main_sizer.Layout()
		wxResizePanelToContent(self)
		self.Center()
		self.m_btnOK.SetFocus()

	# Virtual event handlers, override them in your derived class
	def m_btnOKOnButtonClick(self, event):
		self.arguments = ""
		global g_detphocalOptions
		for option in g_detphocalOptions:
			if option.widget is not None:
				option.setValue(option.widget.GetValue())
			if len(option.value) and not (option.type == "" and option.value == "False"):
				self.arguments += " --" + option.name
				if option.type != "":
					self.arguments += '="' + option.value + '"'
		g_detphocalOptions.save(self.filename)
		formDetectorPhotonCalibration.m_btnOKOnButtonClick(self, event)

	def formatArgs(self):
		return g_detphocalOptions.format()


class DetPhoCalProcess:
	def __init__(self, folder):
		self.folder = folder
		self.cmd = ""
		self.proc = None
		self.pid = -1
		self.exit_code = None
		self.handle = -1
		self.output = ""
		self.errors = ""

	def start(self, args):
		self.exit_code = None
		self.output = ""
		self.errors = ""
		cwd = os.path.dirname(g_detphocal_path)
		self.cmd = '"' + g_detphocal_path + '" ' + args
		self.proc = subprocess.Popen(self.cmd, cwd=os.path.dirname(g_detphocal_path), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, creationflags=CREATE_NO_WINDOW)
		self.pid = self.proc.pid
		self.handle = ctypes.windll.kernel32.OpenProcess(SYNCHRONIZE, False, self.proc.pid)

	def close(self):
		self.exit_code = -1
		self.output = ""
		self.errors = ""
		try:
			self.exit_code = self.proc.poll()
			if self.exit_code is None:
					self.exit_code = os.waitpid(self.pid, 0)[1]
			out_err = self.proc.communicate()
			self.output = out_err[0].decode("utf-8")
			self.errors = out_err[1].decode("utf-8")
		except:
			pass
		self.handle = -1
		self.proc = None
		self.pid = -1
		self.save()

	def save(self):
		try:
			f = open(os.path.join(self.folder,"out.txt"), "w")
		except:
			return
		f.write(self.cmd + "\n")
		f.write(self.output)
		f.write(self.errors)
		f.close()

	def wait(self, timeout=0):
		ret = ctypes.windll.kernel32.WaitForSingleObject(self.handle, timeout)
		if ret == WAIT_TIMEOUT:
			return 0
		self.close()
		return 1

	def kill(self):
		self.proc.kill()
		self.close()


class DetPhoCalProcesses(dict):
	def __init__(self):
		dict.__init__(self)

	def start(self, folder, args, bright, dark):
		if folder in self.keys():
			p = self[folder]
			p.kill()
		else:
			p = DetPhoCalProcess(folder)
			self[folder] = p
		args += ' --exportpath="' + folder + '" "' + folder + '\\' + bright + '" "' + folder + '\\' + dark + '"'
		p.start(args)

	def kill(self, folder):
		if folder not in self.keys():
			return
		self[folder].kill()
		self.pop(folder)

	def check(self, folder):
		if folder not in self.keys():
			return None
		proc = self[folder]
		completed = proc.wait(0)
		if not completed:
			return None
		self.pop(folder)
		return proc

	def checkAll(self):
		if not len(self):
			return None
		handles = {}
		for folder, proc in self.items():
			handles[proc.handle] = proc
		arr_type = ctypes.c_uint64 * len(handles)
		handle_array = arr_type(*handles.keys())
		ret = ctypes.windll.kernel32.WaitForMultipleObjects(len(handle_array), handle_array, False, 0)
		if ret < WAIT_OBJECT_0 or ret >= (WAIT_OBJECT_0 + len(handle_array)):
			return None
		proc = handles[handle_array[ret - WAIT_OBJECT_0]]
		proc.close()
		self.pop(proc.folder)
		return proc

	def isRunning(self, folder):
		return folder in self.keys()


g_detphocalProcesses = DetPhoCalProcesses()
