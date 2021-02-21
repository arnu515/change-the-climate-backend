from datetime import datetime
from .util import generate_string

from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(2048))
    password = db.Column(db.String(256))
    username = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    # Possible values: "member", "admin"
    role = db.Column(db.String(16), default="member")
    is_blocked = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        for post in self.posts:
            post.delete()
        db.session.delete(self)
        db.session.commit()

    def no_relations_dict(self):
        return dict(id=self.id, email=self.email, username=self.username, created_at=self.created_at,
                    updated_at=self.updated_at, role=self.role, is_deleted=self.is_deleted, is_blocked=self.is_blocked)

    def dict(self):
        return {**self.no_relations_dict(), "posts": [p.no_relations_dict() for p in self.posts],
                "comments": [c.no_relations_dict() for c in self.comments]}


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String(64), primary_key=True, default=lambda: generate_string(64))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    is_deleted = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="posts", foreign_keys=user_id)

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        for comment in self.comments:
            comment.delete()
        db.session.delete(self)
        db.session.commit()

    def no_relations_dict(self):
        return dict(id=self.id, content=self.content, created_at=self.created_at, updated_at=self.updated_at,
                    is_deleted=self.is_deleted, likes=[like.no_relations_dict() for like in self.likes])

    def dict(self):
        return {**self.no_relations_dict(), "user": self.user.no_relations_dict(),
                "comments": [c.no_relations_dict() for c in self.comments]}


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="comments", foreign_keys=user_id)

    post_id = db.Column(db.String(64), db.ForeignKey(Post.id))
    post = db.relationship(Post, backref="comments", foreign_keys=post_id)

    def save(self):
        self.updated_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.user = None
        self.post = None
        self.save()
        db.session.delete(self)
        db.session.commit()

    def no_relations_dict(self):
        return dict(id=self.id, content=self.content, created_at=self.created_at,
                    updated_at=self.updated_at)

    def dict(self):
        return {**self.no_relations_dict(), "user": self.user.no_relations_dict(),
                "post": self.post.no_relations_dict()}


class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, backref="likes", foreign_keys=user_id)

    post_id = db.Column(db.String(64), db.ForeignKey(Post.id))
    post = db.relationship(Post, backref="likes", foreign_keys=post_id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        self.user = None
        self.post = None
        self.save()
        db.session.delete(self)
        db.session.commit()

    def no_relations_dict(self):
        return dict(id=self.id, user_id=self.user_id, post_id=self.post_id)
