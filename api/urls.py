from django.urls import path
from .views import StringAnalyzerCreateAPIView, StringAnalyzerListAPIView, StringAnalyzerDetailDestroyAPIView

urlpatterns = [
    path("strings/", StringAnalyzerListAPIView.as_view()),
    path("strings/create", StringAnalyzerCreateAPIView.as_view()),
    path("strings/<str:value>", StringAnalyzerDetailDestroyAPIView.as_view()),
]
