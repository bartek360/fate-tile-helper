from binary_reader import BinaryReader
import struct
from ctypes import *

def next_mul(val, mul):
    return (val + mul - 1) // mul * mul

# from PPSSPP ge_constants.h
# class GETextureFormat:
GE_TFMT_5650 = 0
GE_TFMT_5551 = 1
GE_TFMT_4444 = 2
GE_TFMT_8888 = 3
GE_TFMT_CLUT4 = 4
GE_TFMT_CLUT8 = 5
GE_TFMT_CLUT16 = 6
GE_TFMT_CLUT32 = 7
GE_TFMT_DXT1 = 8
GE_TFMT_DXT3 = 9
GE_TFMT_DXT5 = 10

# class GEPaletteFormat:
GE_CMODE_16BIT_BGR5650 = 0
GE_CMODE_16BIT_ABGR5551 = 1
GE_CMODE_16BIT_ABGR4444 = 2
GE_CMODE_32BIT_ABGR8888 = 3
    
class TEXFile:
    def __init__(self, path=None):
        self.texData = None
        if path:
            self.load(path)

    def load(self, path):
        print(path)
        with open(path, "rb") as f:
            data = f.read()
        self.from_bytes(data)
    
    def from_bytes(self, data, skip_untiled=False):
        bs = BinaryReader(data)
        if bs.size() < 0xC:
            return
        bs.read_bytes(0xC)
        palOff = bs.pos() + bs.read_int32()
        texType, isSwizzled, pixWidth, pixHeight, unk03, unk04 = \
            struct.unpack("<6H", bs.read_bytes(12))
        bpp = 4 if texType == GE_TFMT_CLUT4 else 8
        if texType not in (GE_TFMT_CLUT4,GE_TFMT_CLUT8):
            raise ValueError("Unsupported texture type", texType)
        texSize = bs.read_int32()
        texOff = bs.pos() + bs.read_int32()
        # bs.seek(texOff, NOESEEK_ABS)
        isTiled = bs.read_int32()
        if skip_untiled and not isTiled:
            return
        bs.read_bytes(0x8)
        texData = bs.read_bytes(texSize)
        # bs.seek(palOff, NOESEEK_ABS)
        palType, palNumColors = struct.unpack("2H", bs.read_bytes(4))
        if palType not in (GE_CMODE_32BIT_ABGR8888, GE_CMODE_16BIT_ABGR5551):
            raise ValueError("Unsupported palette type", palType)
        palSize, Null = struct.unpack("2I", bs.read_bytes(8))
        palStart = bs.pos() + bs.read_int32()
        # bs.seek(palStart, NOESEEK_ABS)
        palData = bytearray(bs.read_bytes(palSize))
        # cluthash fix
        for i in range(0, palSize, 2 * (1+(palType == 3))):
            if palType == 0 and palData[i] | palData[i+1] << 8 == 0x07e0 \
            or palType == 1 and palData[i] | palData[i+1] << 8 == 0x83e0 \
            or palType == 2 and palData[i] | palData[i+1] << 8 == 0xf0f0:
                palData[i],palData[i+1] = 0,0
            elif palType == 3:
                if palData[i] == 0 and palData[i+1] == 0xFF and palData[i+2] == 0:
                    palData[i],palData[i+1] = 0,0
                    palData[i+2],palData[i+3] = 0,0
        if isTiled:
            tileHeader = bs.read_bytes(20)
            self.tileH, self.tileV = struct.unpack_from("2I", tileHeader, 0)
            self.tileNumBlits, self.tileW, self.tileNumUniqueBlits, unkT2 = \
                struct.unpack_from("4H", tileHeader, 8)
            self.tileSize = self.tileW ** 2 // (8 // bpp)
            self.tileLUT = bs.read_bytes(self.tileH * self.tileV * 2)
        self.texType = texType
        self.palType = palType
        self.isTiled = isTiled
        self.texData = texData
        self.palData = palData
        self.bpp = bpp
        return 1

def load_pak(path, data=None):
    file_list = []
    if path is None:
        bs = BinaryReader(data)
    else:
        with open(path, "rb") as f:
            bs = BinaryReader(f.read())
    if bs.size():
        files, flag = struct.unpack("<2H", bs.read_bytes(4))
        size_arr = struct.unpack(files * "I", bs.read_bytes(files * 4))
        bs.seek( next_mul(bs.pos(), 16) )
        if flag & 0x8000: # has filename
            for file_size in (size_arr):
                name = bs.read_str(64)
                data = bs.read_bytes(file_size)
                file_list.append( (name, data) )
        else:
            for i, file_size in enumerate(size_arr):
                data = bs.read_bytes(file_size)
                file_list.append( (f"{i:08x}", data) )
    return file_list

lzss0_dll = None
def init_lzss0():
    global lzss0_dll
    lzss0_dll = CDLL(".\\lzss0.dll")

def load_cmp(path):
    with open(path, "rb") as f:
        bs = BinaryReader(f.read())
        iecp = bs.read_str(4)
        if iecp != "IECP":
            print("Not a Fate/Extra CMP file.")
            return None
        decmp_size = bs.read_int32()
        cmp_data = bs.read_bytes( bs.size() - 8)
        outarr = create_string_buffer(decmp_size)
        lzss0_dll.unlzss(cmp_data, len(cmp_data), outarr, decmp_size)
        return outarr

hash_dll = CDLL(".\\hash.dll")
qt = hash_dll.QuickTexHashNonSSE
qt.restype = c_uint32
class quick:
    def __init__(self, data):
        self.data = bytearray(data)
    def update(self, data):
        self.data.extend(data)
    def intdigest(self):
        return qt(bytes(self.data), len(self.data))
    def hexdigest(self):
        return "%08x" % qt(self.data, len(self.data))
