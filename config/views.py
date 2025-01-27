from django.shortcuts import render
from rest_framework.views import APIView  # REST Framework


class Sub(APIView):
    def get(self, request):
        print("Get으로 호출")
        return render(request, "instagram/index.html")
