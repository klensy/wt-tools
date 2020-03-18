import struct, sys, ctypes, zlib
import os.path
import pylzma

ddsx_types = ['DXT1', 'DXT5']

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

compression_type = {0x0: "not_packed", 0x40: "lzma", 0x60: "oodle", 0x80: "zlib"}


def unpack(data):
    """
    Unpack data from ddsx and returns it. If data have wrong header, prints error
    and return None. Return unpacked dds data, ready for saving.

    :param data: ddsx data
    """
    header_format = struct.unpack_from('4s', data, 0x4)[0].decode("utf-8")
    if header_format not in ddsx_types:
        print('wrong ddsx type:', header_format)
        return

    dds_height = struct.unpack_from('H', data, 0xc)[0]
    dds_width = struct.unpack_from('H', data, 0xe)[0]
    dds_mipmapcount = struct.unpack_from('B', data, 0x10)[0]
    dds_unpacked_body_size = struct.unpack_from('I', data, 0x18)[0]
    dds_body_size = struct.unpack_from('I', data, 0x1c)[0]
    ddsx_unknown_flag_0 = struct.unpack_from('B', data, 0xa)
    if ddsx_unknown_flag_0 in [0, 1]:
        pass  # all unpack ok 11 c0 01 40, 11 40 01 40, 11 40 00 40
    dds_compression_type = struct.unpack_from('B', data, 0xb)[0]

    dds_data = ctypes.create_string_buffer(0x80)
    struct.pack_into('128B', dds_data, 0, *dds_header)
    struct.pack_into('I', dds_data, 0xc, dds_width)
    struct.pack_into('I', dds_data, 0x10, dds_height)
    struct.pack_into('I', dds_data, 0x14, dds_unpacked_body_size)
    struct.pack_into('B', dds_data, 0x1c, dds_mipmapcount)
    struct.pack_into('4s', dds_data, 0x54, header_format.encode('utf-8'))

    dds_packed = compression_type.get(dds_compression_type, "")
    if dds_packed == "not_packed":
        return dds_data.raw + data[0x20:]
    elif dds_packed == "lzma":
        return dds_data.raw + pylzma.decompress(data[0x20:], maxlength=dds_unpacked_body_size)
    elif dds_packed == "zlib":
        return dds_data.raw + zlib.decompress(data[0x20:])
    elif dds_packed == "oodle":
        print("unsupported compression type: {}".format(dds_packed))
    else:
        print("Unknown compression type: {}".format(dds_compression_type))
        return


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
                print(subname)
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
