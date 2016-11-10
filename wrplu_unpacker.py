import os.path
import argparse
from formats.wrplu_parser import wrplu_file


def unpack(data, filename):
    parsed = wrplu_file.parse(data)
    print parsed
    # dirty hack, till i discover how to do it right
    # open(os.path.splitext(filename)[0] + '.' + 'm_set.blk', 'wb').write(simple_blk_build(parsed.m_set))
    # open(os.path.splitext(filename)[0] + '.' + 'rez.blk', 'wb').write(simple_blk_build(parsed.rez))
    # open(os.path.splitext(filename)[0] + '.' + 'wrplu', 'wb').write(parsed.wrplu.decompressed_body)


def main():
    parser = argparse.ArgumentParser(description="Unpacks wrplu")
    parser.add_argument('filename', help="unpack from")
    parse_result = parser.parse_args()

    filename = parse_result.filename
    if not filename.endswith(".wrplu"):
        print "wrong file extension"
        exit(1)

    with open(filename, 'rb') as f:
        data = f.read()

    unpack(data, filename)

if __name__ == '__main__':
    main()
