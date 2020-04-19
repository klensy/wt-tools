import os.path
import argparse
from lark import Lark, Transformer, tree, lexer

strip_options = {
    'strip_empty_objects': False,
    'strip_comment_objects': False,
    'strip_disabled_objects': False
}


class BLKTransformer(Transformer):
    def var_value(self, s):
        if type(s[0]) == str:
            return s[0]
        elif type(s[0]) == tree.Tree:
            return ''.join(s[0].children)
        return s

    def var_name(self, s):
        if type(s) == list:
            pass
        return ''.join([value for value in s])

    def var_type(self, s):
        return s[0].value

    def t_equal(self, s):
        return s[0].value

    def t_colon(self, s):
        return s[0].value

    def expr_end(self, s):
        return ";"

    def r_sqb(self, s):
        return "]"

    def l_sqb(self, s):
        return "["

    def value_array_el(self, s):
        res = []
        for t in s:
            if type(t) == list:
                res.append(''.join(t))
            else:
                res.append(t)
        return ''.join(res)

    def value_array(self, s):
        res = []
        for t in s:
            if type(t) == tree.Tree:
                print("error in value_array?")
                exit(1)
            else:
                res.append(t)
        return ''.join(res)

    def key_type_value(self, s):
        res = []
        for t in s:
            if type(t) == list:
                res.append(t[0])
            else:
                res.append(t)
        return ''.join(res)

    def named_object(self, s):
        # better remove node, than transform it?
        res = []
        if strip_options['strip_comment_objects']:
            if s[0] == 'comment':
                return ''
        # disabled objects starts with __ in mission editor:  __unitRespawn{
        if strip_options['strip_disabled_objects']:
            if s[0].startswith('__'):
                return ''
        for t in s:
            # skip newline token
            if type(t) == lexer.Token and t.type == 'NEWLINE':
                pass
            # and empty string, from collapsed objects
            elif t == '':
                pass
            else:
                res.append(t)
        if strip_options['strip_empty_objects']:
            # there smth in object, except it's name plus braces
            if len(res) > 3:
                return ''.join(res)
            else:
                return ''
        else:
            return ''.join(res)

    def l_brace(self, s):
        return "{"

    def r_brace(self, s):
        return "}"

    def numbers_list(self, s):
        return ''.join(s)

    def value(self, s):
        return ''.join(s)


def main():
    parser = argparse.ArgumentParser(description="minify blk")
    parser.add_argument('filename', help="blk file")
    parser.add_argument("out_filename", help="output file")
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
    out_filename = parse_result.out_filename

    if parse_result.strip_all:
        for option in strip_options:
            strip_options[option] = True

    if parse_result.strip_empty_objects:
        strip_options['strip_empty_objects'] = True

    if parse_result.strip_comment_objects:
        strip_options['strip_comment_objects'] = True

    if parse_result.strip_disabled_objects:
        strip_options['strip_disabled_objects'] = True

    # get size, as we get it wrong from text opened file
    parsed_file_size = os.path.getsize(filename)
    with open(filename, mode='r', encoding="utf8") as f:
        data = f.read()

    blk_parser = Lark(open('blk.lark').read(), parser='lalr',
                      transformer=BLKTransformer(), keep_all_tokens=True)

    parsed_data = blk_parser.parse(data)
    with open(out_filename, 'w', encoding="utf8") as f:
        f.write(parsed_data)
    print("minified {} from {} to {}, with rate {:.2}".format(filename,
                                                              parsed_file_size, len(parsed_data),
                                                              len(parsed_data) / parsed_file_size))


if __name__ == '__main__':
    main()
