import errno
import json
import os
from hashlib import md5
from typing import Optional

import click

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


def unpack(filename: os.PathLike, dist_dir: os.PathLike):
    with open(filename, 'rb') as f:
        data = f.read()
    parsed = vromfs_file.parse(data)

    with click.progressbar(range(parsed.body.files_count), label="Unpacking files") as bar:
        for i in bar:
            unpacked_filename = os.path.join(dist_dir, parsed.body.filename_table.filenames[i])
            mkdir_p(unpacked_filename)
            with open(unpacked_filename, 'wb') as f:
                f.write(parsed.body.file_data_table.file_data_list[i].data)


def files_list_info(filename: os.PathLike, dist_file: Optional[os.PathLike]) -> Optional[str]:
    with open(filename, 'rb') as f:
        data = f.read()
    parsed = vromfs_file.parse(data)
    out_list = []

    for i in range(parsed.body.files_count):
        m = md5(parsed.body.file_data_table.file_data_list[i].data).hexdigest()
        out_list.append({"filename": os.path.normcase(parsed.body.filename_table.filenames[i]), "hash": m})
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
def main(filename: os.PathLike, output_path: os.PathLike, metadata: bool):
    """
    vromfs_unpacker: unpacks vromfs file into folder

    FILENAME: vromfs file to unpack

    -O, --output: path where to unpack vromfs file, by default is FILENAME with appended _u, like some.vromfs.bin_u

    --metadata: if present, prints metadata of vromfs file: json with filename: md5_hash. If --output option used,
     prints to file instead.

    example: `vromfs_unpacker some.vromfs.bin` will unpack content to some.vromfs.bin_u folder. If you want to unpack to
    custom folder, use `vromfs_unpacker some.vromfs.bin --output my_folder`, that will unpack some.vromfs.bin folder to
    my_folder. If you want to get only file metadata, use `vromfs_unpacker some.vromfs.bin --metadata`
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
        unpack(filename, output_path)


if __name__ == '__main__':
    main()
