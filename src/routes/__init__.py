from flask import make_response, jsonify
from typing import Any


def response(message: str, data: Any = None, status=200, success=True):
    if data is None:
        data = dict()
    return make_response(jsonify(dict(message=message, data=data, success=success)), status)


class HTTPException(Exception):
    message: str
    data: Any
    status: int
    success: bool

    def __init__(self, message: str, data: Any = None, status=400, success=False):
        if data is None:
            data = dict()
        self.message = message
        self.status = status
        self.success = success
        self.data = data

    @property
    def response(self):
        return make_response(jsonify(dict(message=self.message, data=self.data, success=self.success)), self.status)
