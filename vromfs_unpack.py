from zlib import decompress
import os, errno, sys, struct

g_file_off = 0x1d
g_file_np_off = 0x10
total_files_offset = 0x31
total_files_not_packed_offset = 0x14
files_content_start_offset_in_file = 0x2d
files_content_start_offset_in_not_packed_file = 0x20
files_names_table_off = 0x3d
files_names_table_np_off = 0x40
vrfs_magic = 0x73465256  # VRFs
vrfs_not_packed_magic = 0x80000000
vrfs_type = {'packed': 0x0, 'not_packed': 0x1}

class VRFS:

    def __init__(self, added_off, total_files_off, file_content_start_off, file_names_table_off):
        self.added_off = added_off
        self.total_files_off = total_files_off
        self.file_content_start_off = file_content_start_off
        self.file_names_table_off = file_names_table_off


packed_vrfs = VRFS(0x1d, 0x31, 0x2d, 0x3d)
not_packed_vrfs = VRFS(0x10, 0x14, 0x20, 0x40)

head_part = [
    0x56, 0x52, 0x46, 0x73, 0x00, 0x00, 0x50, 0x43,
    0xB0, 0xA8, 0x1A, 0x00, 0x51, 0x52, 0x05, 0x80,
    0x19, 0xFF, 0x78, 0x78, 0x9D, 0x00, 0x05, 0x52,
    0x4B, 0x00, 0x1A, 0xA8, 0xB0
    ]


tail_part = [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x14, 0x38, 0xD8, 0xD7, 0x94, 0x99, 0x33, 0xAE,
    0xA4, 0x2A, 0x68, 0x84, 0x13, 0x45, 0xEC, 0x6D,
    0x31, 0xB8, 0x7B, 0xF8, 0x97, 0x59, 0x00, 0x91,
    0x8C, 0xA9, 0x9E, 0x39, 0x50, 0xF7, 0xAF, 0x2A,
    0x75, 0xB6, 0xAA, 0x16, 0x38, 0x9D, 0x57, 0x67,
    0x8B, 0x5F, 0xF9, 0xE0, 0xF8, 0x1A, 0x26, 0xF9,
    0xA6, 0xFB, 0x88, 0x64, 0x32, 0x65, 0x9D, 0xBA,
    0x99, 0xCC, 0x26, 0xD9, 0xAD, 0x25, 0xAF, 0xE7,
    0x35, 0x98, 0x0F, 0x6F, 0xDD, 0x76, 0x82, 0x75,
    0x02, 0xB0, 0x7A, 0xAF, 0x9D, 0x21, 0x8A, 0xAD,
    0x0E, 0x1A, 0xC7, 0xE5, 0xFA, 0x35, 0x6C, 0xC3,
    0x50, 0x01, 0x40, 0x3E, 0xAB, 0xDB, 0x57, 0x9F,
    0x15, 0x8E, 0x39, 0xA4, 0x5F, 0x51, 0x51, 0xA3,
    0x6A, 0xA5, 0x2B, 0x59, 0x4E, 0xA0, 0xB4, 0x81,
    0x2B, 0xFC, 0xFF, 0x85, 0x03, 0xE1, 0x62, 0xB2,
    0xD2, 0x03, 0xE4, 0x95, 0x7D, 0x20, 0xCD, 0x3F,
    0x07, 0xB3, 0xBC, 0xE1, 0x42, 0x30, 0xE9, 0x14,
    0xF8, 0xFB, 0x91, 0x25, 0xD8, 0x2C, 0xED, 0x4C,
    0x84, 0x31, 0x29, 0xB7, 0x7B, 0xD1, 0x50, 0x12,
    0xA4, 0x78, 0x68, 0x00, 0xCC, 0x47, 0xE2, 0xBB,
    0x0D, 0xA1, 0x07, 0xAE, 0xC3, 0xD6, 0x21, 0x49,
    0x1D, 0x11, 0xBE, 0x25, 0xB7, 0x8D, 0x75, 0x98,
    0x43, 0xE5, 0x24, 0xFC, 0x83, 0x47, 0xC1, 0x12,
    0xB2, 0x29, 0xB7, 0x36, 0x3A, 0xCF, 0x72, 0x75,
    0x06, 0x46, 0x94, 0x66, 0xD5, 0x94, 0x5B, 0x5B,
    0x7B, 0xD3, 0x57, 0x8C, 0x13, 0x68, 0x08, 0xCC,
    0x38, 0xFB, 0xCE, 0x88, 0x19, 0xF8, 0x7C, 0x54,
    0xF5, 0xB4, 0xB4, 0x27, 0x6E, 0xC5, 0x24, 0x48,
    0x02, 0xE0, 0x88, 0x48, 0x1D, 0x1A, 0x36, 0x04,
    0x9E, 0x04, 0x98, 0x56, 0x94, 0xCB, 0xA4, 0xDD,
    0x74, 0x5B, 0x5E, 0xD3, 0xB1, 0xE0, 0x6B, 0x6D,
    0xD7, 0x68, 0x7F, 0x64, 0x69, 0x4E, 0xBF, 0x64,
    0xF8, 0x7F, 0x45, 0x8B, 0x74, 0xF7, 0x40, 0x9A,
    0x84, 0x29, 0xF0, 0xEC, 0xCC, 0x30, 0x21, 0x99,
    0x11, 0x26, 0xD3, 0x3E, 0xEB
    ]


def decomp_and_write(file, is_store_temp_file=False):
    with open(file, 'rb') as f:
        f_data = f.read()

    if struct.unpack_from('I', f_data, 0)[0] != vrfs_magic:
        print "wrong file type"
        exit(1)
    if struct.unpack_from('I', f_data, 0xc)[0] == vrfs_not_packed_magic:
        return f_data, vrfs_type["not_packed"]
    else:  # vrfs packed
        dec_data = decompress(f_data[0x10:])
        head_str = ''.join([chr(c) for c in head_part])
        tail_str = ''.join([chr(c) for c in tail_part])
        if is_store_temp_file:
            with open(file + '.dec', 'wb') as f:
                f.write(head_str)
                f.write(dec_data)
                f.write(tail_str)
    return head_str + dec_data + tail_str, vrfs_type["packed"]


def mkdir_p(path):
    n_path = ''.join(os.path.split(path)[:-1])
    try:
        if n_path != '': os.makedirs(n_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(n_path):
            pass
        else: raise


def main():
    if len(sys.argv) != 2:
        print 'usage: vromfs_unpack.py file'
        sys.exit(1)

    filename = sys.argv[1]
    dist_dir = filename + '_u/'

    data, vrfs_curr_type = decomp_and_write(filename)

    if vrfs_curr_type == vrfs_type["packed"]:
        print 'file lenght: ' + str(len(data))
        total_files = struct.unpack_from('I', data, total_files_offset)[0]
        print 'total files: ' + str(total_files)

        files_content_start_offset = struct.unpack_from('I', data, files_content_start_offset_in_file)[0]
        files_content_start_offset += g_file_off

        files_names_list = []
        for i in xrange(total_files):
            print '\n'
            name_off_src = files_names_table_off + i * 8
            name_off = struct.unpack_from('I', data, name_off_src)[0]
            name_off += g_file_off
            name = []
            for c in data[name_off:]:
                if ord(c) != 0x0:
                    name.append(c)
                else:
                    break
            name = ''.join(name)
            print name

            content_off_src = files_content_start_offset + i * 16
            content_off = struct.unpack_from('I', data, content_off_src)[0]
            content_off += g_file_off
            print 'cont offset: ' + str(content_off)
            content_size_off_src = content_off_src + 4
            content_size = struct.unpack_from('I', data, content_size_off_src)[0]
            print 'cont size: ' + str(content_size)
            content = data[content_off:content_off + content_size]
            mkdir_p(dist_dir + name)
            with open(dist_dir + name, 'wb') as f:
                f.write(content)
    else:
        total_files = struct.unpack_from('I', data, total_files_not_packed_offset)[0]
        print 'total files: ' + str(total_files)

        files_content_start_offset = struct.unpack_from('I', data, files_content_start_offset_in_not_packed_file)[0]
        files_content_start_offset += g_file_np_off

        files_names_list = []
        for i in xrange(total_files):
            print '\n'
            name_off_src = files_names_table_np_off + i * 8
            name_off = struct.unpack_from('I', data, name_off_src)[0]
            name_off += g_file_np_off
            name = []
            for c in data[name_off:]:
                if ord(c) != 0x0:
                    name.append(c)
                else:
                    break
            name = ''.join(name)
            print name

            content_off_src = files_content_start_offset + i * 16
            content_off = struct.unpack_from('I', data, content_off_src)[0]
            content_off += g_file_np_off
            print 'cont offset: ' + str(content_off)
            content_size_off_src = content_off_src + 4
            content_size = struct.unpack_from('I', data, content_size_off_src)[0]
            print 'cont size: ' + str(content_size)

            # content = blk + data (ddsx)
            content = data[content_off:content_off + content_size]
            blk_data_size = struct.unpack_from('I', content, 0x4)[0]
            blk_data = content[0x8: 0x8 + blk_data_size]
            ddsx_data_start = blk_data_size + 0x8  # 0x8 - header
            ddsx_data = content[ddsx_data_start:]
            mkdir_p(dist_dir + name)
            with open(dist_dir + name + '.blk', 'wb') as f:
                f.write(blk_data)
            with open(dist_dir + name, 'wb') as f:
                f.write(ddsx_data)

if __name__ == '__main__':
    main()
