from cx_Freeze import setup, Executable
import sys

src_path = "src/wt_tools/"
packages = []
includes = []
excludes = ["socket", "unittest", "http", "email", "pydoc", "construct.examples", "bz2"]
includefiles = [src_path + "/blk.lark"]
zip_include_packages = ["collections", "construct", "ctypes", "encodings", "json", "logging", "importlib", "formats",
                        "zstandard", "xml", "urllib", "distutils", "click", "pkg_resources"]


blk_unpack = Executable(
    script=src_path + "blk_unpack.py",
)

clog_unpack = Executable(
    script=src_path + "clog_unpack.py",
)

ddsx_unpack = Executable(
    script=src_path + "ddsx_unpack.py",
)

dxp_unpack = Executable(
    script=src_path + "dxp_unpack.py",
)

vromfs_unpacker = Executable(
    script=src_path + "vromfs_unpacker.py",
)

wrpl_unpacker = Executable(
    script=src_path + "wrpl_unpacker.py",
)

blk_minify = Executable(
    script=src_path + "blk_minify.py",
)

setup(
    name="wt_tools",
    version="0.2.2.5-dev",
    author='klensy',
    description="War Thunder resource extraction tools",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages, "zip_include_packages": zip_include_packages,
                           "path": sys.path + [src_path]}},
    executables=[blk_unpack, clog_unpack, ddsx_unpack, dxp_unpack, vromfs_unpacker, wrpl_unpacker, blk_minify]
)
