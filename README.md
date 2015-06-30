## War Thunder resource extraction tools

Python scripts, that help you extract resources from game: fonts, textures, FM/DM of tanks and planes, parameters of cannons and machine guns, and other interesting stuff.

## Installation
1. Download latest 2.7.* python from [here](https://www.python.org/downloads/), install it.
2. Add python path to env variables, see [description](https://docs.python.org/2/using/windows.html#excursus-setting-environment-variables), (optional).
3. Download scripts ("Download ZIP" button), extract somewhere.
4. Run scripts from console, as described lower.

### Or

Download compiled files (exe files, compressed in wt-tools.rar) from [here](https://github.com/klensy/wt-tools/releases), **no python** required.  
Command-line using the same as for python scripts, except you should write `vromfs_unpack some_file.vromfs.bin`, not `python vromfs_unpack.py some_file.vromfs.bin` (for other scripts too).

## Usage

    python vromfs_unpack.py somefile.vromfs.bin
Files will be extracted to `somefile.vromfs.bin_u` folder.

    python dxp_unpack.py somefile.dxp.bin
Files will be extracted to `somefile.dxp.bin_u` folder, *.ddsx files inside.

    python ddsx_unpack.py somefile.ddsx
File will be extracted to `somefile.dds`, not *all* files will work correct.

    python blk_unpack.py somefile.blk
File will be extracted to `somefile.blkx`, this type of file contains settings.

### Or if you use *.exe file scripts

Just drag'n'drop wt files onto exe script files.


##  Would you like to know more?
Read [wiki](https://github.com/klensy/wt-tools/wiki).