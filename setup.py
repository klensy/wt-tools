from cx_Freeze import setup, Executable

packages = ["construct"]
includes = []
excludes = []
includefiles = []

executable = Executable(
    script="vromfs_unpacker.py",
    compress=True,
)

setup(
    name="vromfs_unpacker",
    version="0.2.0.1",
    author='klensy',
    description="description",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages}},
    executables=[executable]
)
