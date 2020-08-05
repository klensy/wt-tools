import struct

from construct import Enum, Int16ul, Const, Struct, Int32ub, Int32ul, Bytes, this, Int24ul, Seek, Switch, If,\
    IfThenElse, Pass, Probe

from .common import zlib_stream


# there should be better way to build this, but i don't know it, for now
def simple_blk_build(obj):
    return b"".join([obj.magic, struct.pack('>I', obj.unknown_0), struct.pack('<I', obj.blk_body_size), obj.blk_body])

wrpl_versions_list = {
    "version_1_45": 0x889a,
    "version_1_47": 0x88c8,
    "version_1_49": 0x88ca,
    "version_1_51": 0x88e7,
    "version_1_63": 0x8964,
    "version_1_63-99": 0x8a4b,
    "version_1_99": 0x8aa9,
}

simple_blk = "blk" / Struct(
    "magic" / Const(b"\x00BBF"),
    "unknown_0" / Int32ub,
    "blk_body_size" / Int32ul,
    # maybe find more suitable format?
    "blk_body" / Bytes(this.blk_body_size),
)

wrpl_file = "wrpl" / Struct(
    "magic" / Const(b"\xe5\xac\x00\x10"),
    "version" / Int16ul,
    # here we ignore some bytes, better version detect i think
    "unknown_0" / Int24ul,
    # there skip some data, not used now anyway
    # ...
    IfThenElse(
        this.version >= wrpl_versions_list['version_1_63-99'],
        Seek(0x444),
        IfThenElse(
            this.version >= wrpl_versions_list['version_1_63'],
            Seek(0x440),
            Seek(0x450)
        )
    ),
    "m_set" / simple_blk,
    "wrplu" / zlib_stream,
    "rez" / simple_blk,
)
