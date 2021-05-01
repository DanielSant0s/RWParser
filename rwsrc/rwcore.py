from enum import Enum, IntEnum

class ChunkType(Enum):
    NAOBJECT        = 0x0  #do NOT use this.
    STRUCT          = 0x1  #nonymous chunk.
    STRING          = 0x2
    EXTENSION       = 0x3
    CAMERA          = 0x5
    TEXTURE         = 0x6
    MATERIAL        = 0x7
    MATLIST         = 0x8
    ATOMICSECT      = 0x9
    PLANESECT       = 0xA
    WORLD           = 0xB
    SPLINE          = 0xC
    MATRIX          = 0xD
    FRAMELIST       = 0xE
    GEOMETRY        = 0xF
    CLUMP           = 0x10
    LIGHT           = 0x12
    UNICODESTRING   = 0x13
    ATOMIC          = 0x14
    TEXTURENATIVE   = 0x15
    TEXDICTIONARY   = 0x16
    ANIMDATABASE    = 0x17
    IMAGE           = 0x18
    SKINANIMATION   = 0x19
    GEOMETRYLIST    = 0x1A
    ANIMANIMATION   = 0x1B
    HANIMANIMATION  = 0x1B
    TEAM            = 0x1C
    CROWD           = 0x1D
    RIGHTTORENDER   = 0x1F
    MTEFFECTNATIVE  = 0x20
    MTEFFECTDICT    = 0x21
    TEAMDICTIONARY  = 0x22
    PITEXDICTIONARY = 0x23
    TOC             = 0x24
    PRTSTDGLOBALDATA = 0x25
    ALTPIPE         = 0x26
    PIPEDS          = 0x27
    PATCHMESH       = 0x28
    CHUNKGROUPSTART = 0x29
    CHUNKGROUPEND   = 0x2A
    UVANIMDICT      = 0x2B
    COLLTREE        = 0x2C
    ENVIRONMENT     = 0x2D
    COREPLUGINIDMAX = 0x2E
    MORPH           = 0x105
    SKYMIPMAP       = 0x110
    SKIN            = 0x116
    PARTICLES       = 0x118
    HANIM           = 0x11E
    MATERIALEFFECTS = 0x120
    ADCPLG          = 0x134
    BINMESH         = 0x50E
    NATIVEDATA      = 0x510
    VERTEXFORMAT    = 0x510
    SCRIPT          = 0x704
    ASSET           = 0x716
    CONTAINER       = 0x71C
    PIPELINESET      = 0x253F2F3
    SPECULARMAT      = 0x253F2F6
    CHUNK_2DFX       = 0x253F2F8
    NIGHTVERTEXCOLOR = 0x253F2F9
    COLLISIONMODEL   = 0x253F2FA
    REFLECTIONMAT    = 0x253F2FC
    MESHEXTENSION    = 0x253F2FD
    FRAME            = 0x253F2FE

def PackRWVersion(decversion):
    rwversion = ((decversion - 0x30000 & 0x3ff00) << 14) | (decversion & 0x3F) << 16
    rwversion =  rwversion.to_bytes(4, byteorder="little")
    return rwversion

def UnpackRWVersion(rwfile):
    rwversion = rwfile.read(4)
    rwversion = int.from_bytes(rwversion, 'little')
    rwversion = (rwversion >> 14 & 0x3FF00) + 0x30000 | (rwversion >> 16 & 0x3F)
    return rwversion

def GetFileSize(rwfile):
    rwfile.seek(0, 2)
    fileSize = rwfile.tell()
    return fileSize

#Section Parameter functions

def GetSectionType(rwfile):
    rwtype = rwfile.read(4)
    rwtype = int.from_bytes(rwtype, 'little')
    disptype = ChunkType(rwtype)
    disptype = disptype.name
    return disptype

def GetSectionTypeRaw(rwsection):
    typeraw = rwsection.read(4)
    typeraw = int.from_bytes(typeraw, 'little')
    return typeraw

def GetSectionSize(rwsection):
    secSize = rwsection.read(4)
    secSize = int.from_bytes(secSize, 'little')
    return secSize

def GetHeaderSize(rwsection):
    HeaderSize = rwsection.read(4)
    HeaderSize = int.from_bytes(HeaderSize, 'little')
    #HeaderSize += 4
    return HeaderSize

def GetSectionName(rwsection):
    NameSize = rwsection.read(4)
    NameSize = int.from_bytes(NameSize, 'little')
    SectionName = rwsection.read(NameSize)
    return SectionName

def GetUnknownBin(rwsection):
    UnknownBin = rwsection.read(16)
    return UnknownBin

def GetTypeName(rwsection):
    rwIDSize = rwsection.read(4)
    rwIDSize = int.from_bytes(rwIDSize, 'little')
    rwIDName = rwsection.read(rwIDSize)
    return rwIDName

def GetProjectPath(rwsection):
    ProjPathSize = rwsection.read(4)
    ProjPathSize = int.from_bytes(ProjPathSize, 'little')
    ProjectPath = rwsection.read(ProjPathSize)
    return ProjectPath

def GetBuildPath(rwsection):
    BuildPathSize = rwsection.read(4)
    BuildPathSize = int.from_bytes(BuildPathSize, 'little')
    BuildPath = rwsection.read(BuildPathSize)
    return BuildPath

def Skip4Bytes(rwsection):
    #Null Padding
    rwsection.seek(4, 1)
    return rwsection

def GetAssetSize(rwsection):        
    AssetSize = rwsection.read(4)
    AssetSize = int.from_bytes(AssetSize, 'little')
    #AssetSize -= 9
    return AssetSize




