import unittest
import tempfile
import os.path
import blk_unpack

test_data_folder = "data_for_tests"
test_data_output_folder = os.path.join(test_data_folder, 'out')


def read_and_unpack(blk_file, blkx_file, out_type):
    """Prepare files: unpack and return"""
    with open(os.path.join(test_data_folder, blk_file), 'rb') as f:
        data = f.read()
    blk = blk_unpack.BLK(data)
    tempfile_path = tempfile.mkstemp(prefix=blkx_file, dir=test_data_output_folder)
    with open(tempfile_path[1], 'w') as f:
        f.write(blk.unpack(out_type))

    expected_data = open(os.path.join(test_data_folder, blkx_file), 'r').read()
    result_data = open(tempfile_path[1], 'r').read()
    return expected_data, result_data


class BLKTestsOld(unittest.TestCase):
    def test_old_blk_in_strict_blk_mode(self):
        expected_data, result_data = read_and_unpack('camera.old.blk', 'camera.old.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        self.assertEqual(result_data, expected_data, msg="Wrong output blkx")

    def test_old_blk_in_json_mode(self):
        expected_data, result_data = read_and_unpack('camera.old.blk', 'camera.old.json.blkx',
                                                     blk_unpack.BLK.output_type['json'])
        self.assertEqual(result_data, expected_data, msg="Wrong output blkx")


class BLKTestsNew(unittest.TestCase):
    def test_new_blk_in_strict_blk_mode(self):
        expected_data, result_data = read_and_unpack('camera.new.blk', 'camera.new.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        self.assertEqual(result_data, expected_data, msg="Wrong output blkx")

    def test_new_blk_in_json_mode(self):
        expected_data, result_data = read_and_unpack('camera.new.blk', 'camera.new.json.blkx',
                                                     blk_unpack.BLK.output_type['json'])
        self.assertEqual(result_data, expected_data, msg="Wrong output blkx")

if __name__ == '__main__':
    unittest.main()
