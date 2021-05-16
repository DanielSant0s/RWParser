import io
import os
from os.path import join, splitext
import PIL.Image
import PIL.ImageTk

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfile

from rwsrc import rwcore

tempname = "temp.tmp"

def MainApp(self):
    try:
        if not self.parenttree == None:
            interface.ResetAppView(self)
    except Exception:
        pass
    file = interface.openfile()
    filename, ext = splitext(file)
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    self.parenttree = ttk.Treeview(self)
    self.parenttree.heading("#0", text=file)
    with io.open(file, mode="rb") as rwfile:
        width, height = interface.GetWindowSize(self)
        fileSize = rwcore.GetFileSize(rwfile)
        rwfile.seek(0, 0)
        disprwtype = rwcore.GetSectionType(rwfile)
        rwfile.seek(8, 0)
        version = rwcore.UnpackRWVersion(rwfile)
        self.filelist = []
        displaylist = []
        #if disprwtype == 'CONTAINER':
        rwfile.seek(0, 0)
        self.SectionIndex = 0
        filePos = 0
        while filePos < fileSize:
            filePos = rwfile.tell()
            disptype = rwcore.GetSectionType(rwfile)
            assetSize = rwcore.GetSectionSize(rwfile)
            rwversion = rwcore.UnpackRWVersion(rwfile)
            disptype = interface.DisplayAssetNames(disptype, rwfile)
            chunk = rwfile.read(assetSize)
            self.filelist.append([disptype, filePos, assetSize, rwversion])
            displaylist.append([disptype, "-", "Offset:", hex(filePos), "|", "Size:", assetSize, "bytes"])
            self.parenttree.insert('', END, text=displaylist[self.SectionIndex], iid=self.SectionIndex, open=False)
            self.SectionIndex += 1

        if not disprwtype == 'CONTAINER':
            self.ParentCount = 0
            self.ImSecIndex = self.SectionIndex
            while self.ParentCount < self.SectionIndex:
                try:
                    interface.ProcessRWSection(self, rwfile)
                except Exception:
                    pass
                self.ParentCount += 1
            while self.ParentCount < self.ImSecIndex:
                try:
                    interface.ProcessRWSection(self, rwfile)
                except Exception:
                    pass
                self.ParentCount += 1

    self.parenttree.grid(row=0, column=0, sticky='nsew')
    interface.DisplayFileProperties(self, disprwtype, fileSize, version, self.SectionIndex)
    interface.SetFileTitle(self, file)
    interface.RightClickMenu(self, self.parenttree, file)
    interface.GetSectionProperties(self)
    
class interface():
    def __init__(self):
        self.root = Tk()
        root = self.root
        root.iconbitmap('ui/rwlogo.ico')
        root.title("RWParser 1.0")
        w = 600
        h = 500
        x = 150
        y = 100

        background = PIL.Image.open("ui/static.png")
        background = background.resize((80, 80), PIL.Image.ANTIALIAS)
        bgobj = PIL.ImageTk.PhotoImage(background)
        bgtest = Label(root, image = bgobj)
        bgtest.image = bgobj
        bgtest.place(relx=0.58, rely=0.43, relwidth=1, relheight=1, anchor=NE)
        
        root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        interface.DisplayCascadeMenus(root)
        interface.CreateSideBar(root)
        root.mainloop()

    def CreateSideBar(self):
        self.sidebar = Frame(self)
        self.sidebar.rowconfigure(0, weight=1)
        self.sidebar.columnconfigure(1, weight=1)
        self.sidebar.grid(row=0, column=1, sticky='n')
        label = Label(self.sidebar, text="File Properties", width=22, relief=GROOVE).grid(row=0, column=0, sticky='n')
        padding = Label(self.sidebar, text="", width=23).grid(sticky='s')

    def SetFileTitle(self, file):
        filehead = os.path.split(file)
        windowtitle = filehead[1], "-", "RWParser"
        self.title(windowtitle)

    def DisplayCascadeMenus(self):
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff = 0)
        filemenu.add_command(label="New", command = interface.donothing)
        filemenu.add_command(label = "Open", command = lambda: MainApp(self))
        filemenu.add_command(label = "Save", command = interface.donothing)
        filemenu.add_command(label = "Save as...", command = interface.donothing)
        filemenu.add_command(label = "Close", command = lambda: interface.ResetAppView(self))
        filemenu.add_separator()
        filemenu.add_command(label = "Exit", command = self.quit)
        menubar.add_cascade(label = "File", menu = filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label = "Undo", command = interface.donothing)
        editmenu.add_separator()
        editmenu.add_command(label = "Cut", command = interface.donothing)
        editmenu.add_command(label = "Copy", command = interface.donothing)
        editmenu.add_command(label = "Paste", command = interface.donothing)
        editmenu.add_command(label = "Delete", command = interface.donothing)
        editmenu.add_command(label = "Select All", command = interface.donothing)
        menubar.add_cascade(label = "Edit", menu = editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label = "Help Index", command = interface.donothing)
        helpmenu.add_command(label = "About...", command = lambda: interface.aboutrwparser(self))
        menubar.add_cascade(label = "Help", menu = helpmenu)
        self.config(menu = menubar)

    def DisplayRWVersion(version):
        version = hex(version)[2:]
        def split(version):
            return [char for char in version]
        rwver = '.'.join(split(version))
        dispver = "Version:", rwver
        return dispver

    def donothing(self):
        filewin = Toplevel(self)
        button = Button(filewin, text="Do nothing button")
        button.pack()

    def aboutrwparser(self):
        filewin = Toplevel(self)
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

    def ExportSection(self, file, sectree):
        selectedSection = sectree.selection()
        section = self.filelist[int(selectedSection[0])]
        with io.open(file, mode="rb") as rwfile:
            rwfile.seek(section[1], 0)
            SectionType = rwcore.GetSectionType(rwfile)
            SectionSize = rwcore.GetSectionSize(rwfile)
            RWVersion = rwcore.UnpackRWVersion(rwfile)
            if SectionType == 'ASSET':
                HeaderSize = rwcore.GetHeaderSize(rwfile)
                rwfile.seek(HeaderSize, 1)
                AssetSize = rwcore.GetAssetSize(rwfile)
            else:
                AssetSize = SectionSize
            sec = rwfile.read(AssetSize)
        secdata = asksaveasfile(mode='wb', initialfile=section[0])
        secdata.write(sec)
        secdata.close()

    def ImportSection(self, file, sectree):
        selectedSection = sectree.selection()
        section = self.filelist[int(selectedSection[0])]
        rwasset = openfile()
        with io.open(rwasset, mode="rb") as rwfile:
            FileSize = rwcore.GetFileSize(rwfile)
            rwfile.seek(0, 0)
            ImportedFile = rwfile.read(FileSize)
        with io.open(file, mode="rb") as container:
            ContSize = rwcore.GetFileSize(container)
            container.seek(0, 0)
            BeforeFile = container.read(section[1])
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

    def CreateProperties(self):
        padding = Label(self.sidebar, text="", width=23).grid(row=5, column=0, sticky='n')
        secprops = Label(self.sidebar, text="Section Properties", width=22, relief=GROOVE).grid(row=6, column=0, sticky='n')

        self.secoffsetvar = StringVar()
        displaysecsize = Label(self.sidebar, textvariable=self.secoffsetvar, padx=12)
        displaysecsize.config(font=("Segoe UI", 9))
        displaysecsize.grid(row=7, column=0, sticky='n')
        self.secoffsetvar.set("Offset:")

        self.secsizevar = StringVar()
        displaysecsize = Label(self.sidebar, textvariable=self.secsizevar, padx=12)
        displaysecsize.config(font=("Segoe UI", 9))
        displaysecsize.grid(row=8, column=0, sticky='n')
        self.secsizevar.set("Size:")

        self.rwversionvar = StringVar()
        displayrwver = Label(self.sidebar, textvariable=self.rwversionvar, padx=12)
        displayrwver.config(font=("Segoe UI", 9))
        displayrwver.grid(row=9, column=0, sticky='n')
        self.rwversionvar.set("Version:")

    def GetSectionProperties(self):
        interface.CreateProperties(self)
        
        def GetProperties(event):
            selectedSection = self.parenttree.selection()
            section = self.filelist[int(selectedSection[0])]
            
            sectionoffset = "Offset:", hex(section[1])
            self.secoffsetvar.set(sectionoffset)
            
            sectionsize = "Size:", section[2], "bytes"
            self.secsizevar.set(sectionsize)

            rwverdisp = interface.DisplayRWVersion(section[3])
            self.rwversionvar.set(rwverdisp)
            
        self.parenttree.bind('<<TreeviewSelect>>', GetProperties)
        self.parenttree.grid()

    def RightClickMenu(self, screenspace, rwfile):
        m = Menu(self, tearoff=0)
        m.add_command(label="Export Section", command= lambda: interface.ExportSection(self, rwfile, screenspace))
        m.add_command(label="Import Section", command= lambda: interface.ImportSection(self, rwfile, screenspace))
        m.add_command(label="Edit Section")
        m.add_separator()
        m.add_command(label="Properties")
        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()
        screenspace.bind("<Button-3>", do_popup)

    def GetWindowSize(self):
        self.update()
        width = self.winfo_width()
        height = self.winfo_height()
        return width, height

    def ResetAppView(self):
        print("Resetting interface")
        self.parenttree.destroy()
        self.sidebar.destroy()
        interface.CreateSideBar(self)

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

    def DisplayFileProperties(self, disprwtype, fileSize, version, SectionIndex):
        disprwtype = "Type:", disprwtype
        displayfiletype = Label(self.sidebar, text=disprwtype, padx=12)
        displayfiletype.config(font=("Segoe UI", 9))
        displayfiletype.grid(row=1, column=0, sticky='n')

        dispfilesize = "Size:", fileSize, "bytes"
        displayfilesize = Label(self.sidebar, text=dispfilesize, padx=12)
        displayfilesize.config(font=("Segoe UI", 9))
        displayfilesize.grid(row=2, column=0, sticky='n')

        disprwver = interface.DisplayRWVersion(version)
        displayrwversion = Label(self.sidebar, text=disprwver, padx=12)
        displayrwversion.config(font=("Segoe UI", 9))
        displayrwversion.grid(row=3, column=0, sticky='n')

        SectionsQuantity = SectionIndex, "Parent", "sections"
        displaysectionsnumber = Label(self.sidebar, text=SectionsQuantity, padx=12)
        displaysectionsnumber.config(font=("Segoe UI", 9))
        displaysectionsnumber.grid(row=4, column=0, sticky='n')

    def ProcessRWSection(self, rwfile):
        section = self.filelist[self.ParentCount]
        rwfile.seek(section[1], 0)
        rwchunk = rwfile.read(section[2])

        with io.open(tempname, mode="wb") as rwchild:
            rwchild.truncate()
            rwchild.write(rwchunk)
        with io.open(tempname, mode="rb") as rwchild:
            fileSize = rwcore.GetFileSize(rwchild)
            rwchild.seek(12, 0)
            ChildIndex = 0
            filePos = 0
            childlist = []
            while filePos < fileSize:
                filePos = rwchild.tell() + section[1]
                print("Child Offset:", hex(filePos))
                disptype = rwcore.GetSectionType(rwchild)
                assetSize = rwcore.GetSectionSize(rwchild)
                if assetSize > section[2]:
                    raise Exception("Child section size is bigger than parent")
                rwversion = rwcore.UnpackRWVersion(rwchild)
                if rwversion != section[3]:
                    raise Exception("Child section version difer from parent")
                disptype = interface.DisplayAssetNames(disptype, rwchild)
                chunk = rwchild.read(assetSize)
                if rwversion > 0:
                    self.filelist.append([disptype, filePos, assetSize, rwversion])
                    childlist.append([disptype, "-", "Offset:", hex(filePos), "|", "Size:", assetSize, "bytes"])
                    self.parenttree.insert('', END, text=childlist[ChildIndex], iid=self.ImSecIndex, open=False)
                    self.parenttree.move(self.ImSecIndex, self.ParentCount, ChildIndex)
                    self.ImSecIndex += 1
                    ChildIndex += 1

self = interface()





