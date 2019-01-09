import zlib

from construct import Construct, Struct, Tell, Computed, Seek, this


# used for unpacking zlib block and return in context
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
