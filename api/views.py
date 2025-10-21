from .serializers import StringAnalyzerSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from .models import StringAnalyzer
from rest_framework.response import Response
from rest_framework import status
from .utils import status_error_code_displayer, get_sha256_hash, is_palindrome, unique_character, word_count, character_map
from datetime import datetime, timezone

# class StringAnalyzerListAPIView(ListAPIView):
class StringAnalyzerListAPIView(ListCreateAPIView):
    queryset = StringAnalyzer.objects.all()
    serializer_class = StringAnalyzerSerializer

class StringAnalyzerCreateAPIView(CreateAPIView):
    queryset = StringAnalyzer.objects.all()
    serializer_class = StringAnalyzerSerializer

    def create(self, serializer):

        data = self.request.data.copy()

        # print(data)


        if "value" not in data.keys():
            return Response(
                {status_error_code_displayer(400): "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(data["value"], str): 
            return Response(
                {status_error_code_displayer(422): "Invalid request body or missing 'value' field"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if self.queryset.filter(value = data["value"]):
            return Response(
                {status_error_code_displayer(409): "String already exists in the system"},
                status=status.HTTP_409_CONFLICT
            )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def perform_create(self, serializer):

        value = self.request.data["value"]

        hashed_value = get_sha256_hash(value)

        id = hashed_value
        properties = {
            "length": len(value),
            "is_palindrome": is_palindrome(value),
            "unique_characters": unique_character(value),
            "word_count": word_count(value),
            "sha256_hash": hashed_value,
            "character_frequency_map": character_map(value)
        }

        serializer.save(id = hashed_value, properties = properties)
        return super().perform_create(serializer)