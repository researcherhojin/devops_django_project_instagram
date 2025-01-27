# Devops_Django_Project_Instagram

이 프로젝트는 Django 웹 프레임워크를 사용하여 만든 Instagram Clone Coding 결과물입니다.

## 설치 방법

1. Python 가상환경 생성하기:

    ```bash
    conda create -n instagram_env python=3.10
    conda activate instagram_env

    ```

2. 필요한 패키지 설치하기

    ```bash
    pip install -r requirements.txt

    ```

3. 데이터베이스 설정하기

    ```bash
    python manage.py migrate

    ```

4. 개발 서버 실행하기

    ```bash
    python manage.py runserver

    ```

## 주요 기능

1. 사용자 인증 (로그인/회원가입)
2. 게시물 작성 및 수정
3. 댓글 작성
4. 프로필 관리

## 필요한 환경

-   Python 3.10 이상
-   Django 5.x 이상
-   `requirements.txt` 파일에 명시된 Python 패키지
