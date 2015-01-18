import struct, sys
from time import ctime


sz_file_from_header_offset = 0x8
num_of_units_in_file_offset = 0xc
bbf_magic = '\x00BBF'

type_list = {
    0x0: 'size', 0x1: 'str', 0x2: 'int', 0x3: 'float', 0x4: 'typex3',
    0x5: 'typex4', 0x6: 'typex2', 0x7: 'typex5', 0x8: 'typex8',  0x9: 'bool',
    0xa: 'color', 0xb: 'typex10', 0xc: 'time', 0x10: 'typex7', 0x89: 'typex'
    }


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
        elif type_list[block_type] == 'typex':
            return struct.unpack_from('B', data, id_offset + 0x2)[0], 0x4
        elif type_list[block_type] == 'bool':
            return struct.unpack_from('B', data, id_offset + 0x2)[0], 0x4
        elif type_list[block_type] == 'size':  # [xxyy], xx - flat size, yy - group num
            return struct.unpack_from('HH', data, id_offset + 0x4), 0x8
        elif type_list[block_type] == 'typex3':
            return struct.unpack_from('ff', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'typex4':
            return struct.unpack_from('fff', data, id_offset + 0x4), 0x10
        elif type_list[block_type] == 'typex5':
            return struct.unpack_from('II', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'time':  # unixtime
            return struct.unpack_from('II', data, id_offset + 0x4), 0xc
        elif type_list[block_type] == 'typex2':
            return list(struct.unpack_from('ffff', data, id_offset + 0x4)), 0x14
        elif type_list[block_type] == 'typex10':
            ret = []
            ret.append(get_block_value(data, id_offset, 0x6)[0])
            ret.append(get_block_value(data, id_offset + 0x10, 0x6)[0])
            ret.append(get_block_value(data, id_offset + 0x20, 0x6)[0])
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
        return 'yes' if item_data else 'no'
    elif item_type == 'typex':
        return 'yes' if not item_data else 'no'
    elif item_type == 'color':
        return "#{:x}".format(item_data)
    elif item_type in ['typex7', 'int']:
        return item_data
    elif item_type in ['typex2', 'typex4', 'typex3']:
        return [float("{:.4f}".format(i)) for i in item_data]
    elif item_type == 'time':
        return ctime(item_data[0])
    elif item_type in ['typex5', 'typex8', 'typex10']:
        return list(item_data)
    else:
        print "error, unknown type = {:x}".format(item_type)
        exit(1)


# data_c - data container, ids_w_names - {id: name} pairs, sub_units_names - text names from 2th text block
def print_all_data(data_c, ids_w_names, sub_units_names):
    indent = 0
    ind_sizes = []
    ind_sizes.append([0, 0])
    all_text = []
    for i in data_c:
        for k, v in i.iteritems():
            v_type = type_list[v[0]]
            if v_type in ['str', 'time']:
                all_text.append("{}{}:{} = '{}'".format(' ' * (indent * 4), ids_w_names[k], v_type,
                    print_item(v_type, v[1], sub_units_names)))
            elif v_type == 'size':
                all_text.append("\n{}{}{{".format(' ' * (indent * 4), ids_w_names[k]))
                indent += 1
                ind_sizes.append([v[1][0] + 1, v[1][1]])  # flat + inner groups
            elif v_type in ['float', 'bool', 'typex', 'color', 'typex7', 'int', 'typex2',
                'typex4', 'typex3', 'typex5', 'typex8', 'typex10']:
                all_text.append("{}{}:{} = {}".format(' ' * (indent * 4), ids_w_names[k], v_type,
                    print_item(v_type, v[1], sub_units_names)))
            else:
                print "{}{}:{} = {}".format(' ' * (indent * 4), ids_w_names[k], v_type, v[1])
                print 'error, new type?'
                exit(1)
        ind_sizes[-1][0] -= 1
        while ind_sizes[-1][0] == 0 and ind_sizes[-1][1] == 0:
            ind_sizes.pop()
            indent -= 1
            ind_sizes[-1][1] -= 1
            all_text.append('{}}}'.format(' ' * (indent * 4)))
    return all_text


def unpack(data):
    """
    Parse file from data and return list of strings.

    :param data: blk data
    :return: list of strings
    """
    if struct.unpack_from('4s', data, 0)[0] != bbf_magic:
        print "wrong file type"
        exit(1)

    #print 'file length: ' + str(len(data))

    '''sz_file_from_header = struct.unpack_from('I', data, sz_file_from_header_offset)[0]
    print 'data length: ' + str(sz_file_from_header)'''

    num_of_units_in_file = struct.unpack_from('I', data, num_of_units_in_file_offset)[0]
    #print '\nnum of units: ' + str(num_of_units_in_file)
    
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

    #print '\nnum of sub units: ' + str(total_sub_units)
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
    
    full_data = parse_data(data, cur_p)
    
    if len(units_names) != len(ids_w_names):
        print "error, units != ids", len(units_names), len(ids_w_names), ", not all keys correct!"

    return print_all_data(full_data, ids_w_names, sub_units_names)


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


def parse_data(data, cur_p):
    """
    Read main block of data and parse it.

    :param data: blk data
    :param cur_p: pointer where to start
    :return: list with {key_id: [key_type, key_value]} items
    """
    full_data = []
    block_sizes = []
    b_size, flat = read_first_header(data, cur_p)
    for i in b_size[::-1]:
        block_sizes.append(i)

    cur_p += 4
    while cur_p < len(data):
        if not flat:  # more headers
            b_id, b_type = get_block_id_w_type(data, cur_p)
            b_value, b_off = get_block_value(data, cur_p, b_type)
            cur_p += b_off
            full_data.append({b_id: [0x0, b_value]})
            for i in b_value[::-1]:
                block_sizes.append(i)
        if cur_p == len(data):
            print 'error, EOF! ', hex(cur_p)
            break
        for i in xrange(block_sizes[-1]):
            b_id, b_type = get_block_id_w_type(data, cur_p)
            b_value, b_off = get_block_value(data, cur_p, b_type)
            cur_p += b_off
            full_data.append({b_id: [b_type, b_value]})
        flat = False
        block_sizes.pop()
        while len(block_sizes) != 0 and block_sizes[-1] == 0:
            block_sizes.pop()
        if len(block_sizes) != 0:
            block_sizes[-1] -= 1
        if len(block_sizes) == 0:
            break
    return full_data


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
        f.write('\n'.join(unpack(data)))
        f.write('\n')


if __name__ == '__main__':
    main()
