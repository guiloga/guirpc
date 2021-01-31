import json

from .domain.contracts import BaseSerializer


class JsonSerializer(BaseSerializer):
    CONTENT_TYPE = 'application/json'
    ENCODING = 'ascii'

    @classmethod
    def serialize(cls, obj: dict) -> str:
        return json.dumps(obj, ensure_ascii=True)

    @classmethod
    def deserialize(cls, obj_str: str) -> dict:
        return json.loads(obj_str)


class TextSerializer(BaseSerializer):
    CONTENT_TYPE = 'text/plain'
    ENCODING = 'ascii'

    @classmethod
    def serialize(cls, obj: str) -> str:
        return str(obj)

    @classmethod
    def deserialize(cls, obj_str: str) -> str:
        return obj_str


class BinarySerializer(BaseSerializer):
    """
    This is a void binary serializer,
    it can be used to pass any object type within a ProxyObject.
    """
    CONTENT_TYPE = None
    ENCODING = None

    @classmethod
    def serialize(cls, obj):
        pass

    @classmethod
    def deserialize(cls, obj_str):
        pass
