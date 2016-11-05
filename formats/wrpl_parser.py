import zlib
import struct
from construct import *


class ZlibContext(Construct):
    def __init__(self):
        super(ZlibContext, self).__init__()

    def _parse(self, stream, ctx, path):
        ctx.decompressed_data, ctx.size_of_unused_data = self._zlib_decompress(stream.getvalue()[ctx.start_offset:])

    def _zlib_decompress(self, data):
        zdo = zlib.decompressobj()
        decompressed_data = zdo.decompress(data)
        size_of_unused_data = len(zdo.unused_data)
        return decompressed_data, size_of_unused_data


# there should be better way to build this, but i don't know it, for now
def simple_blk_build(obj):
    return "".join([obj.magic, struct.pack('>I', obj.unknown_0), struct.pack('<I', obj.blk_body_size), obj.blk_body])

# i think not byte, but word\dword
wrpl_version = "wrpl_version" / Enum(Byte,
                                     version_1_45=0x9a,
                                     version_1_47=0xc8,
                                     version_1_49=0xca,
                                     version_1_51=0xe7,
                                     version_1_63=0x64)

simple_blk = "blk" / Struct(
    "magic" / Const(b"\x00BBF"),
    "unknown_0" / Int32ub,
    "blk_body_size" / Int32ul,
    # maybe find more suitable format?
    "blk_body" / Bytes(this.blk_body_size),
)

# only one 'real' field is `decompressed_body`, other only for changing offset
zlib_stream = "zlib_stream" / Struct(
    "start_offset" / Tell,
    ZlibContext(),
    "unused_size" / Computed(this.size_of_unused_data),
    "global_file_size" / Seek(0, 2),
    "decompressed_body" / Computed(this.decompressed_data),
    "end_offset" / Computed(this.global_file_size - this.unused_size),
    Seek(this.end_offset)
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

