from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Django의 AbstractUser를 상속받는 사용자 정의 모델입니다.
    이 모델은 여러 필드를 정의하여 사용자 정보를 저장합니다.

    - profile_image: 사용자 프로필 사진의 URL 또는 경로
    - nickname: 화면에 표시되는 이름으로, 애플리케이션 내에서 사용자를 식별하는 데 사용
    - name: 사용자의 실제 이름
    - email: 사용자 이메일 주소로, 로그인 시 사용자명으로 사용
    - password: 사용자 비밀번호로, AbstractUser에서 상속받은 기능을 사용
    """

    profile_image = models.TextField()  # 프로필 이미지
    nickname = models.CharField(max_length=24, unique=True)  # 닉네임
    name = models.CharField(max_length=24, default="")  # 사용자 이름
    email = models.EmailField(unique=True, blank=True)  # 이메일

    class Meta:
        db_table = "user"
