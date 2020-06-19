import os.path
import sys
import zlib

from construct import Construct, Struct, Tell, Computed, Seek, this, FlagsEnum, Container, BitwisableString
from lark import Transformer, tree, lexer


# used for unpacking zlib block and return in context
class ZlibContext(Construct):
    def __init__(self):
        super(ZlibContext, self).__init__()

    def _parse(self, stream, ctx, path):
        ctx.decompressed_data, ctx.size_of_unused_data = self._zlib_decompress(stream.getvalue()[ctx.start_offset:])

    def _zlib_decompress(self, data):
        zdo = zlib.decompressobj()
        decompressed_data = zdo.decompress(data)
        size_of_unused_data = len(zdo.unused_data)
        return decompressed_data, size_of_unused_data


class FlagsEnumCumulative(FlagsEnum):
    def __init__(self, subcon, *merge, **flags):
        super(FlagsEnumCumulative, self).__init__(subcon)
        for enum in merge:
            for enumentry in enum:
                flags[enumentry.name] = enumentry.value
        self.flags = flags
        # keep reverse sorted flag values, so we can substract from our flag
        self.flags_reverse_sorted = sorted(self.flags.items(), key=lambda x: x[1], reverse=True)

    def _decode(self, obj, context, path):
        obj2 = Container()
        obj2._flagsenum = True
        assert isinstance(obj, int)
        leftover = obj
        for name, value in self.flags_reverse_sorted:
            if leftover > value:
                leftover -= value
                obj2[BitwisableString(name)] = True
            else:
                obj2[BitwisableString(name)] = False
        return obj2


# only one 'real' field is `decompressed_body`, other only for changing offset
zlib_stream = "zlib_stream" / Struct(
    "start_offset" / Tell,
    ZlibContext(),
    "unused_size" / Computed(this.size_of_unused_data),
    "global_file_size" / Seek(0, 2),
    "decompressed_body" / Computed(this.decompressed_data),
    "end_offset" / Computed(this.global_file_size - this.unused_size),
    Seek(this.end_offset)
)


def blk_transformer(strip_options):
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

        def expr_end(self, s):
            return ";"

        def expr_end_optional(self, s):
            return ""

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
            if strip_options.get('strip_comment_objects', False):
                if s[0] == 'comment':
                    return ''
            # disabled objects starts with __ in mission editor:  __unitRespawn{
            if strip_options.get('strip_disabled_objects', False):
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
            if strip_options.get('strip_empty_objects', False):
                # there smth in object, except it's name plus braces
                if len(res) > 3:
                    return ''.join(res)
                else:
                    return ''
            else:
                return ''.join(res)

        def numbers_list(self, s):
            return ''.join(s)

        def values(self, s):
            return ''.join(s)

        def r_include(self, s):
            return ' '.join(s)

        def values_in_named_object(self, s):
            return ''.join(s)

    return BLKTransformer()


def get_tool_path() -> os.PathLike:
    tool_path = None
    if getattr(sys, 'frozen', False):
        # frozen
        tool_path = os.path.dirname(sys.executable)
    else:
        # unfrozen
        tool_path = os.path.dirname(os.path.realpath(__file__))
    return tool_path
