from django.contrib import admin
from .models import Feed, Like, Reply, Bookmark


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "content"]  # 목록에서 보여줄 필드 추가
    search_fields = ["email", "content"]  # 검색 기능 추가


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["feed_id", "email", "is_like"]


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ["feed_id", "email", "reply_content"]
    search_fields = ["reply_content"]


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["feed_id", "email", "is_marked"]
