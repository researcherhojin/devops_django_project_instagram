import logging
from uuid import uuid4
import os

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Feed, Reply, Like, Bookmark
from user.models import User
from config.settings import MEDIA_ROOT

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class Index(APIView):
    def get(self, request):
        try:
            email = request.session.get("email", None)
            if email is None:
                # 세션에 이메일이 없으면 로그인 페이지로
                return render(request, "user/login.html")

            # 세션에 있는 사용자
            session_user = User.objects.filter(email=email).first()
            if session_user is None:
                # 혹은 DB에 해당 이메일이 없으면 로그인 페이지로
                return render(request, "user/login.html")

            # 모든 피드를 최신순으로 가져오기
            feed_object_list = Feed.objects.all().order_by("-id")
            feed_list = []

            for feed in feed_object_list:
                # 여기서 feed 작성자의 이메일로 사용자 정보 가져올 때
                # 세션의 user와 겹치지 않도록 변수명을 구분
                feed_user = User.objects.filter(email=feed.email).first()
                if not feed_user:
                    # feed.email에 해당하는 사용자가 없으면 스킵
                    continue

                # 댓글 처리
                reply_object_list = Reply.objects.filter(feed_id=feed.id)
                reply_list = []
                for reply in reply_object_list:
                    reply_user = User.objects.filter(email=reply.email).first()
                    if reply_user:
                        reply_list.append(
                            dict(
                                reply_content=reply.reply_content,
                                nickname=reply_user.nickname,
                            )
                        )

                # 좋아요 / 북마크 처리
                like_count = Like.objects.filter(feed_id=feed.id, is_like=True).count()
                is_liked = Like.objects.filter(
                    feed_id=feed.id, email=email, is_like=True
                ).exists()
                is_marked = Bookmark.objects.filter(
                    feed_id=feed.id, email=email, is_marked=True
                ).exists()

                feed_list.append(
                    dict(
                        id=feed.id,
                        image=feed.image,
                        content=feed.content,
                        like_count=like_count,
                        # feed 작성자의 프로필/닉네임
                        profile_image=feed_user.profile_image,
                        nickname=feed_user.nickname,
                        reply_list=reply_list,
                        is_liked=is_liked,
                        is_marked=is_marked,
                    )
                )

            # 최종적으로 템플릿에는
            # - feeds: 모든 피드 정보 (feed 작성자 정보 포함)
            # - user: 현재 로그인한 사용자(세션 사용자)
            return render(
                request,
                "instagram/index.html",
                context=dict(
                    feeds=feed_list,
                    user=session_user,  # ← 중복 없이 session_user 로 넘김
                ),
            )

        except Exception as e:
            logger.error(f"Error in Index view: {str(e)}")
            return HttpResponseRedirect("/user/login")


@method_decorator(csrf_exempt, name="dispatch")
class UploadFeed(APIView):
    def post(self, request):
        try:
            if "file" not in request.FILES:
                return Response({"message": "파일이 필요합니다."}, status=400)

            file = request.FILES["file"]
            content = request.data.get("content")
            email = request.session.get("email")

            if not content or not email:
                return Response({"message": "필수 정보가 누락되었습니다."}, status=400)

            uuid_name = uuid4().hex
            save_path = os.path.join(MEDIA_ROOT, uuid_name)
            with open(save_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            Feed.objects.create(
                content=content,
                image=uuid_name,
                email=email,
            )
            return Response({"message": "업로드 성공"}, status=200)

        except Exception as e:
            logger.error(f"Error in UploadFeed: {str(e)}")
            return Response({"message": "업로드 중 오류가 발생했습니다."}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class Profile(APIView):
    def get(self, request):
        try:
            email = request.session.get("email", None)
            if email is None:
                return HttpResponseRedirect("/user/login/")

            user = User.objects.filter(email=email).first()
            if user is None:
                return HttpResponseRedirect("/user/login/")

            feed_list = Feed.objects.filter(email=email).order_by("-id")
            feed_data = []
            for feed in feed_list:
                like_count = Like.objects.filter(feed_id=feed.id, is_like=True).count()
                reply_count = Reply.objects.filter(feed_id=feed.id).count()
                feed_data.append(
                    {
                        "id": feed.id,
                        "image": feed.image,
                        "content": feed.content,
                        "like_count": like_count,
                        "reply_count": reply_count,
                    }
                )

            like_feed_ids = Like.objects.filter(email=email, is_like=True).values_list(
                "feed_id", flat=True
            )
            like_feed_list = Feed.objects.filter(id__in=like_feed_ids).order_by("-id")
            like_feed_data = []
            for feed in like_feed_list:
                like_count = Like.objects.filter(feed_id=feed.id, is_like=True).count()
                reply_count = Reply.objects.filter(feed_id=feed.id).count()
                like_feed_data.append(
                    {
                        "id": feed.id,
                        "image": feed.image,
                        "content": feed.content,
                        "like_count": like_count,
                        "reply_count": reply_count,
                    }
                )

            bookmark_feed_ids = Bookmark.objects.filter(
                email=email, is_marked=True
            ).values_list("feed_id", flat=True)
            bookmark_feed_list = Feed.objects.filter(id__in=bookmark_feed_ids).order_by(
                "-id"
            )
            bookmark_feed_data = []
            for feed in bookmark_feed_list:
                like_count = Like.objects.filter(feed_id=feed.id, is_like=True).count()
                reply_count = Reply.objects.filter(feed_id=feed.id).count()
                bookmark_feed_data.append(
                    {
                        "id": feed.id,
                        "image": feed.image,
                        "content": feed.content,
                        "like_count": like_count,
                        "reply_count": reply_count,
                    }
                )

            stats = {
                "total_posts": feed_list.count(),
                "total_likes_received": Like.objects.filter(
                    feed_id__in=feed_list.values_list("id", flat=True), is_like=True
                ).count(),
                "total_bookmarks": bookmark_feed_list.count(),
                "total_comments": Reply.objects.filter(
                    feed_id__in=feed_list.values_list("id", flat=True)
                ).count(),
            }

            return render(
                request,
                "content/profile.html",
                context=dict(
                    user=user,
                    feed_list=feed_data,
                    like_feed_list=like_feed_data,
                    bookmark_feed_list=bookmark_feed_data,
                    stats=stats,
                ),
            )
        except Exception as e:
            logger.error(f"Error in Profile view: {str(e)}")
            return HttpResponseRedirect("/user/login/")


@method_decorator(csrf_exempt, name="dispatch")
class UploadReply(APIView):
    def post(self, request):
        try:
            feed_id = request.data.get("feed_id")
            reply_content = request.data.get("reply_content")
            email = request.session.get("email")

            if not feed_id or not reply_content or not email:
                return Response(
                    {"message": "필수 입력값이 누락되었습니다."}, status=400
                )

            if not Feed.objects.filter(id=feed_id).exists():
                return Response({"message": "존재하지 않는 게시물입니다."}, status=404)

            Reply.objects.create(
                feed_id=feed_id, reply_content=reply_content, email=email
            )

            return Response({"message": "댓글이 작성되었습니다."}, status=200)

        except Exception as e:
            logger.error(f"Error in UploadReply: {str(e)}")
            return Response(
                {"message": "댓글 작성 중 오류가 발생했습니다."}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class ToggleLike(APIView):
    def post(self, request):
        try:
            feed_id = request.data.get("feed_id", None)
            email = request.session.get("email", None)

            if not feed_id or not email:
                return Response({"message": "필수 정보가 누락되었습니다."}, status=400)

            like = Like.objects.filter(feed_id=feed_id, email=email).first()
            if like:
                like.is_like = not like.is_like
                like.save()
            else:
                Like.objects.create(feed_id=feed_id, email=email, is_like=True)

            like_count = Like.objects.filter(feed_id=feed_id, is_like=True).count()
            return Response({"like_count": like_count}, status=200)

        except Exception as e:
            logger.error(f"Error in ToggleLike: {str(e)}")
            return Response(
                {"message": "좋아요 처리 중 오류가 발생했습니다."}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class ToggleBookmark(APIView):
    def post(self, request):
        try:
            feed_id = request.data.get("feed_id", None)
            email = request.session.get("email", None)

            if not feed_id or not email:
                return Response({"message": "필수 정보가 누락되었습니다."}, status=400)

            bookmark = Bookmark.objects.filter(feed_id=feed_id, email=email).first()
            if bookmark:
                bookmark.is_marked = not bookmark.is_marked
                bookmark.save()
                is_marked = bookmark.is_marked
            else:
                Bookmark.objects.create(feed_id=feed_id, email=email, is_marked=True)
                is_marked = True

            return Response({"is_marked": is_marked}, status=200)

        except Exception as e:
            logger.error(f"Error in ToggleBookmark: {str(e)}")
            return Response(
                {"message": "북마크 처리 중 오류가 발생했습니다."}, status=500
            )
