import binascii
import datetime
import json
import os.path

import bencodepy
import jsondiff
import click

ignored_subfolders_list = ['compiledShaders', 'win32', 'win64', 'EasyAntiCheat', 'frameworks.zip', 'ca-bundle.crt',
    'cef_paks.zip', 'mac.zip', 'linux64', 'mac_cef_framework.zip', 'mac_cef_bin.zip', 'mac_sign.zip']


def parse_yup(file: os.PathLike, ignore=None):
    with open(file, 'rb') as f:
        data = f.read()
        
    d_data = bencodepy.decode(data)

    # print("version:", d_data[b'yup'][b'version'])

    data1 = dict()
    for file in d_data[b'info'][b'files']:
        # only files, skip other things
        if b'sha1' in file.keys():
            f_path = os.path.join(*file[b'path']).decode()
            if ignore and any([f_path.startswith(x) for x in ignore]):
                continue
            f_sha1 = binascii.hexlify(file[b'sha1']).decode()
            f_time = str(datetime.datetime.utcfromtimestamp(file[b'mtime']))
            f_size = file[b'length']
            data1[f_path] = {'sha1': f_sha1, 'time': f_time, 'size': f_size}
    return data1


def make_diff(file_old: os.PathLike, file_new: os.PathLike, ignore=None):
    data1 = parse_yup(file_old, ignore=ignore)
    data2 = parse_yup(file_new, ignore=ignore)
    
    diff = jsondiff.diff(data1, data2, syntax='symmetric')
    diff_fixed = dict()
    for filename, attributes in diff.items():
        diff_fixed[filename] = {'old': {}, 'new': {}}
        for attribute, attr_values in attributes.items():
            diff_fixed[filename]['old'][attribute] = attr_values[0]
            diff_fixed[filename]['new'][attribute] = attr_values[1]
    return json.dumps(diff_fixed)


@click.command()
@click.argument('old_file', type=click.Path(exists=True))
@click.argument('new_file', type=click.Path(exists=True))
@click.option('--show_boring', is_flag=True, default=False)
def main(old_file: os.PathLike, new_file: os.PathLike, show_boring):
    """
    update_differ: diffs two *.yup files to show what's changed and output it's sha1, size, file path in json.

    OLD_FILE, NEW_FILE: paths to 2 yup files to diff
    --show_boring: shows all files changed, like *.exe, hidden by default
    """
    if show_boring:
        diff = make_diff(old_file, new_file)
    else:
        diff = make_diff(old_file, new_file, ignore=ignored_subfolders_list)
    print(diff)
    

if __name__ == '__main__':
    main()
