import ctypes
import os.path
import struct
import sys
import zlib

import pylzma
import zstandard

from formats.common import get_tool_path
from formats.ddsx_parser import ddsx

ddsx_types = [b'DXT1', b'DXT5']

dds_header = [
    0x44, 0x44, 0x53, 0x20, 0x7C, 0x00, 0x00, 0x00,
    0x07, 0x10, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00,
    0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]

compression_type = {0x0: "not_packed", 0x20: "zstd", 0x40: "lzma", 0x60: "oodle", 0x80: "zlib"}

dll_name = 'oo2core_6_win64.dll'
dll_real_path = os.path.join(get_tool_path(), dll_name)
oodle_dll = None
if not os.path.exists(dll_real_path):
    print(
        "Can't unpack oodle compressed textures, until {} not placed to wt-tools directory"
        .format(dll_name))
else:
    oodle_dll = ctypes.cdll.LoadLibrary(dll_real_path)


def unpack(data: bytes):
    """
    Unpack data from ddsx and returns it. If data have wrong header, prints error
    and return None. Return unpacked dds data, ready for saving.

    :param data: ddsx data
    """
    parsed_data = ddsx.parse(data)
    texture_format = parsed_data.header.d3dFormat
    if texture_format not in ddsx_types:
        print("Texture format {} unsupported yet".format(texture_format))
        return

    dds_compression_type = struct.unpack_from('B', data, 0xb)[0]

    dds_data = ctypes.create_string_buffer(0x80)
    struct.pack_into('128B', dds_data, 0, *dds_header)
    struct.pack_into('I', dds_data, 0xc, parsed_data.header.h)
    struct.pack_into('I', dds_data, 0x10, parsed_data.header.w)
    struct.pack_into('I', dds_data, 0x14, parsed_data.header.memSz)
    struct.pack_into('B', dds_data, 0x1c, parsed_data.header.levels)
    struct.pack_into('4s', dds_data, 0x54, parsed_data.header.d3dFormat)

    dds_packed = compression_type.get(dds_compression_type, "")
    if dds_packed == "not_packed":
        d_data = data[0x20:]
    elif dds_packed == "lzma":
        d_data = pylzma.decompress(data[0x20:], maxlength=parsed_data.header.memSz)
    elif dds_packed == "zlib":
        d_data = zlib.decompress(data[0x20:])
    elif dds_packed == "oodle":
        '''
        private static extern long OodleLZ_Decompress(byte[] buffer, long bufferSize, byte[] result,
            long outputBufferSize, int a, int b, int c, long d, long e,
            long f, long g, long h, long i, int ThreadModule);
        '''
        if oodle_dll:
            decompressed_data = ctypes.create_string_buffer(parsed_data.header.memSz)
            res = oodle_dll.OodleLZ_Decompress(data[0x20:], parsed_data.header.packedSz,
                                               decompressed_data,
                                               parsed_data.header.memSz, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                               3)
            if res == 0:
                print("Error unpacking oodle compressed texture")
                return
            d_data = decompressed_data.raw
        else:
            print("unsupported compression type: {}".format(dds_packed))
    elif dds_packed == "zstd":
        dctx = zstandard.ZstdDecompressor()
        d_data = dctx.decompress(data[0x20:], max_output_size=parsed_data.header.memSz)
        if d_data == 0:
            print("Error unpacking zstd compressed texture")
            return
    else:
        print("Unknown compression type: {}".format(dds_compression_type))
        return

    if not d_data:
        print("unpacked data empty somehow")
        return

    if parsed_data.header.flags.FLG_REV_MIP_ORDER:
        # Reverse MIPMAP order (from smallest -> biggest to biggest -> smallest)
        if texture_format in [b'DXT1', b'DXT5']:
            # https://docs.microsoft.com/en-us/windows/win32/direct3ddds/dds-file-layout-for-textures
            def get_dxt1_size(t_width, t_height, dxt_version):
                dxt_size = max(1, (t_width + 3) // 4) * max(1, (t_height + 3) // 4)
                if dxt_version == b'DXT1':
                    return dxt_size * 8
                elif dxt_version == b'DXT5':
                    return dxt_size * 16
                else:
                    print("unknown dxt version: {}", dxt_version)
                    return

            pos = 0
            images = []
            for level in range(parsed_data.header.levels - 1, -1, -1):
                width = parsed_data.header.w // (2 ** level)
                height = parsed_data.header.h // (2 ** level)
                size = get_dxt1_size(width, height, texture_format)
                images.append(d_data[pos:pos + size])
                pos += size

            d_data = bytearray()
            for image in reversed(images):
                d_data.extend(image)

        elif parsed_data.header.levels > 1:
            # left unpacked data as is
            print("Dunno how to re-order mipmaps for format {}".format(texture_format))

    return dds_data.raw + d_data


def unpack_file(filename):
    # TODO: eliminate copy&paste with blk_unpack
    with open(filename, 'rb') as f:
        data = f.read()
    if len(data) == 0:
        print("empty file")
        return
    out_file = unpack(data)
    if out_file:
        with open(filename[:-1], 'wb') as f:
            f.write(out_file)


def unpack_dir(dirname):
    """
    Unpack all *.ddsx files in `dirname`
    """
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            subname = os.path.join(root, filename)
            if os.path.isfile(subname) and os.path.splitext(subname)[1] == '.ddsx':
                print("\n" + subname)
                unpack_file(subname)


def main():
    if len(sys.argv) != 2:
        print('usage: ddsx_unpack.py PATH\n'
              'where PATH - file or folder')
        sys.exit(1)

    filename = sys.argv[1]

    if os.path.isfile(filename):
        unpack_file(filename)
    else:
        unpack_dir(filename)


if __name__ == '__main__':
    main()
