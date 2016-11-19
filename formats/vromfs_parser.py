from construct import *

NOT_PACKED_ADDED_OFFSET = 0x10
NOT_PACKED_FILE_DATA_TABLE_OFFSET = 0x20
NOT_PACKED_FILENAME_TABLE_OFFSET = 0x40

vromfs_type = Enum(
    Int32ub,
    not_packed=0x80
)

filename_table = Struct(
    # move to start of filename table
    Seek(NOT_PACKED_FILENAME_TABLE_OFFSET, 0),
    # here we can find offset table: (total_files * 8 byte) size
    "table_start_offset" / Int32ul,
    "table_start_offset" / Computed(this.table_start_offset + NOT_PACKED_ADDED_OFFSET),
    # but we cheat, just read total_files * cstrings
    Seek(this.table_start_offset, 0),
    "filenames" / Array(this._.files_count, CString())
)

file_data_record = Struct(
    "file_data_offset" / Int32ul,
    "file_data_offset" / Computed(this.file_data_offset + NOT_PACKED_ADDED_OFFSET),
    "file_data_size" / Int32ul,
    "unknown" / Hex(Bytes(8)),
    "next_file_data_record" / Tell,
    # move to file data offset
    Seek(this.file_data_offset, 0),
    # read file data
    "data" / Bytes(this.file_data_size),
    # return to next file data record in table
    Seek(this.next_file_data_record, 0)
)

file_data_table = Struct(
    # move to location of file data table offset
    Seek(NOT_PACKED_FILE_DATA_TABLE_OFFSET, 0),
    "table_start_offset" / Int32ul,
    "table_start_offset" / Computed(this.table_start_offset + NOT_PACKED_ADDED_OFFSET),
    # move to file data table start
    Seek(this.table_start_offset, 0),
    "file_data_list" / Array(this._.files_count, file_data_record)
)

vromfs_file = Struct(
    "magic" / Const(b"VRFs"),
    "unknown_1" / Hex(Bytes(8)),
    "vromfs_type" / vromfs_type,
    "unknown_2" / Int32ul,
    "files_count" / Int32ul,
    "filename_table" / filename_table,
    "file_data_table" / file_data_table
)
