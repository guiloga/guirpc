import base64


class StringEncoder:
    """
    String to Bytes encoder/decoder.
    """

    @classmethod
    def encode(cls, stream_str: str, codec='ascii') -> bytes:
        return stream_str.encode(encoding=codec)

    @classmethod
    def decode(cls, bytes_obj: bytes, codec='ascii') -> str:
        return bytes_obj.decode(encoding=codec)


class BytesEncoder:
    """
    Bytes encoder/decoder.
    This applies binary transformations from a bytes-like object to a bytes mapping with codec base64.
    """
    # TODO: Maybe extend this class allowing other type of binary transformations.
    BINARY_CODECS = ('base64',)

    @classmethod
    def encode(cls, stream_bytes: bytes, binary_codec=BINARY_CODECS[0]) -> bytes:
        _encoder = getattr(cls, f'enc_{binary_codec}')
        return _encoder(stream_bytes)

    @classmethod
    def decode(cls, bytes_obj: bytes, binary_codec=BINARY_CODECS[0]) -> bytes:
        _decoder = getattr(cls, f'dec_{binary_codec}')
        return _decoder(bytes_obj)

    @staticmethod
    def enc_base64(bytes_: bytes):
        return base64.encodebytes(bytes_)

    @staticmethod
    def dec_base64(bytes_: bytes):
        return base64.decodebytes(bytes_)
