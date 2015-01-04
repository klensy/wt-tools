import struct, sys, os, errno


dxp2_magic = 'DxP2'
file_names_block_offset = 0x48
second_block_offset_from = 0x10  # + 0x10
dds_block_offset_from = 0x20  # + 0x10
block_3_offset_from = 0x30  # + 0x10
block_4_offset_from = 0xc  # + 0x10


def mkdir_p(path):
    n_path = ''.join(os.path.split(path)[:-1])
    try:
        if n_path != '':
            os.makedirs(n_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(n_path):
            pass
        else:
            raise


def main():
    if len(sys.argv) != 2:
        print 'usage: dxp_unpack.py file'
        sys.exit(1)

    filename = sys.argv[1]
    dist_dir = filename + '_u/'

    data = []
    with open(filename, 'rb') as f:
        data = f.read()

    if len(data) == 0:
        print "empty file"
        exit(1)

    if struct.unpack_from('4s', data, 0)[0] != dxp2_magic:
        print "wrong dxp type"
        exit(1)

    total_files = struct.unpack_from('H', data, 0x8)[0]
    print "total files:", total_files
    cur_p = file_names_block_offset

    file_names = []
    for i in xrange(total_files):
        old_cur_p = cur_p
        while ord(data[cur_p]) != 0x0:
            cur_p += 1
        file_names.append(data[old_cur_p: cur_p])
        cur_p += 1

    for i in file_names:
        print i

    cur_p = struct.unpack_from('I', data, second_block_offset_from)[0] + 0x10
    offsets_block_1 = []
    for i in xrange(total_files):
        offsets_block_1.append(struct.unpack_from('I', data, cur_p)[0])
        cur_p += 0x8
    # print offsets_block_1

    '''
    from end:
        0x4: unpacked size
        0x4: packed size
    '''
    cur_p = struct.unpack_from('I', data, dds_block_offset_from)[0] + 0x10
    dds_block = []
    for i in xrange(total_files):
        dds_block.append(data[cur_p: cur_p + 0x20])
        cur_p += 0x20
    # print dds_block

    '''
        0xc - offset
        0x10 - size
    '''
    cur_p = struct.unpack_from('I', data, block_3_offset_from)[0] + 0x10
    block_3 = []
    for i in xrange(total_files):
        offset = struct.unpack_from('I', data, cur_p + 0xc)[0]
        size = struct.unpack_from('I', data, cur_p + 0x10)[0]
        block_3.append((offset, size))
        cur_p += 0x18
    # print block_3

    mkdir_p(dist_dir)
    for i, (off, size) in enumerate(block_3):
        with open(dist_dir + file_names[i].split('*')[0] + '.ddsx', 'wb') as f:
            f.write(dds_block[i])
            f.write(data[off: off + size])


if __name__ == '__main__':
    main()
