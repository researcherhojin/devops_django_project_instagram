from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password  # 수정
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt  # 403 Forbidden Error Sol
from django.utils.decorators import method_decorator  # 403 Forbidden Error Sol

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User

import os
from uuid import uuid4

from config.settings import MEDIA_ROOT


@method_decorator(csrf_exempt, name="dispatch")  # 403 Forbidden Error Sol
class Login(APIView):
    def get(self, request):
        return render(request, "user/login.html")

    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if email is None:
            return Response(status=500, data=dict(message="이메일을 입력해주세요"))

        if password is None:
            return Response(status=500, data=dict(message="비밀번호를 입력해주세요"))

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(
                status=500, data=dict(message="회원 정보가 잘못되었습니다.")
            )

        if check_password(password, user.password) is False:
            return Response(
                status=500, data=dict(message="회원 정보가 잘못되었습니다.")
            )

        # 로그인 성공 시 세션에 상태 저장
        request.session["loginCheck"] = True
        request.session["email"] = user.email

        return Response(status=200, data=dict(message="로그인에 성공했습니다."))


@method_decorator(csrf_exempt, name="dispatch")  # 403 Forbidden Error Sol
class Join(APIView):
    def get(self, request):
        return render(request, "user/join.html")

    def post(self, request):
        email = request.data.get("email", None)
        nickname = request.data.get("nickname", None)
        name = request.data.get("name", None)
        password = request.data.get("password", None)

        try:
            User.objects.create(
                email=email,
                nickname=nickname,
                name=name,
                password=make_password(password),
                profile_image="default.png",
                username=email,  # username 필드에 email 값 할당
            )
            return Response(
                {"message": "회원가입이 성공적으로 완료되었습니다."},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError as e:
            if "UNIQUE constraint failed: user.email" in str(e):
                return Response(
                    {"message": "이미 존재하는 이메일 주소입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif "UNIQUE constraint failed: user.nickname" in str(e):
                return Response(
                    {"message": "이미 존재하는 닉네임입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {"message": "회원가입 중 오류가 발생했습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception:
            return Response(
                {"message": "회원가입 중 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")  # 403 Forbidden Error Sol
class LogOut(APIView):
    def get(self, request):
        # 사용자의 세션 정보를 삭제
        request.session.flush()
        return render(request, "user/login.html")


# 추가
@method_decorator(csrf_exempt, name="dispatch")
class UploadProfile(APIView):
    def post(self, request):
        try:
            file = request.FILES["file"]
            email = request.data.get("email")

            # 파일 저장
            uuid_name = uuid4().hex
            save_path = os.path.join(MEDIA_ROOT, uuid_name)
            with open(save_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # 사용자 프로필 업데이트
            user = User.objects.get(email=email)
            user.profile_image = uuid_name
            user.save()

            return Response(status=200)

        except KeyError:
            return Response(status=400)
        except User.DoesNotExist:
            return Response(status=404)
