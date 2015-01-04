import struct, sys, pylzma, ctypes, os, zlib

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


def unpack(data):
    """
    Unpack data from ddsx and returns it. If data have wrong header, prints error
    and exit(1). Return unpacked dds data, ready for saving.

    :param data: ddsx data
    """
    header_format = struct.unpack_from('4s', data, 0x4)[0]
    if header_format not in ddsx_types:
        print 'wrong ddsx type:', header_format
        exit(1)

    dds_width = struct.unpack_from('H', data, 0xc)[0]
    dds_height = struct.unpack_from('H', data, 0xe)[0]
    dds_unpacked_body_size = struct.unpack_from('I', data, 0x18)[0]
    dds_body_size = struct.unpack_from('I', data, 0x1c)[0]

    dds_data = ctypes.create_string_buffer(0x80)
    struct.pack_into('128B', dds_data, 0, *dds_header)
    struct.pack_into('I', dds_data, 0xc, dds_width)
    struct.pack_into('I', dds_data, 0x10, dds_height)
    struct.pack_into('I', dds_data, 0x14, dds_unpacked_body_size)
    struct.pack_into('4s', dds_data, 0x54, header_format)

    if dds_body_size == 0:  # not packed
        return dds_data.raw + data[0x20:]
    elif struct.unpack_from('I', data, 0x20)[0] == 0x1000005d:  # packed with lzma
        return dds_data.raw + pylzma.decompress(data[0x20:], maxlength=dds_unpacked_body_size)
    else:  # packed with zlib
        return dds_data.raw + zlib.decompress(data[0x20:])


def main():
    if len(sys.argv) != 2:
        print 'usage: ddsx_unpack.py file'
        sys.exit(1)

    filename = sys.argv[1]

    data = []
    with open(filename, 'rb') as f:
        data = f.read()

    if len(data) == 0:
        print "empty file"
        exit(1)

    dds_data = unpack(data)
    with open(os.path.split(filename)[1].split('.')[0] + '.dds', 'wb') as f:
        f.write(dds_data)


if __name__ == '__main__':
    main()
