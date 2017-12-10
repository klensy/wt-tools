from cx_Freeze import setup, Executable

packages = ["construct", "zstd", "pylzma"]
includes = []
excludes = ["socket", "unittest", "http", "email", "pydoc", "construct.examples"]
includefiles = []

blk_unpack = Executable(
    script="blk_unpack.py",
)

clog_unpack = Executable(
    script="clog_unpack.py",
)

ddsx_unpack = Executable(
    script="ddsx_unpack.py",
)

dxp_unpack = Executable(
    script="dxp_unpack.py",
)

vromfs_unpacker = Executable(
    script="vromfs_unpacker.py",
)

wrpl_unpacker = Executable(
    script="wrpl_unpacker.py",
)

setup(
    name="wt-tools",
    version="0.2.1-dev",
    author='klensy',
    description="War Thunder resource extraction tools",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages}},
    executables=[blk_unpack, clog_unpack, ddsx_unpack, dxp_unpack, vromfs_unpacker, wrpl_unpacker]
)
