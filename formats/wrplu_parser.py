from construct import *


# http://stackoverflow.com/questions/279561
def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(w_chunk_size=0)
def last_chunk_size(size, action):
    if "w_chunk_size" not in last_chunk_size.__dict__:
        last_chunk_size.w_chunk_size = 0
    if action == "set":
        last_chunk_size.w_chunk_size = size
        # print "sett:", last_chunk_size.w_chunk_size
    elif action == "get":
        return last_chunk_size.w_chunk_size
    else:
        Exception("unknown action")


@singleton
# For more informative error messages
class InfoError(Construct):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        raise ExplicitError("Error field was activated during parsing at 0x%x offset" % (stream.tell(),))

    def _build(self, obj, stream, context, path):
        raise ExplicitError("Error field was activated during parsing at 0x%x offset" % (stream.tell(),))

point_f_3d = Struct(
    "x" / Float32l,
    "y" / Float32l,
    "z" / Float32l,
)

simple_blk = "blk" / Struct(
    # b"\x00BBF"
    "magic" / Const(Int32ub, 0x00424246),
    "unknown_0" / Int32ub,
    "blk_body_size" / Int32ul,
    # maybe find more suitable format?
    "blk_body" / Bytes(this.blk_body_size)
)

# with some text and points
subnode_0x0000 = Struct(
    "unknown_1" / Bytes(26),
    "word" / PascalString(Byte),
    "unknown_2" / Bytes(231)
)

subnode_0x0004 = Struct(
    "first_name" / PascalString(Byte, encoding='ASCII'),
    "group_global_number" / Byte,
    "number" / Byte,
    "fun_words" / Array(this.number, PascalString(Byte)),
    Probe()
)

subnode_0x0006 = Struct(
    "magic" / Const(Byte, 0x00),
    "subnode_0006_index" / Byte,
    "unknown_padding" / If(
        lambda ctx: ctx.subnode_0006_index > 0x7f,
        Byte),
    "words" / Array(2, PascalString(Byte)),
    # bad hack, but don't know how detect 3th word
    "word_3th_length" / Byte,
    "3th_word" / IfThenElse(
        lambda ctx: ctx.word_3th_length < 0x21,
        Struct(
            "word" / String(this._.word_3th_length),
            "data" / Bytes(84)
        ),
        "data" / Bytes(85)
    ),
)

subnode_0x0007 = Struct(
    "unknown_1" / Enum(
        Byte,
        val_x03=0x03,
        val_x05=0x05,
        val_x08=0x08,
        default=InfoError
    ),
    "subnode_0007_index" / Byte,
    "unknown_2" / Byte,
    # some empty byte, seek 1 byte back
    "words" / IfThenElse(
        this.unknown_2 == 0x0,
        PascalString(Byte),
        Struct(
            Seek(-1, 1),
            Array(2, PascalString(Byte))
        ),
    ),
    # if length != 0, then there 3th word
    "3th_word" / PascalString(Byte),
    "subnode_0x0007_probe" / Probe(),
    "data" / Bytes(87)
)

subnode_0x0009 = Struct(
    "const" / Const(Byte, 0x00),
    "subnode_0x0009_index" / Byte,
    "unknown_data" / If(
        lambda ctx: ctx.subnode_0x0009_index > 0x7f,
        Byte),
    "data" / Bytes(50)
)

# battle objective?
subnode_0x000b = Struct(
    "subnode_000d_index" / Byte,
    "const" / Const(Int16ub, 0x0001),
    "word" / PascalString(Byte),
    "data" / Bytes(27)
)

# with some text and points
subnode_0x000d = Struct(
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
    "magic_2" / Const(Byte, 0x80),
)

subnode_0x0011 = Struct(
    "subnode_0x0011_index" / Byte,
    "unknown_1_1" / Byte,
    "type" / Byte,
    "unknown_1_2" / Switch(
        this.type, {
            0x01: Bytes(4),
            0x03: Bytes(3)
        },
        default=InfoError),
    "word_1" / PascalString(Byte),
    "unknown_2" / Bytes(18),
    "word_2" / PascalString(Byte),
    "unknown" / Bytes(5)
)

# wrong parse in test0.wrplu at 0x5f2
# wrapper_chunk size wrong
subnode_0x0014 = Struct(
    "subnode_0x0014_index" / Byte,
    "data" / Bytes(66)
)

chunk_x03x42 = Struct(
    "magic3" / Const(Int16ub, 0x0002),
    "type2" / Int16ub,
    Probe(),
    "chunk_x03x42_sw2" / Switch(this.type2, {
        0x5839: Struct(
            "magic2" / Const(Int16ub, 0xd001),
            "type" / Int16ub,
            Probe(),
            "chunk_x03x42_sw" / Switch(this.type, {
                0x000d: subnode_0x000d,
                0x0006: subnode_0x0006,
                0x0007: subnode_0x0007
            },
                                       default=InfoError),
        ),
        0x582d: Struct(
            # skip parsing this, till i have more ideas
            # - 0x8 = headers size
            "skip_size" / Computed(lambda ctx: last_chunk_size(0xdeadbeef, 'get') - 0x8),
            "some_data" / Bytes(this.skip_size),
            # need review parse this
            # "magic" / Const(b"\xf0\x00"),
            # "number" / Int16ul,
            # Probe(),
            # "data" / IfThenElse(this.number == 1,
            #                     Struct(
            #                         "data" / Bytes(51),
            #                         "nickname" / CString(encoding="utf8"),
            #                         # return 1 byte back, because null eaten by string
            #                         Seek(-1, 1),
            #                         # Bytes(50) or all zeroes?
            #                         GreedyRange(Const(b"\x00")),
            #                         Probe(),
            #                         "is_guild" / Byte,
            #                         "guild" / IfThenElse(this.is_guild == 0x40,
            #                                              # there no guild name
            #                                              Bytes(115)
            #                                              ,
            #                                              Struct(
            #                                                  Seek(-1, 1),
            #                                                  "guild_name" / PascalString(Byte),
            #                                                  "data3" / Bytes(117)
            #                                              )),
            #                         Probe()
            #                     ),
            #                     Array(this.number, Bytes(8))
            #                     )
        ),
        0x5828: Struct(
            "unknown" / Byte,
            "name" / PascalString(Byte),
            "size" / Int16ul,
            "data" / Bytes(this.size)
        ),
        # from t1.wrplu, unparsed
        0x5873: Bytes(45)
    },
                                default=InfoError),
)

chunk_x0bx02 = Struct(
    "type2" / Int16ub,
    "chunk_x0bx02_sw" / Switch(this.type2, {
        0x5839: Struct(
            "magic" / Const(Int16ub, 0xd001),
            "type" / Int16ub,
            "data" / Switch(this.type, {
                0x0000: subnode_0x0000,
                0x0004: subnode_0x0004,
                0x0006: subnode_0x0006,
                0x0007: subnode_0x0007,
                0x0009: subnode_0x0009,
                0x000b: subnode_0x000b,
                0x000d: subnode_0x000d,
                0x0011: subnode_0x0011,
                0x0014: subnode_0x0014
            },
                            default=InfoError),
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
        0x582d: Struct(
            # skip parsing this, till i have more ideas
            # - 0x4 = headers size
            "skip_size" / Computed(lambda ctx: last_chunk_size(0xdeadbeef, 'get') - 0x4),
            # ProbeInto(this.skip_size),
            "some_data" / Bytes(this.skip_size),
            # "unknown_flag" / Int16ub,
            # "data" / Switch(this.unknown_flag, {
            #     0xf001: Bytes(4776),
            #     0xf000: Struct(
            #         # need review parse this
            #         # "magic" / Const(b"\xf0\x00"),
            #         "number" / Int16ul,
            #         Probe(),
            #         "data" / IfThenElse(this.number == 1,
            #                             Struct(
            #                                 "data" / Bytes(51),
            #                                 "nickname" / CString(encoding="utf8"),
            #                                 # return 1 byte back, because null eaten by string
            #                                 Seek(-1, 1),
            #                                 # Bytes(50) or all zeroes?
            #                                 # "data2" / Bytes(50),
            #                                 GreedyRange(Const(b"\x00")),
            #                                 Probe(),
            #                                 "is_guild" / Byte,
            #                                 "guild" / IfThenElse(this.is_guild == 0x40,
            #                                                      # there no guild name
            #                                                      Bytes(115)
            #                                                      ,
            #                                                      Struct(
            #                                                          Seek(-1, 1),
            #                                                          "guild_name" / PascalString(Byte),
            #                                                          Probe(),
            #                                                          "data3" / Bytes(117)
            #                                                      )),
            #                                 Probe()
            #                             ),
            #                             Array(this.number, Bytes(8))
            #                             )
            #     )
            # },
            #                 default=InfoError)
        ),
        # Bytes(4778),
        # stub, till parse
        0x58c3: Bytes(13),
        # c&p from chunk_x03x42
        0x5873: Bytes(45),
        0x587c: Bytes(11)
    },
                               default=InfoError),
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
            BitsInteger(14)),
    ),
    "chunk_size" / Computed(this.chunk_params.chunk_size),
    Check(lambda ctx: ctx.chunk_size != 0),
    # global hack for skipping some chunks
    Computed(lambda ctx: last_chunk_size(ctx.chunk_size, 'set')),
    "wrapper_chunk_probe" / Probe(),
    # "chunk_data" / Bytes(this.chunk_size),
    "chunk_data2" / Struct(

        # skip small chunks
        "data" / IfThenElse(
            lambda ctx: ctx._.chunk_size < 0xf,
            Bytes(this._.chunk_size),
            Struct(
                "type" / Byte,
                "sw" / Switch(this.type, {
                    0x03: Struct(
                        "unknown" / Int24ul,
                        chunk_x03x42
                    ),
                    0x0b: Struct(
                        Struct(
                            "switch_byte" / Byte,
                            Switch(this.switch_byte, {
                                0x02: chunk_x0bx02,
                                0x03: Bytes(11)
                            },
                                   default=InfoError)
                        )
                    )
                },
                              default=InfoError),
                # Probe()
            )
        ),
    ),
    Probe()
)

wrplu_file = "wrplu" / Struct(
    GreedyRange(wrapper_chunk)
)
