import zlib
import struct
from construct import *

point_f_3d = Struct(
    "x" / Float32l,
    "y" / Float32l,
    "z" / Float32l,
)

# with some text and points
subnode_0x000d = Struct(
    # "field_0" / Enum(Int16ub,
    #                  val_0x0d=0x0d),
    # 0x000d index in file, should be 1,2,3...
    "subnode_000d_index" / Byte,
    # word length?
    # "field_2" / Enum(Byte,
    #                  val_0x0b=0x0b),
    "field_2" / PascalString(Byte),
    "field_3" / PascalString(Byte),
    "point_1" / point_f_3d,
    "point_2" / point_f_3d,
    "point_3" / point_f_3d,
    "point_4" / point_f_3d,
    "magic_2" / Const(b"\x80"),
    "magic_3" / Enum(Int16ub,
                     val_x41x15=0x4115,
                     val_x40x5e=0x405e,
                     val_x40x62=0x4062,
                     val_x40x61=0x4061,
                     val_x40x5c=0x405c,
                     val_x40x60=0x4060,
                     val_x40x65=0x4065,
                     val_x44xa7=0x44a7),
    "magic_4" / Const(b"\x0b\x02")
)

# with some text and points
subnode_0x0000 = Struct(
    # "field_0" / Enum(Int16ub,
    #                  val_0x00=0x00),
    "field_1" / Byte[233],
    "field_2" / Byte[35],
    "magic_2" / Const(b"\x00\x40\x5b\x0b\x02")
)

some_struct = "some_s" / Struct(
    "magic" / Const(b"\x58\x39\xd0\x01"),
    "field_0" / Enum(Int16ub,
                     val_0x0d=0x0d,
                     val_0x00=0x00),
    Probe(),
    Switch(this.field_0,
           # duplicate, i know
           {"val_0x0d": subnode_0x000d,
            "val_0x00": subnode_0x0000})
)

wrapper_chunk = Struct(
    # "chunk_size" / Int16ub,
    "chunk_params" / BitStruct(
        # is length field 1 or 2 bytes
        "is_one_byte" / Flag,
        "unknown" / Flag,
        "chunk_size" / IfThenElse(
            this.is_one_byte,
            BitsInteger(6),
            BitsInteger(14))
    ),
    "chunk_size" / Computed(this.chunk_params.chunk_size),
    Probe(),
    "chunk_data" / Byte[this.chunk_size]
)

wrplu_file = "wrplu" / Struct(
    GreedyRange(wrapper_chunk)
)
# wrplu_file = "wrplu" / Struct(
#     # there can be some data, after unpacking from wrpl
#     # ...
#     # don't know how to iterate, till fond first substring in construct, hardcoded offset for testing
#     Seek(0x8),
#     some_struct,
#     some_struct,
#     some_struct,
#     # dont know how handle here, just Seek
#     #some_struct
#     Seek(519, 1),
#     some_struct,
#     some_struct,
#     some_struct,
#     #node_000d, but cant parse last part
#     #some_struct
#     Seek(100,1),
#     some_struct,
#     some_struct,
#     some_struct,
#     some_struct,
#     some_struct,
#     #node_000d, but cant parse last part
#     #some_struct
#     Seek(98, 1),
#     some_struct,
#     some_struct,
#     some_struct,
#     some_struct,
#     some_struct,
#     some_struct
# )

