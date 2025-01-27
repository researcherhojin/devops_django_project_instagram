from django.urls import path
from .views import Login, Join, LogOut, UploadProfile  # 수정

urlpatterns = [
    path("login/", Login.as_view()),
    path("join/", Join.as_view()),
    path("logout/", LogOut.as_view()),
    path("profile/upload", UploadProfile.as_view()),  # 추가
]
