import zlib
import struct
from construct import *

point_f_3d = Struct(
    "x" / Float32l,
    "y" / Float32l,
    "z" / Float32l,
)

simple_blk = "blk" / Struct(
    "magic" / Const(b"\x00BBF"),
    "unknown_0" / Int32ub,
    "blk_body_size" / Int32ul,
    # maybe find more suitable format?
    "blk_body" / Bytes(this.blk_body_size)
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
    # "magic_3" / Enum(Int16ub,
    #                  val_x41x15=0x4115,
    #                  val_x40x5e=0x405e,
    #                  val_x40x62=0x4062,
    #                  val_x40x61=0x4061,
    #                  val_x40x5c=0x405c,
    #                  val_x40x60=0x4060,
    #                  val_x40x65=0x4065,
    #                  val_x44xa7=0x44a7),
    # "magic_4" / Const(b"\x0b\x02")
)

# with some text and points
subnode_0x0000 = Struct(
    # "field_0" / Enum(Int16ub,
    #                  val_0x00=0x00),
    "field_1" / Bytes(233),
    "field_2" / Bytes(35),
    # "magic_2" / Const(b"\x00\x40\x5b\x0b\x02")
    "magic_2" / Const(b"\x00")
)

# some_struct = "some_s" / Struct(
#     "magic" / Const(b"\x58\x39\xd0\x01"),
#     "field_0" / Enum(Int16ub,
#                      val_0x0d=0x0d,
#                      val_0x00=0x00),
#     Probe(),
#     Switch(this.field_0,
#            # duplicate, i know
#            {"val_0x0d": subnode_0x000d,
#             "val_0x00": subnode_0x0000})
# )

# class PassAdapter(Adapter):
#     # def _encode(self, obj, context):
#     #     return obj
#     def _decode(self, obj, context):
#         return obj

subnode_0x0004 = Struct(
    "first_name" / PascalString(Byte, encoding='ASCII'),
    "group_global_number" / Byte,
    "number" / Byte,
    "fun_words" / Array(this.number, PascalString(Byte)),
    Probe()
)

subnode_0x0007 = Struct(
    "unknown" / Enum(Byte,
                     val_x03=0x03,
                     val_x08=0x08,
                     default=Error
                     ),
    # "magic" / Const(b"\x08"),
    "subnode_0007_index" / Byte,
    "words" / Array(2, PascalString(Byte)),
    "data" / Bytes(88)
)

chunk_x03x42 = Struct(
    # "magic" / Const(b"\x03\x42"),
    # "data" / Int16ul,
    "magic3" / Const(b"\x00\x02"),
    "type2" / Int16ub,
    "chunk_x03x42_sw2" / Switch(this.type2, {
        0x5839: Struct(
            "magic2" / Const(b"\xd0\x01"),
            "type" / Int16ub,
            Probe(),
            "chunk_x03x42_sw" / Switch(this.type, {
                0x000d: subnode_0x000d,
                0x0007: subnode_0x0007
            },
                                       default=Error),
        ),
        0x582d: Struct(
            "magic" / Const(b"\xf0\x00"),
            "number" / Int16ul,
            "data" / Array(this.number, Bytes(8))
        ),
        0x5828: Struct(
            "unknown" / Byte,
            "name" / PascalString(Byte),
            "size" / Int16ul,
            "data" / Bytes(this.size)
        )
    },
                                default=Error),
)

chunk_x0bx02 = Struct(
    # "magic" / Const(b"\x0b\x02"),
    # "magic2" / Const(b"\x58\x39\xd0\x01"),
    "type2" / Int16ub,
    "chunk_x0bx02_sw" / Switch(this.type2, {
        0x5839: Struct(
            "magic" / Const(b"\xd0\x01"),
            "type" / Int16ub,
            "data" / Switch(this.type, {
                0x0000: subnode_0x0000,
                0x0004: subnode_0x0004,
                0x0007: subnode_0x0007,
                0x000d: subnode_0x000d
            },
                            default=Error),
        ),
        0x5828: Struct(
            "unknown" / Byte,
            "name" / PascalString(Byte),
            "size_or_what" / Byte,
            "unknown2" / If(this.size_or_what > 0x7f, Byte),
            # "unknown2" / Byte,
            "data" / simple_blk,
            "unknown3" / Byte
        ),
        # stub, till parse
        0x582d: Bytes(4778),
        # stub, till parse
        0x58c3: Bytes(13)
    },
                               default=Error),
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
    "wrapper_chunk_probe" / Probe(),
    # "chunk_data" / Bytes(this.chunk_size),
    "chunk_data2" / Struct(
        # "type" / Int16ub,
        # "chunk_data2_probe" / Probe(),
        "type" / Byte,
        "sw" / Switch(this.type, {
            0x03: Struct(
                "unknown" / Int24ul,
                chunk_x03x42
            ),
            0x0b: Struct(
                "magic" / Const(b"\x02"),
                chunk_x0bx02
            )
        },
                      default=Error),
        Probe()
    ),
    Probe()
)

wrplu_file = "wrplu" / Struct(
    GreedyRange(wrapper_chunk)
)
