import win32pipe, win32file
import threading
import wx.lib.newevent # wxPython

CommandPipeEvent, EVT_COMMANDPIPE_EVENT = wx.lib.newevent.NewCommandEvent()

class CommandPipe(threading.Thread):

    # the CommandPipeEvent events have a 'type' and a 'value' variable.
    # the 'type' variable can have these values:
    ThreadStateEvent = 0
    CommandEvent = 1
    def CommandTypes(commandType: int):
        ECOMMANDTYPES = {
            0: "ThreadState", # value is 0 (stopped) or 1 (started)
            1: "Command",     # value is the command
        }
        return ECOMMANDTYPES.get(commandType, "Unknown")

    def __init__ (self, pipeName: str) -> object:
        threading.Thread.__init__(self)
        self.pipeName = '\\\\.\\pipe\\' + pipeName
        self.parent = None
        self.id = -1
        self.pipe = win32file.INVALID_HANDLE_VALUE

    def GetId(self):
        return self.id

    def __del__(self):
        self.abort()

    # The send command returns True if the pipe existed and the command could be sent
    def send(self, command: str):
        pipe = win32file.INVALID_HANDLE_VALUE
        try:
            pipe = win32file.CreateFile(self.pipeName, win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None)
        except:
            return False
        if pipe == win32file.INVALID_HANDLE_VALUE:
            return False
        result, written  = win32file.WriteFile(pipe,bytes(command,"UTF-16"))
        if result != 0:
            return False
        win32file.CloseHandle(pipe)
        return True

    # The listen command starts listening on the pipe for commands
    def listen(self, parent: wx.Window, id: int):
        self.abort()
        self.parent = parent
        self.id = id
        self.pipe = win32file.INVALID_HANDLE_VALUE
        try:
            self.pipe = win32pipe.CreateNamedPipe(self.pipeName, win32pipe.PIPE_ACCESS_DUPLEX, win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT, 1, 65536, 65536, 0, None)
        except:
            None
        if self.pipe == win32file.INVALID_HANDLE_VALUE:
            return False
        self.start()
        return True

    def abort(self):
        if not self.is_alive():
            return
        pipe = self.pipe
        self.pipe = win32file.INVALID_HANDLE_VALUE
        tmp = win32file.CreateFile(self.pipeName, win32file.GENERIC_WRITE, 0, None, win32file.OPEN_EXISTING, 0, None)
        win32file.CloseHandle(tmp)
        win32file.CloseHandle(pipe) # this will abort the loop waiting for the commands
        self.join(1)

    def run(self):
        wx.PostEvent(self.parent, CommandPipeEvent(self.id, source=self, type=CommandPipe.ThreadStateEvent, value=1))
        while self.pipe != win32file.INVALID_HANDLE_VALUE:
            win32pipe.ConnectNamedPipe(self.pipe, None)
            result = 0
            while result == 0:
                result = 1
                try:
                    result, data = win32file.ReadFile(self.pipe,4096)
                except:
                    None
                if not result:
                    wx.PostEvent(self.parent, CommandPipeEvent(self.id, source=self, type=CommandPipe.CommandEvent, value=data.decode('utf-16')))
            if self.pipe != win32file.INVALID_HANDLE_VALUE:
                win32pipe.DisconnectNamedPipe(self.pipe)
        wx.PostEvent(self.parent, CommandPipeEvent(self.id, source=self, type=CommandPipe.ThreadStateEvent, value=0))
