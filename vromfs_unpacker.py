import os
import sys
import errno
from formats.vromfs_parser import vromfs_file


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


def unpack(filename, dist_dir):
    with open(filename, 'rb') as f:
        data = f.read()
    parsed = vromfs_file.parse(data)

    for i in xrange(parsed.files_count):
        unpacked_filename = dist_dir + parsed.filename_table.filenames[i]
        mkdir_p(unpacked_filename)
        with open(unpacked_filename, 'wb') as f:
            f.write(parsed.file_data_table.file_data_list[i].data)


def main():
    if len(sys.argv) != 2:
        print 'usage: vromfs_unpacker.py file'
        sys.exit(1)

    filename = sys.argv[1]
    dist_dir = filename + '_u/'
    unpack(filename, dist_dir)


if __name__ == '__main__':
    main()
