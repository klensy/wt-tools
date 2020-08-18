import binascii
import datetime
import json
import os.path

import bencodepy
import click
import jsondiff

IGNORED_LIST = ['compiledShaders', 'win32', 'win64', 'EasyAntiCheat', 'frameworks.zip', 'ca-bundle.crt',
                'cef_paks.zip', 'mac.zip', 'linux64', 'mac_cef_framework.zip', 'mac_cef_bin.zip', 'mac_sign.zip']


def parse_yup(file: os.PathLike):
    with open(file, 'rb') as f:
        data = f.read()

    d_data = bencodepy.decode(data)

    # print("version:", d_data[b'yup'][b'version'])

    data1 = dict()
    for file in d_data[b'info'][b'files']:
        # only files, skip other things
        if b'sha1' in file.keys():
            f_path = os.path.join(*file[b'path']).decode()
            f_sha1 = binascii.hexlify(file[b'sha1']).decode()
            f_time = str(datetime.datetime.utcfromtimestamp(file[b'mtime']))
            f_size = file[b'length']
            data1[f_path] = {'sha1': f_sha1, 'time': f_time, 'size': f_size}
    return data1


def make_diff(file_old: os.PathLike, file_new: os.PathLike, show_all: bool):
    data1 = parse_yup(file_old)
    data2 = parse_yup(file_new)

    diff = jsondiff.diff(data1, data2, syntax='symmetric')
    diff_fixed = dict()
    for filename, attributes in diff.items():
        # if we see completely new files, add it
        if isinstance(filename, jsondiff.Symbol):
            if filename == jsondiff.insert:
                for filename_interal, attr_values in attributes.items():
                    diff_fixed[filename_interal] = {'new': attr_values}
                continue
            elif filename == jsondiff.delete:
                for filename_interal, attr_values in attributes.items():
                    diff_fixed[filename_interal] = {'remove': attr_values}
                continue
            else:
                raise NotImplementedError("This jsondiff type not implemented, {}".format(filename))
        # skip key if not show_all and only time changed
        if not show_all and len(attributes) == 1 and list(attributes.keys())[0] == 'time':
            continue
        # skip key if not show_all and filename in boring list
        if not show_all and any([filename.startswith(x) for x in IGNORED_LIST]):
            continue
        diff_fixed[filename] = {'old': {}, 'new': {}}
        for attribute, attr_values in attributes.items():
            diff_fixed[filename]['old'][attribute] = attr_values[0]
            diff_fixed[filename]['new'][attribute] = attr_values[1]
    return json.dumps(diff_fixed, indent=2)


@click.command()
@click.argument('old_file', type=click.Path(exists=True))
@click.argument('new_file', type=click.Path(exists=True))
@click.option('--show_boring', is_flag=True, default=False)
def main(old_file: os.PathLike, new_file: os.PathLike, show_boring):
    """
    update_differ: diffs two *.yup files to show what's changed and output it's sha1, size, file path in json.

    OLD_FILE, NEW_FILE: paths to 2 yup files to diff
    --show_boring: shows all files that hidden by default: *.exe files and files with only timestamp changed
    """
    diff = make_diff(old_file, new_file, show_boring)
    print(diff)


if __name__ == '__main__':
    main()
