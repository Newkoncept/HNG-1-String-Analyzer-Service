from django.urls import path
from .views import StringAnalyzerCreateAPIView, StringAnalyzerListAPIView

urlpatterns = [
    path("strings/", StringAnalyzerListAPIView.as_view()),
    path("strings/create", StringAnalyzerCreateAPIView.as_view()),
]
