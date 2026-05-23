from typing import Any


def success_response(data: Any = None, **metadata: Any) -> dict:
    response = {
        "success": True,
        "data": data,
    }

    if metadata:
        response["metadata"] = metadata

    return response


def error_response(error: Any, **metadata: Any) -> dict:
    response = {
        "success": False,
        "error": error,
        "detail": error,
    }

    if metadata:
        response["metadata"] = metadata

    return response
