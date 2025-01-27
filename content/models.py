from django.db import models


class Feed(models.Model):
    id = models.AutoField(primary_key=True)  # 게시물의 고유 ID
    content = models.TextField()  # 게시물 내용
    image = models.TextField()  # 이미지 경로
    email = models.EmailField(default="")  # 작성자 이메일


class Like(models.Model):
    feed_id = models.IntegerField(default=0)  # 좋아요가 달린 게시물 ID
    email = models.EmailField(default="")  # 좋아요를 누른 사용자
    is_like = models.BooleanField(default=True)  # 좋아요 상태


class Reply(models.Model):
    feed_id = models.IntegerField(default=0)  # 댓글이 달린 게시물 ID
    email = models.EmailField(default="")  # 댓글 작성자
    reply_content = models.TextField()  # 댓글 내용


class Bookmark(models.Model):
    feed_id = models.IntegerField(default=0)  # 북마크된 게시물 ID
    email = models.EmailField(default="")  # 북마크한 사용자
    is_marked = models.BooleanField(default=True)  # 북마크 상태
