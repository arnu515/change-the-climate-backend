from flask import request, g
from functools import wraps
from typing import Optional
from os import getenv as env
from jwt.exceptions import InvalidTokenError, InvalidSignatureError, ExpiredSignatureError
from datetime import datetime, timedelta
import jwt
import redis

from ..routes import HTTPException
from ..models import User

rd = redis.StrictRedis.from_url(env("REDIS_URL", "redis://localhost:6379/0"))


def get_jwt_from_header(raise_ex=True) -> Optional[str]:
    """
    Gets UNVALIDATED token from the header

    :param raise_ex: To raise an exception or not
    :returns: The token (optional)
    :raises: 401 Not Authorized errors with HTTPException (handled internally)
    """
    auth_header: str = request.headers.get("Authorization", request.headers.get("authorization"))
    if not auth_header:
        token: str = request.headers.get("X-Token")
        if token:
            return token
        if raise_ex:
            raise HTTPException("This endpoint requires authorization", status=401)
        else:
            return None

    auth_header_split = auth_header.split()

    if len(auth_header_split) != 2 or auth_header_split[0].lower() != "bearer":
        if raise_ex:
            raise HTTPException("Invalid header format. Format should be Bearer TOKEN", status=401)
        else:
            return None

    token = auth_header_split[1]
    if not token:
        if raise_ex:
            raise HTTPException("Invalid header format. Format should be Bearer TOKEN", status=401)
        else:
            return None
    return token


def get_jwt_identity(token: str, raise_ex=True) -> Optional[dict]:
    """
    Gets the identity of the token

    :param token: The token
    :param raise_ex: Whether to raise an exception or not
    :returns: The token (optional)
    :raises: 401 Not Authorized error with HTTPException (handled internally)
    """

    # Checking if the token was issued by the server / checking for token blacklist
    if not rd.sismember("tokens", token):
        if raise_ex:
            raise HTTPException("The token has expired / is invalid", status=401)
        else:
            return None

    # Getting the identity of the token and checking expiry
    try:
        return jwt.decode(token, env("SECRET", "secret"), algorithms=["HS256"], options={
            "require_exp": True,
            "verify_exp": True
        })
    except (InvalidSignatureError, InvalidTokenError, ExpiredSignatureError):
        if raise_ex:
            raise HTTPException("The token has expired / is invalid", status=401)
        else:
            return None


def create_token(user: User) -> str:
    payload = {"id": user.id, "exp": datetime.utcnow() + timedelta(seconds=int(env("JWT_EXPIRE", str(3600 * 24 * 7))))}
    token = jwt.encode(payload, env("SECRET", "secret"))
    rd.sadd("tokens", token)
    rd.expire("tokens", timedelta(seconds=int(env("JWT_EXPIRE", str(3600 * 24 * 7)))))

    return token


def blacklist_token(token: str):
    rd.srem("tokens", token)
    rd.expire("tokens", timedelta(seconds=int(env("JWT_EXPIRE", str(3600 * 24 * 7)))))


def auth():
    def decorator(func):
        @wraps(func)
        def d(*args, **kwargs):
            token = get_jwt_from_header(False)
            if token is None:
                raise HTTPException("This endpoint requires authorization.", status=401)
            identity = get_jwt_identity(token)
            if "user" in g:
                if g.user.id == identity.get("id"):
                    user = g.user
                else:
                    del g.user
                    user: User = User.query.get(identity.get("id"))
            else:
                user: User = User.query.get(identity.get("id"))
            if user is None:
                raise HTTPException("Invalid token", status=401)
            g.user = user
            g.token = token

            return func(*args, **kwargs)

        return d

    return decorator
