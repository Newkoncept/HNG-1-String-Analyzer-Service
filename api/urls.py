from django.urls import path
from .views import StringAnalyzerListAndCreateAPIView, StringAnalyzerDetailDestroyAPIView,StringAnalyzerNFLListAPIView

urlpatterns = [
    path("strings", StringAnalyzerListAndCreateAPIView.as_view()),
    path("strings/filter-by-natural-language", StringAnalyzerNFLListAPIView.as_view()),
    path("strings/<str:value>", StringAnalyzerDetailDestroyAPIView.as_view()),

]
