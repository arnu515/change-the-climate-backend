from flask import Blueprint, request, g
from flask_sqlalchemy import Pagination
from donttrust import DontTrust, ValidationError, Schema

from . import response, HTTPException
from ..models import Post, Like
from ..util.jwt import auth

b = Blueprint("posts", __name__, url_prefix="/api/posts")


@b.route("", methods=["GET"])
def all_posts():
    try:
        page = int(request.args.get("page") or "1")
        per_page = int(request.args.get("per_page") or "10")
    except (TypeError, ValueError):
        page = 1
        per_page = 10
    posts: Pagination = Post.query.order_by(Post.created_at.desc()).filter_by(is_deleted=False).paginate(page, per_page)
    return response("Posts found",
                    dict(posts=[p.dict() for p in posts.items], pages=posts.pages, has_next=posts.has_next, has_prev=posts.has_prev,
                         page=posts.page))


@b.route("<string:id_>", methods=["GET"])
def one_post(id_: str):
    post: Post = Post.query.get_or_404(id_, "Post not found")
    return response("Post found", dict(post=post.dict()))


@b.route("", methods=["POST"])
@auth()
def create_post():
    user = g.user
    trust = DontTrust(content=Schema().string().required())

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    content = data["content"]

    post = Post(content=content, user_id=user.id)
    post.save()

    return response("Created new post", dict(post=post.dict()))


@b.route("<string:id_>", methods=["PUT"])
@auth()
def update(id_: str):
    post = Post.query.get_or_404(id_, "Post not found")
    user = g.user
    if post.user.id != user.id:
        raise HTTPException("You don't have permission to do that", status=403)

    trust = DontTrust(content=Schema().string().required())

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    content = data["content"]
    post.content = content
    post.save()

    return response("Post updated", dict(post=post.dict()))


@b.route("<string:id_>", methods=["DELETE"])
@auth()
def delete_post(id_: str):
    post = Post.query.get_or_404(id_, "Post not found")
    user = g.user
    if post.user.id != user.id:
        raise HTTPException("You don't have permission to do that", status=403)

    post.is_deleted = True
    post.save()
    return response("Post deleted", dict(post=post.dict()))


@b.route("<string:id_>/like", methods=["PUT"])
@auth()
def like_unlike(id_: str):
    post = Post.query.get_or_404(id_, "Post not found")
    if post.is_deleted:
        raise HTTPException("You cannot like/unlike deleted posts", dict(post=post.dict()))
    user = g.user
    for like in post.likes:
        if like.user_id == user.id:
            like.delete()
            return response("Post unliked", dict(post=post.dict(), like=False))
    like = Like(user_id=user.id, post_id=post.id)
    like.save()

    return response("Post liked", dict(post=post.dict(), like=True))
