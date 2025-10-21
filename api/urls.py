from django.urls import path
from .views import StringAnalyzerCreateAPIView, StringAnalyzerListAPIView, StringAnalyzerDetailAPIView

urlpatterns = [
    path("strings/", StringAnalyzerListAPIView.as_view()),
    path("strings/create", StringAnalyzerCreateAPIView.as_view()),
    path("strings/<str:value>", StringAnalyzerDetailAPIView.as_view()),
]
