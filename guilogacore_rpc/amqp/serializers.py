from .domain.contracts import BaseSerializer
from .domain.objects import ProxyResponse

import json


class TextSerializer(BaseSerializer):
    CONTENT_TYPE = 'text/plain'
    ENCODING = 'ascii'

    @classmethod
    def serialize(cls, obj: ProxyResponse) -> str:
        return str(obj)

    @classmethod
    def deserialize(cls, obj_str: str) -> object:
        return obj_str


class JsonSerializer(BaseSerializer):
    CONTENT_TYPE = 'application/json'
    ENCODING = 'ascii'

    @classmethod
    def serialize(cls, obj: ProxyResponse) -> str:
        return json.dumps(obj, ensure_ascii=True)

    @classmethod
    def deserialize(cls, obj_str: str) -> object:
        return json.loads(obj_str)
