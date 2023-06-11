import win32file, win32event, win32con, pywintypes, win32con # pywin32
import threading
import wx.lib.newevent # wxPython

FolderChangeEvent, EVT_FOLDER_CHANGE_EVENT = wx.lib.newevent.NewCommandEvent()


class FolderWatch(threading.Thread):
    Thread  = 0
    Created = 1
    Deleted = 2
    Updated = 3
    Renamed = 5

    def ActionName(action: int):
        ACTIONS = {
            0: "Thread",
            1: "Created",
            2: "Deleted",
            3: "Updated",
            4: "Renamed from something",
            5: "Renamed"
        }
        return ACTIONS.get(action, "Unknown")

    old_name: str

    def __init__ (self, parent: wx.Window, id: int, folder: str, mask: int, recursive: bool) -> object:
        """

        :rtype: object
        """
        threading.Thread.__init__(self)
        self.parent = parent
        self.folder = folder
        self.id = id
        self.mask = mask
        self.recursive = recursive
        self.old_name = ""
        self.lock = threading.Lock()
        self.postedActions = [[], [], [], [], [], []] # 6 for actions 1-5
        self.stop_event = win32event.CreateEvent(None, True, 0, None)
        self.overlapped = pywintypes.OVERLAPPED()
        self.overlapped.hEvent = win32event.CreateEvent(None, 0, 0, None)
        self.buffer = win32file.AllocateReadBuffer(8092)
        self.handles =  self.overlapped.hEvent, self.stop_event
        self.handle = win32file.CreateFile (
            self.folder,
            0x0001,  # FILE_LIST_DIRECTORY,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS | win32file.FILE_FLAG_OVERLAPPED,
            None
        )
        if self.handle:
            self.start()

    def __del__(self):
        self.abort()

    def GetId(self):
        return self.id

    def abort(self):
        win32event.SetEvent(self.stop_event)
        self.join(1)

    def run(self):
        wx.PostEvent(self.parent, FolderChangeEvent(self.id, source=self, action=0, file="started"))
        #print("thread started.")
        while 1:
            results = win32file.ReadDirectoryChangesW (
                self.handle,
                self.buffer,
                self.recursive,
                self.mask,
                #win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                #win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                #win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                #win32con.FILE_NOTIFY_CHANGE_SIZE |
                #win32con.FILE_NOTIFY_CHANGE_LAST_WRITE, #|
                #win32con.FILE_NOTIFY_CHANGE_SECURITY,
                self.overlapped,
                None
            )
            result = win32event.WaitForMultipleObjects(self.handles, False, win32event.INFINITE)
            #print("win32event.WaitForMultipleObjects result = " + str(result) + "\n")
            if result != win32event.WAIT_OBJECT_0:
                wx.PostEvent(self.parent, FolderChangeEvent(self.id, source=self, action=0, file="stopped"))
                #print("thread stopped.")
                return
            count = win32file.GetOverlappedResult(self.handle, self.overlapped, False)
            results = win32file.FILE_NOTIFY_INFORMATION(self.buffer, count)
            for action, file in results:
                if action == 4:
                    self.old_name = file
                    continue
                if action >= 1 and action <= 5:
                    self.lock.acquire()
                    posted = file in self.postedActions[action]
                    if not posted:
                        self.postedActions[action].append(file)
                    self.lock.release()
                    if posted:
                        continue
                if isinstance(self.parent,wx.Window):
                    wx.PostEvent(self.parent, FolderChangeEvent(self.id, source=self, action=action, file=file, old_name=self.old_name))

    def rearm(self,action,file):
        self.lock.acquire()
        posted = file in self.postedActions[action]
        if  posted:
            self.postedActions[action].remove(file)
        self.lock.release()
