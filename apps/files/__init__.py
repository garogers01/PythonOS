import pyos
from shutil import move, copy2

application = None
state = None

location = str(pyos.__file__).rstrip("pyos.py").rstrip("pyos.pyc")

pathIndicator = None
fileOpeners = {}
selected = []

pathText = None
container = None

def setLocation(loc):
    global location
    if pyos.os.path.exists(loc):
        location = loc
    
def loadFileOpeners():
    global fileOpeners
    fileOpeners = {}
    for app in state.getApplicationList().applications:
        if "file" in app.parameters:
            fileOpeners[app] = {
                                  "method": app.parameters["file"]["method"],
                                  "supported": app.parameters["file"]["supportedFileTypes"]
                                  }
            
def getAppsForFileType(ftype):
    apps = []
    for app in fileOpeners.keys():
        if ftype in fileOpeners[app]["supported"]:
            apps.append(app)
    return apps

def goToPath():
    dialog = pyos.GUI.AskDialog("Location", "Enter the path of the location you want to navigate to.", loadLocation)
    dialog.display()
    
def passSelectedDir(to):
    to(location)
    
class Operations:
    @staticmethod
    def delete():
        global selected
        for path in selected:
            if pyos.os.path.isfile(path):
                pyos.os.remove(path)
            if pyos.os.path.isdir(path):
                pyos.rmtree(path, True)
            selected.remove(path)
    
    @staticmethod            
    def move():
        global selected
        for path in selected:
            if path.rstrip("\\")[:path.rstrip("\\").rfind("\\")] == location.rstrip("\\"): continue
            move(path.rstrip("\\")[:path.rstrip("\\").rfind("\\")], location)
            selected.remove(path)
            
    @staticmethod
    def copy():
        global selected
        for path in selected:
            if path.rstrip("\\")[:path.rstrip("\\").rfind("\\")] == location.rstrip("\\"): continue
            copy2(path.rstrip("\\")[:path.rstrip("\\").rfind("\\")], location)
            selected.remove(path)
            
def loadLocation(loc):
    setLocation(loc)
    load()
    
def up():
    loadLocation(location.rstrip("\\")[:location.rstrip("\\").rfind("\\")+1])

def getDefaultButtonBar():
    buttonBar = pyos.GUI.ButtonRow((0, 0), width=application.ui.width, height=40, color=state.getColorPalette().getColor("background"), padding=0, margin=0,
                                   border=1, borderColor=state.getColorPalette().getColor("accent"))
    button_home = pyos.GUI.Image((0,0), path="res/icons/files_home.png", width=40, height=40,
                                 onClick=loadLocation, onClickData=(str(pyos.__file__).rstrip("pyos.py").rstrip("pyos.pyc"),))
    button_up = pyos.GUI.Image((0,0), path="res/icons/files_up.png", width=40, height=40,
                                 onClick=up)
    button_goto = pyos.GUI.Image((0,0), path="res/icons/files_goto.png", width=40, height=40,
                                 onClick=goToPath)
    button_delete = pyos.GUI.Image((0,0), path="res/icons/files_delete.png", width=40, height=40,
                                 onClick=Operations.delete)
    button_move = pyos.GUI.Image((0,0), path="res/icons/files_move.png", width=40, height=40,
                                 onClick=Operations.move)
    button_copy = pyos.GUI.Image((0,0), path="res/icons/files_copy.png", width=40, height=40,
                                 onClick=Operations.copy)
    buttonBar.addChild(button_home)
    buttonBar.addChild(button_up)
    buttonBar.addChild(button_goto)
    buttonBar.addChild(button_delete)
    buttonBar.addChild(button_move)
    buttonBar.addChild(button_copy)
    return buttonBar

def getSelectButtonBar(passTo):
    buttonBar = pyos.GUI.ButtonRow((0, 0), width=application.ui.width, height=40, color=state.getColorPalette().getColor("background"), padding=0, margin=0,
                                   border=1, borderColor=state.getColorPalette().getColor("accent"))
    button_select = pyos.GUI.Image((0,0), path="res/icons/files_select.png", width=40, height=40,
                                 onClick=passSelectedDir, onClickData=(passTo,))
    button_home = pyos.GUI.Image((0,0), path="res/icons/files_home.png", width=40, height=40,
                                 onClick=loadLocation, onClickData=(str(pyos.__file__).rstrip("pyos.py").rstrip("pyos.pyc"),))
    button_up = pyos.GUI.Image((0,0), path="res/icons/files_up.png", width=40, height=40,
                                 onClick=up)
    button_goto = pyos.GUI.Image((0,0), path="res/icons/files_goto.png", width=40, height=40,
                                 onClick=goToPath)
    buttonBar.addChild(button_select)
    buttonBar.addChild(button_home)
    buttonBar.addChild(button_up)
    buttonBar.addChild(button_goto)
    return buttonBar

def select(cont, path):
    selected.append(path)
    cont.backgroundColor = state.getColorPalette().getColor("accent")

def deselect(cont, path):
    selected.remove(path)
    if cont != None:
        cont.backgroundColor = state.getColorPalette().getColor("background")
        
def toggleSelect(cont, path):
    if cont.backgroundColor == state.getColorPalette().getColor("accent"):
        deselect(cont, path)
    else:
        select(cont, path)
        
def openFile(path):
    if pyos.os.path.isdir(path):
        loadLocation(path)
    else:
        print "Is a file"

def getFileEntry(path):
    name = path.rstrip("\\")[path.rstrip("\\").rfind("\\")+1:]
    cont = pyos.GUI.Container((0,0), width=application.ui.width, height=30, color=state.getColorPalette().getColor("background"), fullPath=path)
    icon = None
    if pyos.os.path.isfile(path):
        icon = pyos.GUI.Image((0,0), path="res/icons/file.png", width=30, height=30,
                              onClick=toggleSelect, onClickData=(cont, path))
    else:
        icon = pyos.GUI.Image((0,0), path="res/icons/folder.png", width=30, height=30,
                          onClick=toggleSelect, onClickData=(cont, path))
    text = pyos.GUI.Text((35, 7), name, state.getColorPalette().getColor("item"), 15,
                         onClick=openFile, onClickData=(path,))
    sizeText = "-"
    try:
        sizeText = str(pyos.os.path.getsize(path) / 1000)+"kb"
    except:
        pass
    size = pyos.GUI.Text((application.ui.width-35, 7), sizeText, state.getColorPalette().getColor("item"), 15)
    cont.addChild(icon)
    cont.addChild(text)
    cont.addChild(size)
    return cont

def load():
    pathText.text = location
    pathText.refresh()
    try:
        container.clearChildren()
    except: pass
    for loc in pyos.os.listdir(location):
        container.addChild(getFileEntry(pyos.os.path.join(location, loc)))
    container.goToPage()
    container.refresh()

def onStart(s, a):
    global application, state, container, pathText
    application = a
    state = s
    container = pyos.GUI.ListPagedContainer((0,50), width=application.ui.width, height=application.ui.height-50)
    pathText = pyos.GUI.Text((0, 40), location, state.getColorPalette().getColor("item"), 10, width=application.ui.width)
    bar = getDefaultButtonBar()
    application.ui.addChild(bar)
    application.ui.addChild(pathText)
    application.ui.addChild(container)
    load()