import struct
from time import ctime
import json
from collections import OrderedDict
import uuid
import argparse

type_list = {
    0x0: 'size', 0x1: 'str', 0x2: 'int', 0x3: 'float', 0x4: 'vec2f',
    0x5: 'vec3f', 0x6: 'vec4f', 0x7: 'vec2i', 0x8: 'typex8', 0x9: 'bool',
    0xa: 'color', 0xb: 'm4x3f', 0xc: 'time', 0x10: 'typex7',
    0x89: 'typex'  # same as 'bool', but reversed
}

# ingame names for types
type_list_strict_blk = {
    0x0: 'size', 0x1: 't', 0x2: 'i', 0x3: 'r', 0x4: 'p2',
    0x5: 'p3', 0x6: 'p4', 0x7: 'ip2', 0x8: 'typex8', 0x9: 'b',
    0xa: 'c', 0xb: 'm', 0xc: 'time', 0x10: 'typex7',
    0x89: 'b'  # same as 'bool', but reversed
}

# https://stackoverflow.com/questions/13249415
# using private interface
class NoIndent(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return repr(self.value)


class NoIndentEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(NoIndentEncoder, self).__init__(*args, **kwargs)
        self.kwargs = dict(kwargs)
        del self.kwargs['indent']
        self._replacement_map = {}

    def default(self, o):
        if isinstance(o, NoIndent):
            key = uuid.uuid4().hex
            self._replacement_map[key] = json.dumps(o.value, **self.kwargs)
            return "@@%s@@" % (key,)
        else:
            return super(NoIndentEncoder, self).default(o)

    def encode(self, o):
        result = super(NoIndentEncoder, self).encode(o)
        for k, v in self._replacement_map.iteritems():
            result = result.replace('"@@%s@@"' % (k,), v)
        return result


class BLK:
    sz_file_from_header_offset = 0x8
    num_of_units_in_file_offset = 0xc
    num_of_units_in_file_v3_offset = 0xe
    units_length_type_v3_offset = 0xd
    bbf_magic = '\x00BBF'
    output_type = {'json': 0x0, 'json_min': 0x1, 'strict_blk': 0x2}

    def __init__(self, data):
        self.data = data
        self.num_of_units_in_file = 0
        self.ids_w_names = dict()  # {key_id: key_string} for keys
        self.blk_version = 0  # 2 for 1.45 and lower, 3 for 1.47

    def unpack(self, out_type=output_type['json']):
        # check file header and version
        # TODO: error handle
        if struct.unpack_from('4s', self.data, 0)[0] != BLK.bbf_magic:
            print "wrong file type"
            exit(1)

        self.blk_version = struct.unpack_from('H', self.data, 0x4)[0]
        if self.blk_version == 2:  # 1.45
            self.num_of_units_in_file = struct.unpack_from('I', self.data, BLK.num_of_units_in_file_offset)[0]
            units_size, ids, cur_p = self.get_unit_sizes_and_ids()

            # at this point we have sizes of units
            while struct.unpack_from('H', self.data, cur_p)[0] == 0x0: cur_p += 2
            # now get unit names
            units_names = []
            for unit_size in units_size:
                units_names.append(self.data[cur_p: cur_p + unit_size])
                cur_p += unit_size

            for u_name in units_names:
                id_hash = self._hash_key_name(u_name)
                while id_hash in self.ids_w_names:
                    id_hash += 0x100
                self.ids_w_names[id_hash] = u_name

            # align to 0x4
            while cur_p % 4 != 0: cur_p += 1

            total_sub_units = struct.unpack_from('I', self.data, cur_p)[0]

            # print '\nnum of sub units: ' + str(total_sub_units)
            cur_p += 0x4
            sub_units_size = []
            while len(sub_units_size) < total_sub_units:
                sub_units_size.append(struct.unpack_from('H', self.data, cur_p)[0])
                cur_p += 2

            # at this point we have sizes of sub units
            sub_units_names = []
            for s_unit_size in sub_units_size:
                sub_units_names.append(self.data[cur_p: cur_p + s_unit_size])
                cur_p += s_unit_size

            # align by 0x4
            while cur_p % 0x4 != 0: cur_p += 1

            full_data = self.parse_data(cur_p, sub_units_names, out_type)
            if out_type == BLK.output_type['json']:
                return json.dumps(full_data, cls=NoIndentEncoder, indent=2, separators=(',', ': '))
            elif out_type == BLK.output_type['json_min']:
                return json.dumps(full_data, cls=NoIndentEncoder, separators=(',', ':'))
            elif out_type == BLK.output_type['strict_blk']:
                return self.print_strict_blk(full_data)
            else:
                print "error out type: %s" % (out_type)
                exit(1)

        elif self.blk_version == 3:
            units_length_type = struct.unpack_from('B', self.data, BLK.units_length_type_v3_offset)[0]
            if units_length_type == 0x41:
                cur_p = 0xf
                self.num_of_units_in_file = struct.unpack_from('B', self.data, BLK.num_of_units_in_file_v3_offset)[0]
            elif units_length_type == 0x81:
                cur_p = 0x10
                self.num_of_units_in_file = struct.unpack_from('H', self.data, BLK.num_of_units_in_file_v3_offset)[0]
            else:
                print 'error, unknown units_length_type = %d' % units_length_type
                exit(1)

            # print 'num_of_units_in_file = %d' % self.num_of_units_in_file

            for i in xrange(self.num_of_units_in_file):
                unit_length = struct.unpack_from('B', self.data, cur_p)[0]
                cur_p += 1
                id_name = self.data[cur_p: cur_p + unit_length]
                cur_p += unit_length
                id_hash = self._hash_key_name(id_name)
                while id_hash in self.ids_w_names:
                    id_hash += 0x100
                self.ids_w_names[id_hash] = id_name

            # align by 0x4
            while cur_p % 4 != 0: cur_p += 1
            # print 'cur_p: %d' % cur_p
            # test if there exist sub_units_names block
            sub_units_block_length = struct.unpack_from('H', self.data, cur_p)[0]
            if sub_units_block_length > 0:
                cur_p += 2
                sub_units_block_type = struct.unpack_from('B', self.data, cur_p + 1)[0]
                cur_p += 2
                if sub_units_block_type == 0x40:
                    total_sub_units = struct.unpack_from('B', self.data, cur_p)[0]
                    cur_p += 1
                elif sub_units_block_type == 0x80:
                    total_sub_units = struct.unpack_from('H', self.data, cur_p)[0]
                    cur_p += 2
                else:
                    print 'error, unknown sub_units_block_type: %d' % sub_units_block_type
                    exit(1)
            else:
                # no sub_units_names
                total_sub_units = 0
                cur_p += 4
            # print 'total_sub_units: %d' % total_sub_units
            sub_units_names = []
            for i in xrange(total_sub_units):
                unit_length = struct.unpack_from('B', self.data, cur_p)[0]
                cur_p += 1
                sub_units_names.append(self.data[cur_p: cur_p + unit_length])
                cur_p += unit_length
            # print sub_units_names

            # align by 0x4
            while cur_p % 0x4 != 0: cur_p += 1
            # print 'cur_p: %d' % cur_p

            full_data = self.parse_data(cur_p, sub_units_names, out_type)
            if out_type == BLK.output_type['json']:
                return json.dumps(full_data, cls=NoIndentEncoder, indent=2, separators=(',', ': '))
            elif out_type == BLK.output_type['json_min']:
                return json.dumps(full_data, cls=NoIndentEncoder, separators=(',', ':'))
            elif out_type == BLK.output_type['strict_blk']:
                return self.print_strict_blk(full_data)
            else:
                print "error out type: %s" % (out_type)
                exit(1)
        else:
            print 'error, unknown version %d' % self.blk_version
            exit(1)

    # return units_size, ids, cur_p
    def get_unit_sizes_and_ids(self):
        key_size = []  # length of string, which represents key
        keys = []  # strings, which represent keys

        # 0x100 in 1.43 - 1.45, 0x40 in 1.41
        header_type = struct.unpack_from('H', self.data, 0x10)[0]
        if header_type == 0x100:
            cur_p = 0x12
            block_size = 0x0  # keys in block
            keys_left = self.num_of_units_in_file
            while keys_left > 0:
                if block_size == 0:
                    while struct.unpack_from('H', self.data, cur_p)[0] == 0x0:
                        cur_p += 2
                    block_size = struct.unpack_from('H', self.data, cur_p)[0]
                    # remember number of added keys before adding new
                    total_keys_old = len(keys)
                    for i in xrange(block_size):
                        keys.append((cur_p - 0x12) // 2 - total_keys_old + i * 0x100)
                    cur_p += 2
                keys_left -= block_size
                while block_size > 0:
                    key_size.append(ord(self.data[cur_p]))
                    cur_p += 2
                    block_size -= 1
            return key_size, keys, cur_p
        else:
            print 'error, unknown block = {:x}'.format(header_type)
            exit(1)

    def parse_data(self, cur_p, sub_units_names, out_type):
        """
        Read main block of data and parse it.

        :param cur_p: pointer where to start
        :return: list (or dict, if no duplicates) with {key_id: [key_type, key_value]} items
        """
        # TODO split parsing and output to json\blkx
        b_size, flat = self.read_first_header(cur_p)
        cur_p += 4
        if self.blk_version == 2:
            full_data, cur_p = self.parse_inner(cur_p, b_size, sub_units_names, out_type)
        else:
            full_data, cur_p = self.parse_inner_v3(cur_p, b_size, sub_units_names, out_type)
        return full_data

    def read_first_header(self, offset):
        linear_units, group_num = struct.unpack_from('HH', self.data, offset)
        return (linear_units, group_num), True

    def parse_inner(self, cur_p, b_size, sub_units_names, out_type):
        # TODO: make class from it, drop ids_w_names, sub_units_names refs
        if out_type == BLK.output_type['strict_blk']:
            curr_block = []
        else:
            curr_block = OrderedDict()
        not_list = True  # flag for group_num == 0
        # print 'b_size', b_size
        while cur_p < len(self.data):
            flat_num, group_num = b_size
            if flat_num > 0:
                for i in xrange(flat_num):
                    b_id, b_type = self.get_block_id_w_type(cur_p)
                    b_value, b_off = self.get_block_value(cur_p, b_type)
                    cur_p += b_off
                    str_id, str_val = self.from_id_to_str(b_id, b_type, b_value, sub_units_names)
                    curr_block, not_list = self.parse_inner_detect_take(not_list,
                                                                        str_id, b_type,
                                                                        str_val, curr_block, out_type)
                b_size = (0, group_num)
            else:  # flat_num == 0
                b_id, b_type = self.get_block_id_w_type(cur_p)
                b_value, b_off = self.get_block_value(cur_p, b_type)
                cur_p += b_off
                if b_value != (0, 0):  # not empty group
                    inner_block, cur_p = self.parse_inner(cur_p, b_value, sub_units_names, out_type)
                else:
                    inner_block = []
                str_id, skip_block = self.from_id_to_str(b_id, b_type, b_value, sub_units_names)
                curr_block, not_list = self.parse_inner_detect_take(not_list,
                                                                    str_id, b_type,
                                                                    inner_block, curr_block, out_type)

                flat_num, group_num = b_size
                b_size = (flat_num, group_num - 1)
            if b_size == (0, 0):
                break
        return curr_block, cur_p

    def parse_inner_v3(self, cur_p, b_size, sub_units_names, out_type):
        # TODO: make class from it, drop ids_w_names, sub_units_names refs
        if out_type == BLK.output_type['strict_blk']:
            curr_block = []
        else:
            curr_block = OrderedDict()
        not_list = True  # flag for group_num == 0
        # print 'b_size, cur_p =', b_size, cur_p
        while cur_p < len(self.data):
            flat_num, group_num = b_size
            if flat_num > 0:
                id_list = []
                for i in xrange(flat_num):
                    b_id, b_type = self.get_block_id_w_type(cur_p)
                    b_value, b_off = self.get_block_value(cur_p, b_type)
                    id_list.append((b_id, b_type, b_value))
                    cur_p += 4
                # print id_list
                # print 'cur_p start 2th cycle: %d' % cur_p
                for b_id, b_type, b_value in id_list:
                    if type_list[b_type] == 'bool' or type_list[b_type] == 'typex':
                        str_id, str_val = self.from_id_to_str(b_id, b_type, b_value, sub_units_names)
                        curr_block, not_list = self.parse_inner_detect_take(not_list,
                                                                            str_id, b_type,
                                                                            str_val, curr_block, out_type)
                    else:
                        # - 0x4 in next line b'couse of stupid func, need fix it
                        b_value, b_off = self.get_block_value(cur_p - 0x4, b_type)
                        str_id, str_val = self.from_id_to_str(b_id, b_type, b_value, sub_units_names)
                        curr_block, not_list = self.parse_inner_detect_take(not_list,
                                                                            str_id, b_type,
                                                                            str_val, curr_block, out_type)
                        # and there
                        cur_p += b_off - 0x4
                b_size = (0, group_num)
            else:  # flat_num == 0
                b_id, b_type = self.get_block_id_w_type(cur_p)
                b_value, b_off = self.get_block_value(cur_p, b_type)
                # print 'b_id, b_type, b_value = ', b_id, b_type, b_value
                cur_p += b_off
                if b_value != (0, 0):  # not empty group
                    inner_block, cur_p = self.parse_inner_v3(cur_p, b_value, sub_units_names, out_type)
                else:
                    inner_block = []
                str_id, skip_block = self.from_id_to_str(b_id, b_type, b_value, sub_units_names)
                curr_block, not_list = self.parse_inner_detect_take(not_list,
                                                                    str_id, b_type,
                                                                    inner_block, curr_block, out_type)

                flat_num, group_num = b_size
                b_size = (flat_num, group_num - 1)
            if b_size == (0, 0):
                break
        return curr_block, cur_p

    def parse_inner_detect_take(self, is_not_list, str_id, val_type, value, block, out_type):
        """
        Check if str_id not already in block as key, and change it type
        to list if necessary(duplicated), and return block and is_not_list state
        """
        if out_type == BLK.output_type['strict_blk']:
            block.append((str_id, val_type, value))
        elif is_not_list:
            if str_id in block:  # duplicates, create list from dict
                block = [{c[0]: c[1]} for c in block.iteritems()]
                block.append({str_id: value})
                is_not_list = False
            else:
                block[str_id] = value
        else:
            block.append({str_id: value})
        return block, is_not_list

    # return block id with type
    def get_block_id_w_type(self, offset):
        block_id, block_type = struct.unpack_from('HxB', self.data, offset)
        return block_id, block_type

    def from_id_to_str(self, id, type, value, sub_units_names):
        item_id = self.ids_w_names[id]
        item_type = type_list[type]
        if item_type != 'size':
            item_value = self.print_item(item_type, value, sub_units_names)
            return item_id, item_value  # for json
        else:
            return item_id, []

    # return value, next offset
    def get_block_value(self, id_offset, block_type):
        if block_type not in type_list:
            print "error, unknown type = {:x}, position = {:x}".format(block_type, id_offset)
            exit(1)
        block_type_from_list = type_list[block_type]
        if block_type_from_list == 'str':
            value, offset = struct.unpack_from('I', self.data, id_offset + 0x4)[0], 0x8
        elif block_type_from_list == 'int':
            value, offset = struct.unpack_from('i', self.data, id_offset + 0x4)[0], 0x8
        elif block_type_from_list == 'float':
            value, offset = struct.unpack_from('f', self.data, id_offset + 0x4)[0], 0x8
        elif block_type_from_list == 'typex':  # reversed 'bool'
            value, offset = struct.unpack_from('B', self.data, id_offset + 0x2)[0], 0x4
        elif block_type_from_list == 'bool':
            value, offset = struct.unpack_from('B', self.data, id_offset + 0x2)[0], 0x4
        elif block_type_from_list == 'size':  # [xxyy], xx - flat size, yy - group num
            value, offset = struct.unpack_from('HH', self.data, id_offset + 0x4), 0x8
        elif block_type_from_list == 'vec2f':
            value, offset = struct.unpack_from('ff', self.data, id_offset + 0x4), 0xc
        elif block_type_from_list == 'vec3f':
            value, offset = list(struct.unpack_from('fff', self.data, id_offset + 0x4)), 0x10
        elif block_type_from_list == 'vec2i':
            value, offset = struct.unpack_from('II', self.data, id_offset + 0x4), 0xc
        elif block_type_from_list == 'time':  # unixtime
            value, offset = struct.unpack_from('II', self.data, id_offset + 0x4), 0xc
        elif block_type_from_list == 'vec4f':
            value, offset = struct.unpack_from('ffff', self.data, id_offset + 0x4), 0x14
        elif block_type_from_list == 'm4x3f':
            ret = [self.get_block_value(id_offset, 0x5)[0],
                   self.get_block_value(id_offset + 0xc, 0x5)[0],
                   self.get_block_value(id_offset + 0x18, 0x5)[0],
                   self.get_block_value(id_offset + 0x24, 0x5)[0]]
            value, offset = ret, 0x34
        elif block_type_from_list == 'color':  # color code, like #6120f00
            value, offset = struct.unpack_from('I', self.data, id_offset + 0x4)[0], 0x8
        elif block_type_from_list == 'typex7':  # what type?
            value, offset = struct.unpack_from('I', self.data, id_offset + 0x4)[0], 0x8
        elif block_type_from_list == 'typex8':  # what type?
            value, offset = struct.unpack_from('III', self.data, id_offset + 0x4), 0x10
        return value, offset

    def print_item(self, item_type, item_data, sub_units_names):
        if item_type == 'str':
            return sub_units_names[item_data]
        elif item_type == 'float':
            return float("{:.4f}".format(item_data))
        elif item_type == 'bool':
            return True if item_data else False
        elif item_type == 'typex':
            return True if not item_data else False
        elif item_type == 'color':
            return "#{:08x}".format(item_data)
        elif item_type in ['typex7', 'int']:
            return item_data
        elif item_type in ['vec4f', 'vec3f', 'vec2f']:
            return NoIndent([float("{:e}".format(i)) for i in item_data])
        elif item_type == 'time':
            return ctime(item_data[0])
        elif item_type in ['vec2i', 'typex8']:
            return NoIndent(list(item_data))
        elif item_type == 'm4x3f':  # 'vec3f' in 'm4x3f'
            return [self.print_item('vec3f', item, sub_units_names) for item in item_data]
        else:
            print "error, unknown type = {:x}".format(item_type)
            exit(1)

    # format output for strict blk type
    def print_item_for_strict_blk(self, item_str_id, item_type, item_data,
                                  indent_level):
        # check if item_str_id is string with spaces, then add quotes
        if ' ' in item_str_id:
            item_str_id = '"' + item_str_id + '"'
        ret = "{}{}:{}=".format('  ' * indent_level, item_str_id, type_list_strict_blk[item_type])
        item_type_from_list = type_list[item_type]
        if item_type_from_list == 'str':
            return '{}"{}"'.format(ret, item_data)
        elif item_type_from_list == 'bool' or item_type_from_list == 'typex':
            item_val = 'yes' if bool(item_data) else 'no'
            return ret + item_val
        elif item_type_from_list in ['vec4f', 'vec3f', 'vec2f', 'vec2i', 'typex8']:
            return ret + repr(item_data)[1:-1]
        elif item_type_from_list == 'm4x3f':
            return '{}{}'.format(ret, str(item_data).replace('],', ']'))
        elif item_type_from_list == 'color':
            color_string = ', '.join([str(int(item_data[i: i + 2], 16)) for i in xrange(1, 9, 2)])
            return '{}{}'.format(ret, color_string)
        else:
            return ret + str(item_data)

    def print_strict_blk(self, s_data):
        s_data_lines = self.print_strict_blk_inner(s_data)
        if s_data_lines[0] == '':
            s_data_lines.pop(0)
        return '\n'.join(s_data_lines)

    def print_strict_blk_inner(self, s_data, indent_level=0):
        lines = []
        for line in s_data:
            id_str_name = line[0]
            if type_list[line[1]] != 'size':
                lines.append(self.print_item_for_strict_blk(id_str_name, line[1], line[2], indent_level))
            else:  # inner list
                lines.append('')
                lines.append('{}{}{{'.format('  ' * indent_level, id_str_name))
                for i in self.print_strict_blk_inner(line[2], indent_level + 1):
                    lines.append(i)
                lines.append('{}}}'.format('  ' * indent_level))
        return lines

    def _hash_key_name(self, key):
        """
        Generate hashcode from 'key' string name.
        """
        key_hash = 0x5
        for c in key:
            key_hash = (33 * key_hash + ord(c)) & 0xff
        return key_hash


def main():
    parser = argparse.ArgumentParser(description="Unpacks blk files to human readable version")
    parser.add_argument('filename', help="unpack from")
    out_type_group = parser.add_mutually_exclusive_group()
    out_type_group.add_argument('--json', action="store_true", help="output in formatted json")
    out_type_group.add_argument('--json_min', action="store_true", help="output in minimal json")
    out_type_group.add_argument('--strict_blk', action="store_true", help="output in ingame blk format")
    parse_result = parser.parse_args()

    filename = parse_result.filename
    out_type = None
    if parse_result.json:
        out_type = BLK.output_type['json']
    elif parse_result.json_min:
        out_type = BLK.output_type['json_min']
    elif parse_result.strict_blk:
        out_type = BLK.output_type['strict_blk']
    else:
        out_type = BLK.output_type['json']

    with open(filename, 'rb') as f:
        data = f.read()

    if len(data) == 0:
        print "empty file"
        exit(1)

    blk = BLK(data)

    with open(filename + 'x', 'w') as f:
        f.write(blk.unpack(out_type))


if __name__ == '__main__':
    main()
