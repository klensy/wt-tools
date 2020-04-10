from construct import Struct, Int32ul, Int16ul, Int8ul, Nibble, Const, FlagsEnum, EmbeddedBitStruct,\
    IfThenElse, this, Bytes, String


'''
typedef enum FLG_CONTIGUOUS_MIP {
    FLG_7ZIP = 0x40000000,
    FLG_ADDRU_MASK = 0xf,
    FLG_ADDRV_MASK = 0xf0,
    FLG_ARRTEX = 0x200000,
    FLG_COMPR_MASK = 0xe0000000,
    FLG_CONTIGUOUS_MIP = 0x100,
    FLG_CUBTEX = 0x800,
    FLG_GAMMA_EQ_1 = 0x8000,
    FLG_GENMIP_BOX = 0x2000,
    FLG_GENMIP_KAIZER = 0x4000,
    FLG_GLES3_TC_FMT = 0x100000,
    FLG_HASBORDER = 0x400,
    FLG_HOLD_SYSMEM_COPY = 0x10000,
    FLG_HQ_PART = 0x80000,
    FLG_NEED_PAIRED_BASETEX = 0x20000,
    FLG_NONPACKED = 0x200,
    FLG_OODLE = 0x60000000,
    FLG_REV_MIP_ORDER = 0x40000,
    FLG_VOLTEX = 0x1000,
    FLG_ZLIB = 0x80000000,
    FLG_ZSTD = 0x20000000
} FLG_CONTIGUOUS_MIP;
'''
ddsx_flags_enum = FlagsEnum(
    Int32ul,
    FLG_7ZIP=0x40000000,
    FLG_ADDRU_MASK=0xf,
    FLG_ADDRV_MASK=0xf0,
    FLG_ARRTEX=0x200000,
    FLG_COMPR_MASK=0xe0000000,
    FLG_CONTIGUOUS_MIP=0x100,
    FLG_CUBTEX=0x800,
    FLG_GAMMA_EQ_1=0x8000,
    FLG_GENMIP_BOX=0x2000,
    FLG_GENMIP_KAIZER=0x4000,
    FLG_GLES3_TC_FMT=0x100000,
    FLG_HASBORDER=0x400,
    FLG_HOLD_SYSMEM_COPY=0x10000,
    FLG_HQ_PART=0x80000,
    FLG_NEED_PAIRED_BASETEX=0x20000,
    FLG_NONPACKED=0x200,
    FLG_OODLE=0x60000000,
    FLG_REV_MIP_ORDER=0x40000,
    FLG_VOLTEX=0x1000,
    FLG_ZLIB=0x80000000,
    FLG_ZSTD=0x20000000
)

'''
struct Header {
    uint label;
    uint d3dFormat;
    uint flags;
    ushort w;
    ushort h;
    uchar levels;
    uchar hqPartLevels;
    ushort depth;
    ushort bitsPerPixel;
    uchar lQmip:4;
    uchar mQmip:4;
    uchar dxtShift:4;
    uchar uQmip:4;
    uint memSz;
    uint packedSz;
};
'''
ddsx_header = Struct(
    "label" / Const(b"DDSx"),
    "d3dFormat" / String(4),
    # there error in parsing flags, fixed somewhere on future of construct, but not on 2.9.24
    "flags" / ddsx_flags_enum,
    "w" / Int16ul,
    "h" / Int16ul,
    "levels" / Int8ul,
    "hqPartLevels" / Int8ul,
    "depth" / Int16ul,
    "bitsPerPixel" / Int16ul,
    EmbeddedBitStruct(
        "lQmip" / Nibble,
        "mQmip" / Nibble,
        "dxtShift" / Nibble,
        "uQmip" / Nibble,
    ),
    "memSz" / Int32ul,
    "packedSz" / Int32ul,
)

ddsx = Struct(
    "header" / ddsx_header,
    "body" / IfThenElse(
        this.header.packedSz != 0,
        Bytes(this.header.packedSz),
        Bytes(this.header.memSz)
    )
)
