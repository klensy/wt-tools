import argparse


def xxor(data, key):
    d_data = bytearray(len(data))
    key_length = len(key)
    for i, c in enumerate(data):
        d_data[i] = (c ^ key[i % key_length])
    return d_data


def main():
    parser = argparse.ArgumentParser(description="Decrypt *.clog files")
    parser.add_argument('-i', dest='in_file', required=True,
                        type=argparse.FileType('rb'), help="*.clog file")
    parser.add_argument('-k', dest='key_file', required=True,
                        type=argparse.FileType('rb'), help="file with decryption key")
    parser.add_argument('-o', dest='out_file', required=True,
                        type=argparse.FileType('wb'), help="output file")

    try:
        parse_result = parser.parse_args()
    except IOError in msg:
        parser.error(str(msg))
        exit(1)

    data = bytearray(parse_result.in_file.read())
    parse_result.in_file.close()
    if len(data) == 0:
        print ("empty file")
        exit(1)

    key_data = bytearray(parse_result.key_file.read())
    parse_result.key_file.close()

    with parse_result.out_file as f:
        f.write(xxor(data, key_data))


if __name__ == '__main__':
    main()
