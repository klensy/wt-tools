import argparse
import os.path
from typing import AnyStr, Dict

from lark import Lark

from formats.common import blk_transformer, get_tool_path

strip_options = {
    'strip_empty_objects': False,
    'strip_comment_objects': False,
    'strip_disabled_objects': False
}


def minify(blk_data: AnyStr, minify_options: Dict[AnyStr, bool]) -> AnyStr:
    grammar_path = 'blk.lark'
    blk_parser = Lark(open(os.path.join(get_tool_path(), grammar_path)).read(), parser='lalr',
                      transformer=blk_transformer(minify_options), keep_all_tokens=True)

    return blk_parser.parse(blk_data)


def main():
    parser = argparse.ArgumentParser(description="minify blk")
    parser.add_argument('filename', help="blk file")
    parser.add_argument("-O", dest='out_filename', default=False, nargs='?', help="output file")
    # removes not all empty objects, really
    parser.add_argument('--strip_empty_objects', dest='strip_empty_objects', action="store_true",
                        default=False, help="remove empty objects")
    # only comment objects, inlined one, like `comments:t=""` not removed
    parser.add_argument('--strip_comment_objects', dest='strip_comment_objects', action="store_true",
                        default=False, help="remove comment objects")
    parser.add_argument('--strip_disabled_objects', dest='strip_disabled_objects', action="store_true",
                        default=False, help="remove disabled objects")
    parser.add_argument('--strip_all', dest='strip_all', action="store_true",
                        default=False, help="select all options")
    parse_result = parser.parse_args()

    filename = parse_result.filename

    out_filename = ''
    if parse_result.out_filename:
        out_filename = parse_result.out_filename
    else:
        f_path, f_ext = os.path.splitext(filename)
        out_filename = f_path + '.min' + f_ext

    if parse_result.strip_all:
        for option in strip_options:
            strip_options[option] = True

    if parse_result.strip_empty_objects:
        strip_options['strip_empty_objects'] = True

    if parse_result.strip_comment_objects:
        strip_options['strip_comment_objects'] = True

    if parse_result.strip_disabled_objects:
        strip_options['strip_disabled_objects'] = True

    if not os.path.exists(filename):
        print("File", filename, "not exist")
        return
    # get size, as we get it wrong from text opened file
    parsed_file_size = os.path.getsize(filename)
    if parsed_file_size == 0:
        with open(out_filename, 'wb') as f:
            pass
        return
    with open(filename, mode='r', encoding="utf8") as f:
        data = f.read()

    parsed_data = minify(data, strip_options)
    with open(out_filename, 'w', encoding="utf8") as f:
        f.write(parsed_data)
    print("minified {} from {} to {}, with rate {:.2}".format(filename,
                                                              parsed_file_size, len(parsed_data),
                                                              len(parsed_data) / parsed_file_size))


if __name__ == '__main__':
    main()
