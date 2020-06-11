## War Thunder resource extraction tools

Tools that help you extract resources from game: fonts, textures, FM/DM of tanks/planes/ships, parameters of weapons, and other interesting stuff.

It also should work for Cuisine Royale and Enlisted games.

All new features in [dev](https://github.com/klensy/wt-tools/tree/dev) branch, master updated not so frequently.
## Installation
#### Hard way
1. Download latest 3.7.* python x86_64 version from [here](https://www.python.org/downloads/).
2. Run installer, check box with "Add Python 3.7 to PATH".
3. Download scripts ("Download ZIP" button), extract somewhere.
4. Run scripts from console, as described lower.

#### Easy way
1. Download compiled files (exe files, compressed in archive) from [here](https://github.com/klensy/wt-tools/releases), **no python** required.
2. Unzip archive.  

If you want to unpack textures, you need to find (file not provided) and place `oo2core_6_win64.dll` file to wt-tools directory, near ddsx_unpack.exe.

## Usage

#### vromfs_unpacker
Tool for unpacking game archives, this archives can contain any type of data:

    vromfs_unpacker.exe somefile.vromfs.bin
This will unpack files from `somefile.vromfs.bin` to `somefile.vromfs.bin_u` folder.

Options:
* -O, --output: path where to unpack vromfs file, if omitted is FILENAME with appended _u, like some.vromfs.bin_u; if used
then, for example `vromfs_unpacker.exe somefile.vromfs.bin --output my_folder`
* --metadata: if present, prints metadata of vromfs file: json with {filename: md5_hash}. If `--output` option used,
prints to file instead.
* --input_filelist: pass the file with list of files you want to unpack and only this files will be unpacked.
File list should be a json array, like: `["buildtstamp", "gamedata/units/tankmodels/fr_b1_ter.blk"]`

#### dxp_unpack
Tool for unpacking texture archives:

    dxp_unpack.exe somefile.dxp.bin
This will unpack textures files from `somefile.dxp.bin` to `somefile.dxp.bin_u` folder,
but textures need to be unpacked with ddsx_unpack.

#### ddsx_unpack
Tool for unpacking textures, can be used to unpack single file or folder:

    ddsx_unpack.exe somefile.ddsx
This will unpack texture from `somefile.ddsx` to `somefile.dds`.

    ddsx_unpack.exe some_folder
This will unpack textures from folder `some_folder` to `some_folder`, unpacked textures will be inside with `*.dds` extension.
For unpacking most of textures, you need `oo2core_6_win64.dll`, as noted in installation section and will work only in Windows.

#### blk_unpack
Tool for unpacking blk files, that contain some text data

    blk_unpack.exe somefile.blk
This will unpack file from `somefile.blk` to `somefile.blkx`, data will be presented as json.
If you want to get ingame format, you can use this:

     blk_unpack.exe --format=strict_blk somefile.blk
This will unpack blk file to `somefile.blkx` in format, that can be used by game.
If you want unpack multiple files, pass folder name instead file name:

    blk_unpack.exe folder_name
This will unpack all blk filed in this folder into blkx files.

#### clog_unpack
Tool for 'decrypting' `*.clog` log files:

    clog_unpack.exe -i some_log.clog -k keyfile.bin -o out_log.log
This will decrypt `some_log.clog` with key `keyfile.bin` to `out_log.log` file.

#### blk_minify
Tool for minimizing blk files, good for modders, who want to create mission, but stuck at 512kb file size limit.
It will decrease size to ~ 70% from initial.
For basic usage:

    blk_minify.exe some_mission.blk some_mission_minified.blk
This will minify file from `some_mission.blk` to `some_mission_minified.blk`, without removing any structures from file.
If you want lower size file, you can try additional options:
* `--strip_empty_objects`: will remove empty objects
* `--strip_comment_objects`: will remove comment objects
* `--strip_disabled_objects`: remove disabled objects: the ones, which names start with __
* `--strip_all`: select all options

For example, for minimum size:

    blk_minify.exe --strip_all some_mission.blk some_mission_minified.blk

## Errors?
Try to launch tools from commandline, it should print some error.

##  Would you like to know more?
Read [wiki](https://github.com/klensy/wt-tools/wiki).