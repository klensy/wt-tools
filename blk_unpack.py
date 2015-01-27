import struct, sys
from time import ctime
import json
from collections import OrderedDict
import uuid


sz_file_from_header_offset = 0x8
num_of_units_in_file_offset = 0xc
bbf_magic = '\x00BBF'

type_list = {
    0x0: 'size', 0x1: 'str', 0x2: 'int', 0x3: 'float', 0x4: 'vec2f',
    0x5: 'vec3f', 0x6: 'vec4f', 0x7: 'vec2i', 0x8: 'typex8',  0x9: 'bool',
    0xa: 'color', 0xb: 'm4x3f', 0xc: 'time', 0x10: 'typex7',
    0x89: 'typex'  # same as 'bool', but reversed
    }

# https://stackoverflow.com/questions/13249415
# using private interface
class NoIndent(object):
    def __init__(self, value):
        self.value = value


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


def read_first_header(data, offset):
    linear_units, group_num = struct.unpack_from('HH', data, offset)
    return (linear_units, group_num), True


# return (block_group_id, in_group_num), block_type
def get_block_id_w_type(data, offset):
    block_group_id, block_in_group_num = struct.unpack_from('BB', data, offset)
    block_type = struct.unpack_from('B', data, offset + 0x3)[0]
    return (block_group_id, block_in_group_num), block_type


# return value, next offset
def get_block_value(data, id_offset, block_type):
    if block_type in type_list.keys():
        if type_list[block_type] == 'str':
            return struct.unpack_from('I', data, id_offset + 0x4)[0], 0x8
        elif type_list[block_type] == 'int':
            return struct.unpack_from('i', data, id_offset + 0x4)[0], 0x8
        elif type_list[block_type] == 'float':
            return struct.unpack_from('f', data, id_offset + 0x4)[0], 0x8
        elif type_list[block_type] == 'typex':  # reversed 'bool'
            return struct.unpack_from('B', data, id_offset + 0x2)[0], 0x4
        elif type_list[block_type] == 'bool':
            return struct.unpack_from('B', data, id_offset + 0x2)[0], 0x4
        elif type_list[block_type] == 'size':  # [xxyy], xx - flat size, yy - group num
            return struct.unpack_from('HH', data, id_offset + 0x4), 0x8
        elif type_list[block_type] == 'vec2f':
            return struct.unpack_from('ff', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'vec3f':
            return list(struct.unpack_from('fff', data, id_offset + 0x4)), 0x10
        elif type_list[block_type] == 'vec2i':
            return struct.unpack_from('II', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'time':  # unixtime
            return struct.unpack_from('II', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'vec4f':
            return struct.unpack_from('ffff', data, id_offset + 0x4), 0x14
        elif type_list[block_type] == 'm4x3f':
            ret = []
            ret.append(get_block_value(data, id_offset, 0x5)[0])
            ret.append(get_block_value(data, id_offset + 0xc, 0x5)[0])
            ret.append(get_block_value(data, id_offset + 0x18, 0x5)[0])
            ret.append(get_block_value(data, id_offset + 0x24, 0x5)[0])
            return ret, 0x34
        elif type_list[block_type] == 'color':  # color code, like #6120f00
            return struct.unpack_from('I', data, id_offset + 0x4)[0], 0x8
        elif type_list[block_type] == 'typex7':  # what type?
            return struct.unpack_from('I', data, id_offset + 0x4)[0], 0x8
        elif type_list[block_type] == 'typex8':  # what type?
            return struct.unpack_from('III', data, id_offset + 0x4), 0x10
    else:
        print "error, unknown type = {:x}, position = {:x}".format(block_type, id_offset)
        exit(1)


def print_item(item_type, item_data, sub_units_names):
    if item_type == 'str':
        return sub_units_names[item_data]
    elif item_type == 'float':
        return float("{:.4f}".format(item_data))
    elif item_type == 'bool':
        return True if item_data else False
    elif item_type == 'typex':
        return True if not item_data else False
    elif item_type == 'color':
        return "#{:x}".format(item_data)
    elif item_type in ['typex7', 'int']:
        return item_data
    elif item_type in ['vec4f', 'vec3f', 'vec2f']:
        return NoIndent([float("{:.4f}".format(i)) for i in item_data])
    elif item_type == 'time':
        return ctime(item_data[0])
    elif item_type in ['vec2i', 'typex8']:
        return NoIndent(list(item_data))
    elif item_type == 'm4x3f':  # 'vec3f' in 'm4x3f'
        return [print_item('vec3f', item, sub_units_names) for item in item_data]
    else:
        print "error, unknown type = {:x}".format(item_type)
        exit(1)


def from_id_to_str(id, type, value, ids_w_names, sub_units_names):
    item_id = ids_w_names[id]
    item_type = type_list[type]
    if item_type != 'size':
        item_value = print_item(item_type, value, sub_units_names)
        #return {'key': item_id, 'type': item_type, 'value': item_value}
        return item_id, item_value  # for json
    else:
        return {item_id: []}


def unpack(data):
    """
    Parse file from data and return list of strings.

    :param data: blk data
    :return: list of strings
    """
    if struct.unpack_from('4s', data, 0)[0] != bbf_magic:
        print "wrong file type"
        exit(1)

    # print 'file length: ' + str(len(data))

    '''sz_file_from_header = struct.unpack_from('I', data, sz_file_from_header_offset)[0]
    print 'data length: ' + str(sz_file_from_header)'''

    num_of_units_in_file = struct.unpack_from('I', data, num_of_units_in_file_offset)[0]
    # print '\nnum of units: ' + str(num_of_units_in_file)

    units_size, ids, cur_p = get_unit_sizes_and_ids(data, num_of_units_in_file)

    # at this point we have sizes of units
    while struct.unpack_from('H', data, cur_p)[0] == 0x0: cur_p += 2
    # now get unit names
    units_names = []
    for unit_size in units_size:
        units_names.append(data[cur_p: cur_p + unit_size])
        cur_p += unit_size
    ids_w_names = dict(zip(ids, units_names))

    # align to 0x4
    while cur_p % 4 != 0: cur_p += 1

    total_sub_units = struct.unpack_from('I', data, cur_p)[0]

    # print '\nnum of sub units: ' + str(total_sub_units)
    cur_p += 0x4
    sub_units_size = []
    while len(sub_units_size) < total_sub_units:
        sub_units_size.append(struct.unpack_from('H', data, cur_p)[0])
        cur_p += 2

    # at this point we have sizes of sub units
    sub_units_names = []
    for s_unit_size in sub_units_size:
        sub_units_names.append(data[cur_p: cur_p + s_unit_size])
        cur_p += s_unit_size

    # align by 0x4
    while cur_p % 0x4 != 0: cur_p += 1

    full_data = parse_data(data, cur_p, ids_w_names, sub_units_names)

    '''if len(units_names) != len(ids_w_names):
        print "error, units != ids", len(units_names), len(ids_w_names), ", not all keys correct!"'''

    return json.dumps(full_data, cls=NoIndentEncoder, indent=2, separators=(',', ': '))


# return units_size, ids, cur_p
def get_unit_sizes_and_ids(data, num_of_keys_in_file):
    key_size = []  # length of string, which represents key
    keys = []  # strings, which represent keys

    # 0x100 in 1.43 - 1.45, 0x40 in 1.41
    header_type = struct.unpack_from('H', data, 0x10)[0]
    if header_type == 0x100:
        cur_p = 0x12
        block_size = 0x0  # keys in block
        keys_left = num_of_keys_in_file
        while keys_left > 0:
            if block_size == 0:
                while struct.unpack_from('H', data, cur_p)[0] == 0x0:
                    cur_p += 2
                block_size = struct.unpack_from('H', data, cur_p)[0]
                # remember number of added keys before adding new
                total_keys_old = len(keys)
                for i in xrange(block_size):
                    keys.append(((cur_p - 0x12) // 2 - total_keys_old, i))
                cur_p += 2
            keys_left -= block_size
            while block_size > 0:
                key_size.append(ord(data[cur_p]))
                cur_p += 2
                block_size -= 1
        return key_size, keys, cur_p
    else:
        print 'error, unknown block = {:x}'.format(header_type)
        exit(1)


def parse_data(data, cur_p, ids_w_names, sub_units_names):
    """
    Read main block of data and parse it.

    :param data: blk data
    :param cur_p: pointer where to start
    :return: list with {key_id: [key_type, key_value]} items
    """
    # TODO split parsing and output to json\blkx
    b_size, flat = read_first_header(data, cur_p)
    cur_p += 4
    full_data, cur_p = parse_inner(data, cur_p, b_size, ids_w_names, sub_units_names)
    return full_data


def parse_inner(data, cur_p, b_size, ids_w_names, sub_units_names):
    # TODO: make class from it, drop ids_w_names, sub_units_names refs
    #curr_block = []
    #curr_block = {}
    curr_block = OrderedDict()
    not_list = True  # flag for group_num == 0
    # print 'b_size', b_size
    while cur_p < len(data):
        flat_num, group_num = b_size
        if flat_num > 0:
            for i in xrange(flat_num):
                b_id, b_type = get_block_id_w_type(data, cur_p)
                b_value, b_off = get_block_value(data, cur_p, b_type)
                cur_p += b_off
                str_id, str_val = from_id_to_str(b_id, b_type, b_value, ids_w_names, sub_units_names)
                if not_list:
                    if str_id in curr_block:  # double, create list from dict
                        curr_block = list([{c[0]: c[1]} for c in curr_block.iteritems()])
                        curr_block.append({str_id: str_val})
                        not_list = False
                    else:
                        curr_block[str_id] = str_val
                else:
                    curr_block.append({str_id: str_val})
            b_size = (0, group_num)
        else:  # flat_num == 0
            b_id, b_type = get_block_id_w_type(data, cur_p)
            b_value, b_off = get_block_value(data, cur_p, b_type)
            cur_p += b_off
            if b_value != (0, 0):  # not empty group
                inner_block, cur_p = parse_inner(data, cur_p, b_value, ids_w_names, sub_units_names)
                '''if len(inner_block) == 1:  # only 1 record, can be extracted from list
                    inner_block = inner_block[0]'''
            else:
                inner_block = None
            str_id = ids_w_names[b_id]
            
            if not_list:
                if str_id in curr_block:  # double, create list from dict
                    curr_block = list([{c[0]: c[1]} for c in curr_block.iteritems()])
                    curr_block.append({str_id: inner_block})
                    not_list = False
                else:
                    curr_block[str_id] = inner_block
            else:
                curr_block.append({str_id: inner_block})

            flat_num, group_num = b_size
            b_size = (flat_num, group_num - 1)
        if b_size == (0, 0):
                break
    return curr_block, cur_p


def main():
    if len(sys.argv) != 2:
        print 'usage: blk_unpack.py file'
        sys.exit(1)

    filename = sys.argv[1]

    data = []
    with open(filename, 'rb') as f:
        data = f.read()

    if len(data) == 0:
        print "empty file"
        exit(1)

    with open(filename + 'x', 'w') as f:
        f.write(unpack(data))


if __name__ == '__main__':
    main()
