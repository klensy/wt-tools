import errno
import os

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


@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('-O', '--output', 'output_dir', type=click.Path(file_okay=False), default=None)
def main(filename: os.PathLike,  output_dir):
    """
    vromfs_unpacker: unpacks vromfs file into folder

    FILENAME: vromfs file to unpack

    output: directory where to unpack vromfs file, by default is FILENAME with appended _u, like some.vromfs.bin_u

    example: `vromfs_unpacker some.vromfs.bin` will unpack content to some.vromfs.bin_u folder. If you want to unpack to
    custom folder, use `vromfs_unpacker some.vromfs.bin --output my_folder`, that will unpack some.vromfs.bin folder to
    my_folder.
    """
    # unpack all into some.vromfs.bin_u folder
    if not output_dir:
        head, tail = os.path.split(filename)
        output_dir = os.path.join(head, tail + '_u')
    # else unpack into output_folder/some.vromfs.bin folder
    else:
        output_dir = os.path.join(output_dir, os.path.basename(filename))
    unpack(filename, output_dir)


if __name__ == '__main__':
    main()
