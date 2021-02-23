from flask import Blueprint, request, g
from donttrust import DontTrust, Schema, ValidationError
import bcrypt

from . import response, HTTPException
from ..models import User
from ..util.jwt import auth

b = Blueprint(__name__, "users", url_prefix="/api/users")


@b.route("")
def all_users():
    users = User.query.all()
    return response("Users found", dict(users=[user.no_relations_dict() for user in users]))


@b.route("<int:id_>")
def get_user_by_id(id_: int):
    user = User.query.get_or_404(id_, "User not found")
    return response("User found", dict(user=user.dict()))


@b.route("<string:username>")
def get_user_by_username(username: str):
    if username.lower() == "deleted account":
        raise HTTPException("User not found", status=404)
    user = User.query.filter_by(username=username).first_or_404("User not found")
    return response("User found", dict(user=user.dict()))


@b.route("<int:id_>/posts")
def get_posts_of_user_by_id(id_: int):
    user = User.query.get_or_404(id_, "User not found")
    return response("User found", dict(user=user.dict(), posts=[post.dict() for post in user.posts]))


@b.route("<string:username>/posts")
def get_posts_of_user_by_username(username: str):
    if username.lower() == "deleted account":
        raise HTTPException("User not found", status=404)
    user = User.query.filter_by(username=username).first_or_404("User not found")
    return response("User found", dict(user=user.dict(), posts=[post.dict() for post in user.posts]))


@b.route("/account/<string:mode>", methods=["PUT"])
@auth()
def modify_user_account(mode: str):
    if mode == "email":
        trust = DontTrust(email=Schema().email().required(), password=Schema().string().min(8).max(256).required())
        try:
            data = trust.validate(request.json)
        except ValidationError as e:
            raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

        email = data.get("email")
        password = data.get("password")

        user = g.user
        if not bcrypt.checkpw(password.encode(), user.password.encode()):
            raise HTTPException("Invalid password", status=401)

        user.email = email
        user.save()

        return response("Email changed", dict(user=user.dict()))
    if mode == "password":
        trust = DontTrust(password=Schema().string().required(),
                          new_password=Schema().string().required().min(8).max(256),
                          confirm_password=Schema().string().required().min(8).max(256))

        try:
            data = trust.validate(request.json)
        except ValidationError as e:
            raise HTTPException(e.message, dict(field=e.field, value=request.form.get(e.field)))

        p = data["password"]
        n = data["new_password"]
        c = data["confirm_password"]

        if n != c:
            raise HTTPException("Passwords don't match")

        user = g.user

        if not bcrypt.checkpw(p.encode(), user.password.encode()):
            raise HTTPException("Invalid password", status=401)

        user.password = bcrypt.hashpw(n.encode(), bcrypt.gensalt(12)).decode()
        user.save()

        return response("Password changed", dict(user=user.dict()))
    else:
        raise HTTPException("Page not found", status=404)
