import errno
import json
import os
from hashlib import md5
from typing import Optional

import click
import zstandard

from formats.vromfs_parser import vromfs_file


def mkdir_p(path):
    n_path = ''.join(os.path.split(path)[:-1])
    try:
        if n_path != '':
            os.makedirs(n_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(n_path):
            pass
        else:
            raise


def unpack(filename: os.PathLike, dist_dir: os.PathLike, file_list_path: Optional[os.PathLike] = None):
    """
    Unpacks files from vromfs

    :param filename: path to vromfs file
    :param dist_dir: path to output dir
    :param file_list_path: path to file list, if you want to unpack only few files, in json list.
    """
    with open(filename, 'rb') as f:
        data = f.read()
    parsed = vromfs_file.parse(data)

    # want to unpack only listed files
    if file_list_path:
        with open(file_list_path, 'r') as f:
            file_list = json.load(f)

        # normalise paths in inputted list
        file_list = [os.path.normcase(p) for p in file_list]

    is_new_version = parsed.is_new_version
    is_dict_here = parsed.body.data.data.filename_table.filenames[0].filename.endswith('.dict')
    if is_new_version and is_dict_here:
        zstd_dict = zstandard.ZstdCompressionDict(parsed.body.data.data.file_data_table.file_data_list[0].data,
                                                  dict_type=zstandard.DICT_TYPE_AUTO)
        # print("dict_id", zstd_dict.dict_id())
        dctx = zstandard.ZstdDecompressor(dict_data=zstd_dict, format=zstandard.FORMAT_ZSTD1)

    with click.progressbar(range(parsed.body.data.data.files_count), label="Unpacking files") as bar:
        for i in bar:
            vromfs_internal_file_path = parsed.body.data.data.filename_table.filenames[i].filename
            # clean leading slashes, there was a bug in 1.99.1.70 with "/version" file path
            vromfs_internal_file_path = vromfs_internal_file_path.lstrip('/\\')
            if file_list_path:
                # TODO should be mostly the same as normal path, dedup
                # FIXME this branch may be broken now
                if os.path.normcase(vromfs_internal_file_path) in file_list:
                    unpacked_filename = os.path.join(dist_dir, vromfs_internal_file_path)
                    mkdir_p(unpacked_filename)
                    with open(unpacked_filename, 'wb') as f:
                        if is_new_version and is_dict_here and i != 0 and unpacked_filename.endswith('.blk'):
                            f.write(dctx.decompress(parsed.body.data.data.file_data_table.file_data_list[i].data))
                        else:
                            f.write(parsed.body.data.data.file_data_table.file_data_list[i].data)
            else:
                unpacked_filename = os.path.join(dist_dir, vromfs_internal_file_path)
                mkdir_p(unpacked_filename)
                with open(unpacked_filename, 'wb') as f:
                    if is_new_version and is_dict_here and i != 0 and unpacked_filename.endswith('.blk'):
                        packed_type = parsed.body.data.data.file_data_table.file_data_list[i].data[0]
                        # not zstd packed, small blk file?
                        if packed_type == 3:
                            f.write(parsed.body.data.data.file_data_table.file_data_list[i].data[1:])
                        # zstd packed blk file
                        elif packed_type == 5:
                            dict_decoded_data = dctx.decompress(
                                parsed.body.data.data.file_data_table.file_data_list[i].data[1:])
                            f.write(dict_decoded_data)
                        # not zstd packed, raw text blk file?
                        else:
                            # print("unknown packed_type:{}, file:{}".format(packed_type,unpacked_filename))
                            f.write(parsed.body.data.data.file_data_table.file_data_list[i].data)
                    # last file `?nm` - name map
                    # skip first 40 bytes, unpack, and few start bytes in unpacked namemap is unknown
                    elif is_new_version and is_dict_here and i == parsed.body.data.data.files_count - 1:
                        name_map_decompressed = dctx.decompress(
                            parsed.body.data.data.file_data_table.file_data_list[i].data[40:],
                            max_output_size=parsed.body.data.data.file_data_table.file_data_list[i].file_data_size)
                        f.write(name_map_decompressed)
                    # older blk versions
                    else:
                        f.write(parsed.body.data.data.file_data_table.file_data_list[i].data)


def files_list_info(filename: os.PathLike, dist_file: Optional[os.PathLike]) -> Optional[str]:
    with open(filename, 'rb') as f:
        data = f.read()
    parsed = vromfs_file.parse(data)
    out_list = []

    for i in range(parsed.body.data.data.files_count):
        m = md5(parsed.body.data.data.file_data_table.file_data_list[i].data).hexdigest()
        out_list.append({"filename": os.path.normcase(parsed.body.data.data.filename_table.filenames[i]), "hash": m})
    out_json = json.dumps({'version': 1, 'filelist': out_list})
    if not dist_file:
        return out_json
    else:
        with open(dist_file, 'w') as f:
            f.write(out_json)


@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('-O', '--output', 'output_path', type=click.Path(), default=None)
@click.option('--metadata', 'metadata', is_flag=True, default=False)
@click.option('--input_filelist', 'input_filelist', type=click.Path(), default=None)
def main(filename: os.PathLike, output_path: Optional[os.PathLike], metadata: bool, input_filelist: Optional[os.PathLike]):
    """
    vromfs_unpacker: unpacks vromfs file into folder

    FILENAME: vromfs file to unpack

    -O, --output: path where to unpack vromfs file, by default is FILENAME with appended _u, like some.vromfs.bin_u

    --metadata: if present, prints metadata of vromfs file: json with filename: md5_hash. If --output option used,
    prints to file instead.

    --input_filelist: pass the file with list of files you want to unpack and only this files will be unpacked.
    Files should be a json list format, like: `["buildtstamp", "gamedata/units/tankmodels/fr_b1_ter.blk"]`

    example: `vromfs_unpacker some.vromfs.bin` will unpack content to some.vromfs.bin_u folder. If you want to unpack to
    custom folder, use `vromfs_unpacker some.vromfs.bin --output my_folder`, that will unpack some.vromfs.bin folder to
    my_folder. If you want to get only file metadata, use `vromfs_unpacker some.vromfs.bin --metadata`. If you want to
    unpack only few selected manually files, place json list of files in file, and use
    `vromfs_unpacker some.vromfs.bin --input_filelist my_filelist.txt`
    """
    if metadata:
        if output_path:
            files_list_info(filename, dist_file=output_path)
        else:
            print(files_list_info(filename, dist_file=None))
    else:
        # unpack into output_folder/some.vromfs.bin folder
        if output_path:
            output_path = os.path.join(output_path, os.path.basename(filename))
        # unpack all into some.vromfs.bin_u folder
        else:
            head, tail = os.path.split(filename)
            output_path = os.path.join(head, tail + '_u')
        unpack(filename, output_path, input_filelist)


if __name__ == '__main__':
    main()
