from guirpc.amqp.decorators import register_faas
from guirpc.amqp.domain import ProxyResponse
from guirpc.amqp.serializers import JsonSerializer, TextSerializer


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
    sum_body = {**x_request.object}

    is_valid, err_msg = _validate_foobar_sum(sum_body)
    if not is_valid:
        return ProxyResponse(400, error_message=f'[ValidationError] {err_msg}')

    try:
        resp_obj = {'result': sum_body['foo'] + sum_body['bar']}
        response = ProxyResponse(200, object_=resp_obj)
    except Exception as err:
        response = ProxyResponse(
            500, error_message="[ServerError] An unexpected error occurred "
                               f"while processing the request message: "
                               f"'{err.__class__.__name__} -> {err}'")
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
    normalized = x_request.object.lower()

    is_valid, err_msg = _validate_foobar_count(normalized)
    if not is_valid:
        return ProxyResponse(400, error_message=f'[ValidationError] {err_msg}')

    try:
        count = len(normalized.split('foo')) - 1
        count += len(normalized.split('bar')) - 1

        response = ProxyResponse(200, object_=str(count))
    except Exception as err:
        response = ProxyResponse(
            500, error_message="[ServerError] An unexpected error occurred "
                               f"while processing the request message: "
                               f"'{err.__class__.__name__} -> {err}'")
    return response


def _validate_foobar_sum(object_: dict):
    if 'foo' not in object_.keys():
        return False, "'foo' field is required."
    elif 'bar' not in object_.keys():
        return False, "'bar' field is required."
    elif not isinstance(object_['foo'], int):
        return False, "'foo' field is not an integer."
    elif not isinstance(object_['bar'], int):
        return False, "'foo' is not an integer."
    else:
        return True, None


def _validate_foobar_count(object_: str):
    if len(object_) < 10:
        return False, 'Invalid sentence: the minimun required length is 10.'
    else:
        return True, None
