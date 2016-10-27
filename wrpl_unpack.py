import os.path, struct, zlib
import argparse

WRPL_MAGIC = 0xe5ac0010


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

    if struct.unpack_from('>I', data, 0)[0] != WRPL_MAGIC:
        raise TypeError("Wrong wrpl file")
    current_replay_version = struct.unpack_from('B', data, 0x4)[0]
    if current_replay_version == 0x9a:  # 1.45
        blk_start_off = 0x450
    elif current_replay_version in [0xc8, 0xca, 0xe7, 0x64]:  # 1.47, 1.51, 1.63
        blk_start_off = 0x440
    else:
        raise TypeError("Unknown wrpl version")

    cur_p = blk_start_off + 0x8  # BBF header + size
    first_bbf_file_size = struct.unpack_from('I', data, cur_p)[0]
    cur_p = blk_start_off + first_bbf_file_size + 0xc

    blk_files.append(('m_set', data[blk_start_off: cur_p]))
    unc_replay, blk_off_from_end = zlib_decompress(data, cur_p)
    open(os.path.splitext(filename)[0] + '.' + 'wrplu', 'wb').write(unc_replay)
    # old replays(1.43?) need +4 to start point: data[len(data) - blk_off_from_end + 4:]
    blk_files.append(('rez', data[len(data) - blk_off_from_end:]))

    for blk in blk_files:
        with open(os.path.splitext(filename)[0] + '.' + blk[0] + '.blk', 'wb') as f:
            f.write(blk[1])


def zlib_decompress(data, offset):
    zdo = zlib.decompressobj()
    uncompressed_data = zdo.decompress(data[offset:])
    # print "unused: %s" % (len(zdo.unused_data))
    return uncompressed_data, len(zdo.unused_data)


def main():
    parser = argparse.ArgumentParser(description="Unpacks wrpl replays to wrplu data file and blk files")
    parser.add_argument('filename', help="unpack from")
    parse_result = parser.parse_args()

    filename = parse_result.filename

    with open(filename, 'rb') as f:
        data = f.read()

    unpack(data, filename)

if __name__ == '__main__':
    main()
