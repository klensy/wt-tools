import argparse
from lark import Lark, Transformer, tree, lexer


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
        res = []
        for t in s:
            if type(t) == lexer.Token and t.type == 'NEWLINE':
                pass
            else:
                res.append(t)
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
    parse_result = parser.parse_args()

    filename = parse_result.filename
    out_filename = parse_result.out_filename

    with open(filename, mode='r', encoding="utf8") as f:
        data = f.read()

    blk_parser = Lark(open('blk.lark').read(), parser='lalr',
                      transformer=BLKTransformer(), keep_all_tokens=True)

    parsed_data = blk_parser.parse(data)
    with open(out_filename, 'w', encoding="utf8") as f:
        f.write(parsed_data)


if __name__ == '__main__':
    main()
