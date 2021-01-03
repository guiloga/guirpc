from guilogacore_rpc.amqp.domain.objects import ProxyResponse
from guilogacore_rpc.amqp.decorators import register_faas
from guilogacore_rpc.amqp.serializers import JsonSerializer, TextSerializer


@register_faas(req_sz=JsonSerializer, resp_sz=JsonSerializer)
def foobar_sum(x_request):
    """
    This is an example of a service callback implementation with :class:`JsonSerializer`
    as a request and response serializer types.
    A :class:`JsonSerializer` encapsulates content as an object of type :class:`dict`.

    :param x_request: Represents a requested object.
        Evaluate it by calling the 'content' property.
        .e.g {'foo': 1, 'bar': 2}
    :type x_request: ProxyRequest
    :returns: A response object.
    :rtype: ProxyResponse
    """
    try:
        resp_obj = {'result': x_request.object['foo'] + x_request.object['bar']}
        response = ProxyResponse(200, resp_obj)
    except Exception as err:
        response = ProxyResponse(
            500,
            "ServerError: An unexpected error occurred " +
            f"while processing the request message.\n {err}")
    return response


@register_faas(req_sz=TextSerializer, resp_sz=TextSerializer)
def foobar_count(x_request):
    """
    This is an example of a service callback implementation with :class:`TextSerializer`
    as a request and response serializer types.
    A :class:`TextSerializer` encapsulates content as an object of type :class:`str`.

    :param x_request: Represents a requested object.
        Evaluate it by calling the 'content' property.
        .e.g 'my name is Foo Bar and I love foobars'
    :type x_request: ProxyRequest
    :returns: A response object.
    :rtype: ProxyResponse
    """
    try:
        normalized = x_request.object.lower()
        count = len(normalized.split('foo')) - 1
        count += len(normalized.split('bar')) - 1

        response = ProxyResponse(200, str(count))
    except Exception as err:
        response = ProxyResponse(
            500,
            "ServerError: An unexpected error occurred " +
            f"while processing the request message.\n {err}")

    return response
