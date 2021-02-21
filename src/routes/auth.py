from flask import Blueprint, request, g
from donttrust import DontTrust, Schema, ValidationError
from bcrypt import checkpw, hashpw, gensalt
import re

from . import HTTPException, response
from ..models import User
from ..util import jwt

b = Blueprint("auth", __name__, url_prefix="/api/auth")


@b.route("/user", methods=["GET"])
@jwt.auth()
def create_user():
    return response("Logged in", data=dict(user=g.user.no_relations_dict()))


@b.route("/login", methods=["POST"])
def login():
    trust = DontTrust(email=Schema().email().required(), password=Schema().string().min(8).max(256).required())

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if user is None:
        raise HTTPException(f"User with email {email} was not found.", dict(field="email", value=email))

    if user.is_deleted:
        raise HTTPException("This account belongs to a deleted user", dict(field="email", value=email))

    if user.is_blocked:
        raise HTTPException("This account is banned from this website", dict(field="email", value=email))

    if not checkpw(password.encode(), user.password.encode()):
        raise HTTPException("Invalid password", dict(field="password", value=password))

    token = jwt.create_token(user)

    return response("Logged in", dict(token=token, user=user.no_relations_dict()))


@b.route("/register", methods=["POST"])
def register():
    trust = DontTrust(email=Schema().email().required(), password=Schema().string().min(8).max(256).required(),
                      username=Schema().string().min(4).max(32).regex(r"[\w_]+").flags(re.I))

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    email = data["email"]
    password = data["password"]
    username = data["username"]

    user = User.query.filter_by(email=email).first()
    if user is not None:
        raise HTTPException(f"Email already registered", dict(field="email", value=email))

    user = User.query.filter_by(username=username).first()
    if user is not None:
        raise HTTPException(f"Username taken", dict(field="username", value=username))

    user = User(email=email, username=username, password=hashpw(password.encode(), gensalt(12)).decode())
    user.save()
    token = jwt.create_token(user)

    return response("Registered", dict(token=token, user=user.no_relations_dict()))


@b.route("/logout", methods=["DELETE"])
@jwt.auth()
def logout():
    token = g.token
    user = g.user
    jwt.blacklist_token(token)

    del g.token
    del g.user
    return response("Logged out", dict(user=user.no_relations_dict()))
