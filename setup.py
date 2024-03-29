import os.path
import sys

from cx_Freeze import setup, Executable

src_path = "src/wt_tools/"
packages = ["multiprocessing"]
includes = []
excludes = ["unittest", "pydoc", "construct.examples", "bz2", "lib2to3", "test", "tkinter"]
includefiles = [os.path.join(src_path, "./formats/blk.lark"), os.path.join(src_path, '../../README.md')]
zip_include_packages = ["collections", "construct", "ctypes", "encodings", "json", "logging", "importlib", "formats",
                        "zstandard", "xml", "urllib", "distutils", "click", "pkg_resources", "colorama", "bencodepy",
                        "jsondiff", "requests", "chardet", "idna", "urllib3", "email", "http", "certifi", "multiprocessing"]


blk_unpack = Executable(
    script=os.path.join(src_path, "blk_unpack.py"),
)

clog_unpack = Executable(
    script=os.path.join(src_path, "clog_unpack.py"),
)

ddsx_unpack = Executable(
    script=os.path.join(src_path, "ddsx_unpack.py"),
)

dxp_unpack = Executable(
    script=os.path.join(src_path, "dxp_unpack.py"),
)

vromfs_unpacker = Executable(
    script=os.path.join(src_path, "vromfs_unpacker.py"),
)

wrpl_unpacker = Executable(
    script=os.path.join(src_path, "wrpl_unpacker.py"),
)

blk_minify = Executable(
    script=os.path.join(src_path, "blk_minify.py"),
)

update_differ = Executable(
    script=os.path.join(src_path, "update_differ.py"),
)

update_checker = Executable(
    script=os.path.join(src_path, "update_checker.py"),
)

setup(
    name="wt_tools",
    version="0.2.2.8-dev",
    author='klensy',
    description="War Thunder resource extraction tools",
    url="https://github.com/klensy/wt-tools",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages, "zip_include_packages": zip_include_packages,
                           "path": sys.path + [src_path]}},
    executables=[blk_unpack, clog_unpack, ddsx_unpack, dxp_unpack, vromfs_unpacker, wrpl_unpacker, blk_minify,
                 update_differ, update_checker]
)
