import pytest
import tempfile
import os.path
from src.wt_tools import blk_unpack

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


@pytest.mark.skip(reason="cant find old files now")
class TestOldBlk:
    def test_old_blk_in_strict_blk_mode(self):
        expected_data, result_data = read_and_unpack('camera.old.blk', 'camera.old.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    def test_old_blk_in_json_mode(self):
        expected_data, result_data = read_and_unpack('camera.old.blk', 'camera.old.json.blkx',
                                                     blk_unpack.BLK.output_type['json'])
        assert result_data == expected_data, "Wrong output blkx"


class TestNewBlk:
    def test_new_blk_in_strict_blk_mode(self):
        expected_data, result_data = read_and_unpack('camera.new.blk', 'camera.new.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    def test_new_blk_in_json_mode(self):
        expected_data, result_data = read_and_unpack('camera.new.blk', 'camera.new.json.blkx',
                                                     blk_unpack.BLK.output_type['json'])
        assert result_data == expected_data, "Wrong output blkx"

    def test_new_blk_with_big_num_of_units_and_subunits(self):
        """
        To trigger units_length_type = 0x81 and
        sub_units_block_type = 0x80
        """
        expected_data, result_data = read_and_unpack('gui.blk', 'gui.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    def test_new_blk_with_zero_subunits(self):
        """
        To trigger sub_units_block_length == 0 and
        total_sub_units = 0
        """
        expected_data, result_data = read_and_unpack('situationconst.blk', 'situationconst.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    @pytest.mark.skip(reason="cant find files now")
    def test_new_blk_with_spaces_in_key(self):
        """
        Check case, when key contain spaces:
            "random from":i=0
        and check type_list[int]
        """
        expected_data, result_data = read_and_unpack('assaults_template.blk', 'assaults_template.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    @pytest.mark.skip(reason="cant find files now")
    def test_new_blk_with_array_type(self):
        """
        Check type_list[m4x3f]
        """
        expected_data, result_data = read_and_unpack('bzt_part.blk', 'bzt_part.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    @pytest.mark.skip(reason="cant find files now")
    def test_new_blk_with_big_unit_length(self):
        """
        Check long unit values strings:
            unit_length >= 0x80:
        """
        expected_data, result_data = read_and_unpack('ct_test.blk', 'ct_test.blkx',
                                                     blk_unpack.BLK.output_type['strict_blk'])
        assert result_data == expected_data, "Wrong output blkx"

    @pytest.mark.skip(reason="cant find files now")
    def test_new_blk_with_utf8_strings(self):
        """
        Check with russian comment lines
        """
        expected_data, result_data = read_and_unpack('lpt_part.blk', 'lpt_part.blkx',
                                                     blk_unpack.BLK.output_type['json'])
        assert result_data == expected_data, "Wrong output blkx"

