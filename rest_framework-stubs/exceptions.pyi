from collections.abc import Sequence
from typing import Any, TypedDict, overload

from typing_extensions import TypeAlias

from django.http import HttpRequest, JsonResponse
from django.utils.functional import _StrOrPromise
from rest_framework.renderers import BaseRenderer
from rest_framework.request import Request
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

_Detail: TypeAlias = _StrOrPromise | list[_Detail] | dict[Any, _Detail] | ErrorDetail

@overload
def _get_error_details(data: ReturnList[_Detail], default_code: str | None = ...) -> ReturnList[_Detail]: ...
@overload
def _get_error_details(data: list[_Detail] | tuple[_Detail, ...], default_code: str | None = ...) -> list[_Detail]: ...
@overload
def _get_error_details(data: ReturnDict[Any, _Detail], default_code: str | None = ...) -> ReturnDict[Any, _Detail]: ...
@overload
def _get_error_details(data: dict[Any, _Detail], default_code: str | None = ...) -> dict[Any, _Detail]: ...
@overload
def _get_error_details(data: _StrOrPromise, default_code: str | None = ...) -> ErrorDetail: ...

_DetailData: TypeAlias = list[_DetailData] | dict[Any, _DetailData] | ErrorDetail

@overload
def _get_codes(detail: list[_DetailData | int]) -> list[_DetailData | int]: ...
@overload
def _get_codes(detail: dict[Any, _DetailData | int]) -> dict[Any, _DetailData | int]: ...
@overload
def _get_codes(detail: ErrorDetail) -> int: ...

class _DetailDict(TypedDict):
    message: ErrorDetail
    code: int

@overload
def _get_full_details(detail: list[_DetailData | _DetailDict]) -> list[_DetailData | _DetailDict]: ...
@overload
def _get_full_details(detail: dict[Any, _DetailData | _DetailDict]) -> dict[Any, _DetailData | _DetailDict]: ...
@overload
def _get_full_details(detail: ErrorDetail) -> _DetailDict: ...

class ErrorDetail(str):
    code: str | None
    def __new__(cls, string: str, code: str | None = ...): ...

class APIException(Exception):
    status_code: int
    default_detail: _Detail
    default_code: str

    detail: _DetailData

    def __init__(self, detail: _Detail | None = ..., code: str | None = ...) -> None: ...
    def get_codes(self) -> Any: ...
    def get_full_details(self) -> Any: ...

class ValidationError(APIException):
    detail: list[_DetailData] | dict[Any, _DetailData]

    def __init__(self, detail: _Detail | tuple[_Detail, ...] | None = ..., code: str | None = ...) -> None: ...

class ParseError(APIException): ...
class AuthenticationFailed(APIException): ...
class NotAuthenticated(APIException): ...
class PermissionDenied(APIException): ...
class NotFound(APIException): ...

class MethodNotAllowed(APIException):
    def __init__(self, method: str, detail: _Detail | None = ..., code: str | None = ...) -> None: ...

class NotAcceptable(APIException):
    available_renderers: Sequence[BaseRenderer] | None
    def __init__(
        self,
        detail: _Detail | None = ...,
        code: str | None = ...,
        available_renderers: Sequence[BaseRenderer] | None = ...,
    ) -> None: ...

class UnsupportedMediaType(APIException):
    def __init__(self, media_type: str, detail: _Detail | None = ..., code: str | None = ...) -> None: ...

class Throttled(APIException):
    extra_detail_singular: str
    extra_detail_plural: str
    def __init__(self, wait: float | None = ..., detail: _Detail | None = ..., code: str | None = ...): ...

def server_error(request: HttpRequest | Request, *args: Any, **kwargs: Any) -> JsonResponse: ...
def bad_request(request: HttpRequest | Request, exception: Exception, *args: Any, **kwargs: Any) -> JsonResponse: ...
