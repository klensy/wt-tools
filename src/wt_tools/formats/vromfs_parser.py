import struct
import zstandard

from construct import Construct, Enum, Byte, this, Adapter, Struct, Seek, Int32ul, Array, CString, Tell, If, Bytes, \
    Computed, Embedded, Switch, Error, Const, Int24ul, Hex, String

from .common import zlib_stream

NOT_PACKED_ADDED_OFFSET = 0x10
NOT_PACKED_FILE_DATA_TABLE_OFFSET = 0x20
NOT_PACKED_FILENAME_TABLE_OFFSET = 0x40

vromfs_type = Enum(
    Byte,
    unknown_type=0x40,
    maybe_packed=0x80,
    zstd_packed=0xc0
)


class ZstdContext(Construct):
    def __init__(self):
        super(ZstdContext, self).__init__()

    def _parse(self, stream, ctx, path):
        need_read_size = ctx._._.header.packed_size - (16 if ctx.first_part else 0) - (16 if ctx.second_part else 0)
        # ugly: align read size to 4 bytes
        need_read_size = need_read_size // 4 * 4
        deobfs_compressed_data = (ctx.first_part if ctx.first_part else b'') + \
                                 stream.getvalue()[ctx.middle_data_offset:ctx.middle_data_offset + need_read_size] + \
                                 (ctx.second_part.data if ctx.second_part.data else b'') + \
                                 (ctx.align_tail if ctx.align_tail else b'')
        dctx = zstandard.ZstdDecompressor()
        decompressed_data = dctx.decompress(deobfs_compressed_data, max_output_size=ctx._._.header.original_size)
        ctx.parsed_data = vromfs_not_packed_body.parse(decompressed_data)


class ZlibAdapter(Adapter):
    def _decode(self, obj, context):
        return vromfs_not_packed_body.parse(obj)


class Obfs16Adapter(Adapter):
    def _decode(self, obj, context):
        return struct.pack("<4L", *[x ^ y for (x, y) in zip(obj, [0xAA55AA55, 0xF00FF00F, 0xAA55AA55, 0x12481248])])


class Obfs32Adapter(Adapter):
    def _decode(self, obj, context):
        return struct.pack("<4L", *[x ^ y for (x, y) in zip(obj, [0x12481248, 0xAA55AA55, 0xF00FF00F, 0xAA55AA55])])


filename_table = Struct(
    # move to start of filename table
    Seek(this._.data_start_offset + this._.filename_table_offset, 0),
    # here we can find offset table: (total_files * 8 byte) size
    # but we cheat, just read total_files * cstrings
    "first_filename_offset" / Int32ul,
    Seek(this._.data_start_offset + this.first_filename_offset),
    "filenames" / Array(this._.files_count, CString())
)

file_data_record = Struct(
    "file_data_offset" / Int32ul,
    "file_data_offset" / Computed(this.file_data_offset + this._._.data_start_offset),
    "file_data_size" / Int32ul,
    "unknown" / Hex(Bytes(8)),
    "next_file_data_record" / Tell,
    # move to file data offset
    Seek(this.file_data_offset, 0),
    # read file data
    "data" / Bytes(this.file_data_size),
    # return to next file data record in table
    Seek(this.next_file_data_record, 0)
)

file_data_table = Struct(
    # move to location of file data table offset
    Seek(this._.data_start_offset + this._.filedata_table_offset, 0),
    # main actions in file_data_record
    "file_data_list" / Array(this._.files_count, file_data_record)
)
vromfs_not_packed_body = Struct(
    "data_start_offset" / Tell,
    "filename_table_offset" / Int32ul,
    "files_count" / Int32ul,
    Seek(8, 1),
    "filedata_table_offset" / Int32ul,
    "filename_table" / filename_table,
    "file_data_table" / file_data_table,
)

vromfs_zstd_packed_body = Struct(
    "before_obfs" / Tell,
    "first_part" / If(
        this._._.header.packed_size >= 16,
        Obfs16Adapter(Int32ul[4])
    ),
    "middle_data_offset" / Tell,
    "second_part" / If(
        this._._.header.packed_size >= 32,
        Struct(
            # 32 = length of obfuscated header + footer of data
            # ugly: align seek with 4 bytes
            Seek((this._._._.header.packed_size - 32) // 4 * 4, 1),
            "data" / Obfs32Adapter(Int32ul[4])
        )),
    "after_obfs" / Tell,
    # last part, if packed_size % 4 != 0
    "align_tail" / If(
        this._._.header.packed_size % 4,
        Bytes(this._._.header.packed_size % 4)
    ),
    ZstdContext(),
    Embedded(Computed(this.parsed_data))
)

vromfs_zlib_packed_body = Struct(
    Embedded(zlib_stream),
    Embedded(ZlibAdapter(Computed(this.decompressed_body)))
)

vromfs_header = Struct(
    # b"VRFs\x00\x00PC"
    "magic" / Const(String(4), b"VRFs"),
    "platform" / Enum(String(4), pc=b"\x00\x00PC", ios=b"\x00iOS", andr=b"\x00and"),
    "original_size" / Int32ul,
    "packed_size" / Int24ul,
    "vromfs_type" / vromfs_type,
    "vromfs_packed_type" / Computed(lambda ctx: "zstd_packed" if ctx.vromfs_type == "zstd_packed" else
        ("not_packed" if ctx.vromfs_type == "maybe_packed" and ctx.packed_size == 0 else
        ("zlib_packed" if ctx.vromfs_type == "maybe_packed" and ctx.packed_size > 0 else "hoo")))
)

vromfs_body = Struct(
    Embedded(Switch(this._.header.vromfs_packed_type, {
        "not_packed": vromfs_not_packed_body,
        "zstd_packed": vromfs_zstd_packed_body,
        "zlib_packed": vromfs_zlib_packed_body
    }, default=Error)),
)

vromfs_file = Struct(
    "header" / vromfs_header,
    "body" / vromfs_body,
    "tail" / Bytes(272)
)
