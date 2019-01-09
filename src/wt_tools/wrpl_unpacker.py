import os.path
import argparse
from formats.wrpl_parser import wrpl_file, simple_blk_build


def unpack(data, filename):
    parsed = wrpl_file.parse(data)
    # dirty hack, till i discover how to do it right
    open(os.path.splitext(filename)[0] + '.' + 'm_set.blk', 'wb').write(simple_blk_build(parsed.m_set))
    open(os.path.splitext(filename)[0] + '.' + 'rez.blk', 'wb').write(simple_blk_build(parsed.rez))
    open(os.path.splitext(filename)[0] + '.' + 'wrplu', 'wb').write(parsed.wrplu.decompressed_body)


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
