g_app = None

def wxGetApp():
    return g_app

def wxSetApp(app):
    global g_app
    g_app = app
