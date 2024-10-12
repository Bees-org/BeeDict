import re
import zlib
from struct import pack, unpack


def _unescape_entities(text):
    """
    unescape offending tags < > " &
    """
    text = text.replace(b'&lt;', b'<')
    text = text.replace(b'&gt;', b'>')
    text = text.replace(b'&quot;', b'"')
    text = text.replace(b'&amp;', b'&')
    return text


def _decode_header_string(bytes):
    if bytes[-2:] == b'\x00\x00':
        return bytes[:-2].decode("utf-16").encode("utf-8")
    else:
        return bytes[:-1]


class MDict(object):
    """
    MDict is a dictionary that allows you to access and manipulate dictionaries.
    """

    def __init__(self, fname, encoding="", passcode=None):
        self._fname = fname
        self._encoding = encoding.upper()
        self._encrypt_key = None

        self._read_header()

    def _parse_header(self, header):
        """
        extract attributes from <Dict attr="value" ... >
        """
        taglist = re.findall(rb'(\w+)="(.*?)"', header, re.DOTALL)
        tagdict = {}
        for key, value in taglist:
            tagdict[key] = _unescape_entities(value)
        return tagdict

    def _read_header(self):
        """
        Read the header from the file header.
        Header of MDict:
        size of header    adler32 checksum
        +--+--+--+--+     +--+--+--+--+
        |  |  |  |  | --  |  |  |  |  |
        +--+--+--+--+     +--+--+--+--+
        integer           integer
        :return:
        """
        with open(self._fname, 'rb') as f:
            header_size = unpack(">I", f.read(4))[0]
            header_text = _decode_header_string(f.read(header_size))
            adler32 = unpack("<I", f.read(4))[0]
            self._key_block_offset = f.tell()
            header_tag = self._parse_header(header_text)


if __name__ == '__main__':
    mdict = MDict('../mdict/牛津高阶（第10版 英汉双解） V5_0.mdx')
