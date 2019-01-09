import struct

from construct import Enum, Int16ul, Const, Struct, Int32ub, Int32ul, Bytes, this, Int24ul, Seek

from .common import zlib_stream


# there should be better way to build this, but i don't know it, for now
def simple_blk_build(obj):
    return b"".join([obj.magic, struct.pack('>I', obj.unknown_0), struct.pack('<I', obj.blk_body_size), obj.blk_body])

# i think not byte, but word\dword
wrpl_version = "wrpl_version" / Enum(Int16ul,
                                     version_1_45=0x889a,
                                     version_1_47=0x88c8,
                                     version_1_49=0x88ca,
                                     version_1_51=0x88e7,
                                     version_1_63=0x8964
                                     )

simple_blk = "blk" / Struct(
    "magic" / Const(b"\x00BBF"),
    "unknown_0" / Int32ub,
    "blk_body_size" / Int32ul,
    # maybe find more suitable format?
    "blk_body" / Bytes(this.blk_body_size),
)

wrpl_file = "wrpl" / Struct(
    "magic" / Const(b"\xe5\xac\x00\x10"),
    wrpl_version,
    # here we ignore some bytes, better version detect i think
    "unknown_0" / Int24ul,
    # there skip some data, not used now anyway
    # ...
    Seek(0x450 if wrpl_version == "version_1_45" else 0x440),
    "m_set" / simple_blk,
    "wrplu" / zlib_stream,
    "rez" / simple_blk,
)
