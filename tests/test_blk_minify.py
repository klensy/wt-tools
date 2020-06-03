from src.wt_tools.blk_minify import minify

strip_options = {
    'strip_empty_objects': False,
    'strip_comment_objects': False,
    'strip_disabled_objects': False
}


class TestKeyTypeValueSimples:
    def test_key_type_value_r(self):
        data = "density:r = 0.75"
        expected = "density:r=0.75"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_i(self):
        data = "texSize:i = 256"
        expected = "texSize:i=256"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_t(self):
        data = 'collision:t = "Unigine"'
        expected = 'collision:t="Unigine"'
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_b(self):
        data = "refl:b=yes"
        expected = "refl:b=yes"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_c(self):
        data = "volfogColor:c=234, 237, 240, 255"
        expected = "volfogColor:c=234,237,240,255"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_p2(self):
        data = "fadeK:p2=16, 5.49"
        expected = "fadeK:p2=16,5.49"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_p3(self):
        data = "fadeK:p2=16, 5.49, 0"
        expected = "fadeK:p2=16,5.49,0"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_p4(self):
        data = "fadeK:p2=16, 5.49, 0, 1"
        expected = "fadeK:p2=16,5.49,0,1"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_ip2(self):
        data = "numActiveChunks:ip2=40, 80 "
        expected = "numActiveChunks:ip2=40,80"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_ip3(self):
        data = "size:ip3=32, 16, 16 "
        expected = "size:ip3=32,16,16"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"

    def test_key_type_value_m(self):
        data = "tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] [0.0, 0.0, 1.0] [0.0, 0.0, 0.0]] "
        expected = "tm:m=[[1.0,0.0,0.0][0.0,1.0,0.0][0.0,0.0,1.0][0.0,0.0,0.0]]"
        actual = minify(data, strip_options)
        assert actual == expected, "zzz"


def test_empty_file():
    data = ""
    expected = ""
    actual = minify(data, strip_options)
    assert actual == expected, "zzz"


def test_newlines():
    data = \
    """
    
    """
    expected = ""
    actual = minify(data, strip_options)
    assert actual == expected, "zzz"


def test_empty_object():
    data = "some{}"
    expected = "some{}"
    actual = minify(data, strip_options)
    assert actual == expected, "zzz"


def test_empty_object_with_newlines():
    data = \
    """
    some{
    }
    """
    expected = "some{}"
    actual = minify(data, strip_options)
    assert actual == expected, "zzz"
