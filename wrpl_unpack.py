import os.path, sys, struct, zlib
import blk_unpack


def unpack(data, filename):
    blk_files = []
    '''cur_p = 0x8
    while struct.unpack_from('B', data, cur_p)[0] != 0x0: cur_p += 1
    replay_level = data[0x8:cur_p]
    print replay_level

    cur_p = 0x88
    while struct.unpack_from('B', data, cur_p)[0] != 0x0: cur_p += 1
    game_data = data[0x88:cur_p]
    print game_data

    cur_p = 0x18c
    while struct.unpack_from('B', data, cur_p)[0] != 0x0: cur_p += 1
    gs_data = data[0x18c:cur_p]
    print gs_data

    cur_p = 0x20c
    while struct.unpack_from('B', data, cur_p)[0] != 0x0: cur_p += 1
    part_of_day = data[0x20c:cur_p]
    print part_of_day

    cur_p = 0x28c
    while struct.unpack_from('B', data, cur_p)[0] != 0x0: cur_p += 1
    visibility = data[0x28c:cur_p]
    print visibility'''

    cur_p = 0x450 + 0x8  # BBF header + size
    first_bbf_file_size = struct.unpack_from('I', data, cur_p)[0]
    cur_p = 0x450 + first_bbf_file_size + 0xc

    blk_files.append(('m_set', data[0x450: cur_p]))
    unc_replay, blk_off_from_end = zlib_decompress(data, cur_p)
    open(os.path.splitext(filename)[0] + '.' + 'wrplu', 'wb').write(unc_replay)
    # old replays(1.43?) need +4 to start point
    blk_files.append(('rez', data[len(data) - blk_off_from_end:]))

    for blk in blk_files:
        with open(os.path.splitext(filename)[0] + '.' + blk[0] + '.blkx', 'wb') as f:
            f.write('\n'.join(blk_unpack.unpack(blk[1])))
            f.write('\n')


def zlib_decompress(data, offset):
    zdo = zlib.decompressobj()
    uncompressed_data = zdo.decompress(data[offset:])
    # print "unused: %s" % (len(zdo.unused_data))
    return uncompressed_data, len(zdo.unused_data)


def main():
    if len(sys.argv) != 2:
        print 'usage: wrpl_unpack.py file'
        sys.exit(1)

    filename = sys.argv[1]

    data = []
    with open(filename, 'rb') as f:
        data = f.read()

    unpack(data, filename)

if __name__ == '__main__':
    main()
