from flask import Blueprint, request, g
from donttrust import DontTrust, ValidationError, Schema

from . import response, HTTPException
from ..models import Post, Comment
from ..util.jwt import auth

b = Blueprint("comments", __name__, url_prefix="/api/comments")


@b.route("<string:post_id>", methods=["GET"])
def all_comments_of_post(post_id: str):
    post = Post.query.get_or_404(post_id, "Post not found")
    return response("Comments found", dict(comments=[c.dict() for c in post.comments]))


@b.route("<int:comment_id>", methods=["GET"])
def get_comment_by_id(comment_id: int):
    comment = Comment.query.get_or_404(comment_id, "Comment not found")
    return response("Comment found", dict(comment=comment.dict()))


@b.route("<string:post_id>", methods=["POST"])
@auth()
def add_comment(post_id: str):
    post = Post.query.get_or_404(post_id, "Post not found")
    user = g.user
    trust = DontTrust(content=Schema().string().required())

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    content = data["content"]

    comment = Comment(content=content, user_id=user.id, post_id=post.id)
    comment.save()

    return response("Comment created", dict(comment=comment.dict()))


@b.route("<int:comment_id>", methods=["PUT"])
@auth()
def update_comment(comment_id: int):
    comment = Comment.query.get_or_404(comment_id, "Comment not found")
    user = g.user

    if comment.user.id != user.id:
        raise HTTPException("You don't have permission to do that!", status=403)

    trust = DontTrust(content=Schema().string().required())

    try:
        data = trust.validate(request.json)
    except ValidationError as e:
        raise HTTPException(e.message, dict(field=e.field, value=request.json.get(e.field)))

    content = data["content"]

    comment.content = content
    comment.save()

    return response("Comment updated", dict(comment=comment.dict()))


@b.route("<int:comment_id>", methods=["DELETE"])
@auth()
def delete_comment(comment_id: int):
    comment = Comment.query.get_or_404(comment_id, "Comment not found")
    user = g.user

    if comment.user.id != user.id:
        raise HTTPException("You don't have permission to do that!", status=403)

    comment.delete()

    return response("Comment deleted", dict(comment=comment.no_relations_dict()))
