import io
import os
from os.path import join, splitext
import PIL.Image
import PIL.ImageTk

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile

from rwsrc import rwcore

tempname = "temp.tmp"

def InitializeInterface():
    root = tk.Tk()
    root.iconbitmap('ui/rwlogo.ico')
    root.title("RWParser 1.0")
    w = 600
    h = 500
    x = 150
    y = 100

    background = PIL.Image.open("ui/static.png")
    background = background.resize((80, 80), PIL.Image.ANTIALIAS)
    bgobj = PIL.ImageTk.PhotoImage(background)
    bgtest = tk.Label(root, image = bgobj)
    bgtest.image = bgobj
    bgtest.place(relx=0.58, rely=0.43, relwidth=1, relheight=1, anchor=NE)
    
    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    root = DisplayCascadeMenus(root)
    root = CreateSideBar(root)
    return root

def CreateSideBar(root):
    global sidebar
    sidebar = Frame(root)
    
    sidebar.pack(side=RIGHT, anchor=N)
    label = Label(sidebar, text="File Properties", width=22, relief=GROOVE).pack()
    padding = Label(sidebar, text="", width=23).pack(side=BOTTOM)
    return root

def SetFileTitle(file, root):
    filehead = os.path.split(file)
    windowtitle = filehead[1], "-", "RWParser"
    root.title(windowtitle)
    return root

def DisplayCascadeMenus(root):
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff = 0)
    filemenu.add_command(label="New", command = donothing)
    filemenu.add_command(label = "Open", command = lambda: MainApp(root))
    filemenu.add_command(label = "Save", command = donothing)
    filemenu.add_command(label = "Save as...", command = donothing)
    filemenu.add_command(label = "Close", command = donothing)
    filemenu.add_separator()
    filemenu.add_command(label = "Exit", command = root.quit)
    menubar.add_cascade(label = "File", menu = filemenu)

    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label = "Undo", command = donothing)
    editmenu.add_separator()
    editmenu.add_command(label = "Cut", command = donothing)
    editmenu.add_command(label = "Copy", command = donothing)
    editmenu.add_command(label = "Paste", command = donothing)
    editmenu.add_command(label = "Delete", command = donothing)
    editmenu.add_command(label = "Select All", command = donothing)
    menubar.add_cascade(label = "Edit", menu = editmenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label = "Help Index", command = donothing)
    helpmenu.add_command(label = "About...", command = lambda: aboutrwparser(root))
    menubar.add_cascade(label = "Help", menu = helpmenu)
    root.config(menu = menubar)
    return root

def DisplayRWVersion(version):
    version = hex(version)[2:]
    def split(version):
        return [char for char in version]
    rwver = '.'.join(split(version))
    dispver = "Version:", rwver
    return dispver

def donothing(root):
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def aboutrwparser(root):
    filewin = Toplevel(root)
    filewin.iconbitmap('ui/rwlogo.ico')
    filewin.title("About RWParser")
    w = 350
    h = 150
    x = 150
    y = 100
    filewin.geometry("%dx%d+%d+%d" % (w, h, x, y))

    rwparserbuild = Label(filewin, text="RWParser 1.0", pady=12)
    rwparserbuild.config(font=("Segoe UI", 15))
    rwparserbuild.pack(anchor="n")

    description = Label(filewin, text="A multi-proposal modding tool for Renderware games.")
    description.config(font=("Segoe UI", 10))
    description.pack(anchor="n")

    rwparsercredits = Label(filewin, text="Created by Daniel Santos", pady=15)
    rwparsercredits.config(font=("Segoe UI", 8))
    rwparsercredits.pack(side=BOTTOM)
   
def openfile():
    rwfile = askopenfilename(title='Open a Renderware file...')
    return rwfile      

def ExportSection(file):
    CurSection = seclist.get(seclist.curselection())
    with io.open(file, mode="rb") as rwfile:
        rwfile.seek(CurSection[1], 0)
        SectionType = rwcore.GetSectionType(rwfile)
        SectionSize = rwcore.GetSectionSize(rwfile)
        RWVersion = rwcore.UnpackRWVersion(rwfile)
        HeaderSize = rwcore.GetHeaderSize(rwfile)
        rwfile.seek(HeaderSize, 1)
        AssetSize = rwcore.GetAssetSize(rwfile)
        sec = rwfile.read(AssetSize)
    secdata = asksaveasfile(mode='wb', initialfile=CurSection[0])
    secdata.write(sec)
    secdata.close

def ImportSection(file):
    CurSection = seclist.get(seclist.curselection())
    rwasset = openfile()
    with io.open(rwasset, mode="rb") as rwfile:
        FileSize = rwcore.GetFileSize(rwfile)
        rwfile.seek(0, 0)
        ImportedFile = rwfile.read(FileSize)
    with io.open(file, mode="rb") as container:
        ContSize = rwcore.GetFileSize(container)
        container.seek(0, 0)
        BeforeFile = container.read(CurSection[1])
        SectionType = rwcore.GetSectionTypeRaw(container)
        SectionSize = rwcore.GetSectionSize(container)
        RWVersion = rwcore.UnpackRWVersion(container)
        HeaderSize = rwcore.GetHeaderSize(container)
        HeaderContent = container.read(HeaderSize)
        AssetSize = rwcore.GetAssetSize(container)
        container.seek(AssetSize, 1)
        AfterPos = container.tell()
        ContSize = AfterPos - ContSize
        ContSize = abs(ContSize)
        AfterInsert = container.read(ContSize)
    with io.open(file, mode="wb") as target:
        target.truncate()
        SectionType = SectionType.to_bytes(4, byteorder="little")
        ImportLen = 4 + HeaderSize + 4 + FileSize
        print(hex(ImportLen))
        ImportLen = ImportLen.to_bytes(4, byteorder="little")
        RWVersion = rwcore.PackRWVersion(RWVersion)
        HeaderSize = HeaderSize.to_bytes(4, byteorder="little")
        FileSize = FileSize.to_bytes(4, byteorder="little")
        Content = BeforeFile + SectionType + ImportLen + RWVersion + HeaderSize + HeaderContent + FileSize + ImportedFile + AfterInsert
        target.write(Content)

def CreateProperties():
    padding = Label(sidebar, text="", width=23).pack()
    secprops = Label(sidebar, text="Section Properties", width=22, relief=GROOVE).pack()

    global secoffsetvar
    secoffsetvar = StringVar()
    displaysecsize = Label(sidebar, textvariable=secoffsetvar, padx=12)
    displaysecsize.config(font=("Segoe UI", 9))
    displaysecsize.pack(anchor="w")
    secoffsetvar.set("Offset:")

    global secsizevar
    secsizevar = StringVar()
    displaysecsize = Label(sidebar, textvariable=secsizevar, padx=12)
    displaysecsize.config(font=("Segoe UI", 9))
    displaysecsize.pack(anchor="w")
    secsizevar.set("Size:")

def GetSectionProperties():
    CreateProperties()
    
    def GetProperties(event):
        CurSection = seclist.get(seclist.curselection())
        
        sectionoffset = "Offset:", hex(CurSection[1])
        secoffsetvar.set(sectionoffset)
        
        sectionsize = "Size:", CurSection[2], "bytes"
        secsizevar.set(sectionsize)
        
    seclist.bind('<Button-1>', GetProperties)
    seclist.pack()

def OpenChildSections(file, root):
    def GetSection(event):
        ProcessRWSection(file, root)
    seclist.bind('<Double-1>', GetSection)
    seclist.pack()

def DisplayItemType(sectionlist, filelist):
    sectionlist.pack(expand=YES)
    sectionlist.insert(END, filelist)
    global seclist
    seclist = sectionlist
    return sectionlist

def ProcessRWSection(file, root):
    childbox = Toplevel(root)
    global childlist

    try:
        CurSection = seclist.get(seclist.curselection())
    except:
        print("Child list")
    try:
        CurSection = childlist.get(childlist.curselection())
    except:
        print("Parent list")

    scrollbar, childlist = CreateScrollbar(childbox)
    childbox.iconbitmap('ui/rwlogo.ico')
    childbox.title("Child Section View")
    w = 350
    h = 350
    x = 150
    y = 100
    childbox.geometry("%dx%d+%d+%d" % (w, h, x, y))

    with io.open(file, mode="rb") as rwfile:
        rwfile.seek(CurSection[1], 0)
        rwchunk = rwfile.read(CurSection[2])

    with io.open(tempname, mode="wb") as rwchild:
        rwchild.truncate()
        rwchild.write(rwchunk)

    with io.open(tempname, mode="rb") as rwchild:
        fileSize = rwcore.GetFileSize(rwchild)
        rwchild.seek(0, 0)
        disprwtype = rwcore.GetSectionType(rwchild)
        rwchild.seek(8, 0)
        version = rwcore.UnpackRWVersion(rwchild)
        SectionIndex = 0
        filePos = 0
        child = []
        while filePos < fileSize:
            filePos = rwchild.tell()
            disptype = rwcore.GetSectionType(rwchild)
            assetSize = rwcore.GetSectionSize(rwchild)
            rwversion = rwcore.UnpackRWVersion(rwchild)
            disptype = DisplayAssetNames(disptype, rwchild)
            chunk = rwchild.read(assetSize)
            child.append([disptype, filePos, assetSize, rwversion])
            childlist.pack(expand=YES)
            childlist.insert(END, child[SectionIndex])

            SectionIndex += 1
    RightClickMenu(childbox, childlist, tempname)
    scrollbar, childlist = CloseScrollbar(scrollbar, childlist)

def RightClickMenu(root, screenspace, rwfile):
    m = Menu(root, tearoff=0)
    m.add_command(label="Scan Child Sections", command= lambda: ProcessRWSection(rwfile, root))
    m.add_command(label="Export Section", command= lambda: ExportSection(rwfile))
    m.add_command(label="Import Section", command= lambda: ImportSection(rwfile))
    m.add_command(label="Edit Section")
    m.add_separator()
    m.add_command(label="Properties")
    def do_popup(event):
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()
    screenspace.bind("<Button-3>", do_popup)

def CreateScrollbar(root):
    scrollbar = Scrollbar(root)
    scrollbar.pack( side = RIGHT, fill = Y )
    sectionlist = Listbox(root, yscrollcommand = scrollbar.set )
    return scrollbar, sectionlist

def CloseScrollbar(scrollbar, sectionlist):
    sectionlist.pack(fill=BOTH)
    scrollbar.config( command = sectionlist.yview )
    return scrollbar, sectionlist

def GetWindowSize(root):
    root.update()
    width = root.winfo_width()
    height = root.winfo_height()
    return width, height

def ResetAppView(sectionlist, scrollbar, disprwtype, disprwver):
    print("Resetting interface")
    sectionlist.destroy()
    scrollbar.destroy()
    disprwtype.destroy()
    disprwver.destroy()

def UpdateInterface(root):
    root.mainloop()

def DisplayAssetNames(disptype, rwfile):
    if disptype == 'ASSET':
        rwfile.seek(4, 1)
        assetnamesize = rwfile.read(4)
        assetnamesize = int.from_bytes(assetnamesize, 'little')
        assetname = rwfile.read(assetnamesize)
        assetname = assetname.rstrip(b'\xBF')
        assetnamesize = ((-assetnamesize) - 8)
        rwfile.seek(assetnamesize, 1)
        assetname = assetname.decode('utf-8')
        assetname = ''.join(x for x in assetname if x.isprintable())
        disptype = assetname
    return disptype

def DisplayFileProperties(disprwtype, fileSize, version, SectionIndex):
    disprwtype = "Type:", disprwtype
    displayfiletype = Label(sidebar, text=disprwtype, padx=12)
    displayfiletype.config(font=("Segoe UI", 9))
    displayfiletype.pack(anchor="w")

    dispfilesize = "Size:", fileSize, "bytes"
    displayfilesize = Label(sidebar, text=dispfilesize, padx=12)
    displayfilesize.config(font=("Segoe UI", 9))
    displayfilesize.pack(anchor="w")

    disprwver = DisplayRWVersion(version)
    displayrwversion = Label(sidebar, text=disprwver, padx=12)
    displayrwversion.config(font=("Segoe UI", 9))
    displayrwversion.pack(anchor="w")
    
    SectionsQuantity = SectionIndex, "Parent", "sections"
    displaysectionsnumber = Label(sidebar, text=SectionsQuantity, padx=12)
    displaysectionsnumber.config(font=("Segoe UI", 9))
    displaysectionsnumber.pack(anchor="w")

root = InitializeInterface()

def MainApp(root):
    scrollbar, sectionlist = CreateScrollbar(root)
    file = openfile()
    _, ext = splitext(file)
    with io.open(file, mode="rb") as rwfile:
        width, height = GetWindowSize(root)
        fileSize = rwcore.GetFileSize(rwfile)
        rwfile.seek(0, 0)
        disprwtype = rwcore.GetSectionType(rwfile)
        rwfile.seek(8, 0)
        version = rwcore.UnpackRWVersion(rwfile)
        filelist = []
        if disprwtype == 'CONTAINER':
            rwfile.seek(0, 0)
        SectionIndex = 0
        filePos = 0
        while filePos < fileSize:
            filePos = rwfile.tell()
            disptype = rwcore.GetSectionType(rwfile)
            assetSize = rwcore.GetSectionSize(rwfile)
            rwversion = rwcore.UnpackRWVersion(rwfile)
            disptype = DisplayAssetNames(disptype, rwfile)
            chunk = rwfile.read(assetSize)
            filelist.append([disptype, filePos, assetSize, rwversion])
            dispchunk = DisplayItemType(sectionlist, filelist[SectionIndex])
            SectionIndex += 1
    DisplayFileProperties(disprwtype, fileSize, version, SectionIndex)
    root = SetFileTitle(file, root)
    scrollbar, sectionlist = CloseScrollbar(scrollbar, sectionlist)
    RightClickMenu(root, sectionlist, file)
    OpenChildSections(file, root)
    GetSectionProperties()

UpdateInterface(root)

