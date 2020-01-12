from marshmallow import Schema
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

FAILURE = {'status': 'failure'}
SUCCESS = {'status': 'success'}


# Map dict to dereferencable object
class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class EmptySchema(Schema):
    pass


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


def is_integer(decimal):
    return decimal % 1 == 0


def log_exception(e, tb=None):
    context = {'status': FAILURE}
    # TODO log
    context.update({'exception': str(e)})
    if tb and DEBUG:
        print(tb)
        context.update({'tb': tb})

    return Response(context, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def log_validation_errors(errors):
    # TODO log
    if DEBUG:
        print(errors)
    context = {'status': FAILURE}
    context.update({'errors': errors})
    print(context)
    return Response(context, status=status.HTTP_400_BAD_REQUEST)


def illegal_action(message, data=None):
    context = {'status': FAILURE}
    context.update({'message': message})
    if data:
        context.update({'result': data})
    return Response(context, status=status.HTTP_403_FORBIDDEN)


def failed_parse(message, data=None):
    context = {'status': FAILURE}
    context.update({'message': message})
    if data:
        context.update({'result': data})
    return Response(context, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


def success_action(data, status=status.HTTP_200_OK):
    return Response(
        {'status': 'success',
         'result': data,
         },
        status=status)


def unimplemented_action(data, status=status.HTTP_200_OK):
    return Response(
        {'status': 'under-construction',
         'result': data,
         },
        status=status)


def full_media_url(request):
    return get_base(request) + MEDIA_URL


def get_base(request):
    if request.is_secure():
        return "https://" + request.get_host()
    else:
        return "http://" + request.get_host()
