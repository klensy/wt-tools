## War Thunder resource extraction tools

Python scripts, that help you extract various resources from game: pictures, settings.

## Installation
Just download and run with python 2.7.

## Usage

    python vromfs_unpack.py somefile.vromfs.bin
Files will be extracted to `somefile.vromfs.bin_u` folder.

    python dxp_unpack.py somefile.dxp.bin
Files will be extracted to `somefile.dxp.bin_u` folder, *.ddsx files inside.

    python ddsx_unpack.py somefile.ddsx
File will be extracted to `somefile.dds`, not *all* files will work correct.

    python blk_unpack.py somefile.blk
File will be extracted to `somefile.blkx`, this type of file contains settings.