from django.urls import path
from .views import StringAnalyzerCreateAPIView, StringAnalyzerListAPIView, StringAnalyzerDetailDestroyAPIView,StringAnalyzerNFLListAPIView

urlpatterns = [
    path("strings/", StringAnalyzerListAPIView.as_view()),
    path("strings/create", StringAnalyzerCreateAPIView.as_view()),
    # path("strings/create", StringAnalyzerCreateAPIView.as_view()),
    path("strings/filter-by-natural-language", StringAnalyzerNFLListAPIView.as_view()),
    path("strings/<str:value>", StringAnalyzerDetailDestroyAPIView.as_view()),

]
