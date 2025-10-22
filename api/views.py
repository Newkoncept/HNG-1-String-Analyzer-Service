from .serializers import StringAnalyzerSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveDestroyAPIView
from .models import StringAnalyzer
from rest_framework.response import Response
from rest_framework import status
from .utils import status_error_code_displayer, get_sha256_hash, is_palindrome, unique_character, word_count, character_map, nlf
from datetime import datetime, timezone
from rest_framework.exceptions import NotFound
from django.db.models import Q

class StringAnalyzerListAPIView(ListAPIView):
    queryset = StringAnalyzer.objects.all()
    serializer_class = StringAnalyzerSerializer

    def get_queryset(self):
        query = super().get_queryset()

        qs = query.filter(
            properties__is_palindrome       = self.is_palindrome,
            properties__length__gte         = self.min_length,
            properties__length__lte         = self.max_length,                 
            properties__word_count__exact   = self.word_count,          
            value__icontains                = self.contains_character
        )
    
        return qs
    
    def list(self, request, *args, **kwargs):
        
        request_parameters = request.query_params
        expected_parameters = ["is_palindrome", "min_length", "max_length", "word_count", "contains_character"]

        unknown = set(request_parameters.keys()) != set(expected_parameters)

        if unknown:
            return Response(
                {status_error_code_displayer(400): "Invalid query parameter values or types"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            self.is_palindrome = bool(request_parameters["is_palindrome"])
            self.min_length = int(request_parameters["min_length"])
            self.max_length = int(request_parameters["max_length"])
            self.word_count = int(request_parameters["word_count"])
            self.contains_character = str(request_parameters["contains_character"])
        except Exception as e:
            return Response(
                {status_error_code_displayer(400): "Invalid query parameter values or types"
                 },
                status=status.HTTP_400_BAD_REQUEST
            )
        

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "data" : serializer.data,\
            "count" : len(serializer.data),
            "filter_applied": request_parameters
        }

        return Response(data)


        
        # return super().list(request, *args, **kwargs)
    

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
    

class StringAnalyzerDetailDestroyAPIView(RetrieveDestroyAPIView):
    queryset = StringAnalyzer.objects.all()
    serializer_class = StringAnalyzerSerializer
    lookup_url_kwarg = 'value'
    lookup_field = "value"

    def handle_exception(self, exc):
        response =  super().handle_exception(exc)
        if response is None or response.status_code == 404:
            return Response(
                {status_error_code_displayer(404): "String does not exist in the system"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return super().handle_exception(exc)


class StringAnalyzerNFLListAPIView(ListAPIView):
    queryset = StringAnalyzer.objects.all()
    serializer_class = StringAnalyzerSerializer

    def get_queryset(self):
        query = super().get_queryset()

        if 'is_palindrome' in self.filters:
            query = query.filter(properties__is_palindrome=self.filters['is_palindrome'])

        if 'word_count' in self.filters:
            query = query.filter(properties__word_count__exact=self.filters['word_count'])

        if 'min_length' in self.filters:
            query = query.filter(properties__length__gte=self.filters['min_length'])

        if 'max_length' in self.filters:
            query = query.filter(properties__length__lte=self.filters['max_length'])

        if 'contains_character' in self.filters:
            query = query.filter(value__icontains=self.filters['contains_character'])
            
        return query
    
    
    def list(self, request, *args, **kwargs):
        request_parameters = request.query_params
        filters = nlf(request_parameters["query"])

        if len(filters) > 0:
                    # --- sanity/contradictions ---
            if "min_length" in filters and "max_length" in filters:
                return Response(
                    {status_error_code_displayer(422): "Query parsed but resulted in conflicting filters"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            else:
                self.filters = filters
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)

                data = {
                    "data" : serializer.data,\
                    "count" : len(serializer.data),
                    "interpreted query":  {
                        "original": request_parameters["query"],
                        "parsed_filters": filters
                    }
                }

                return Response(data)
        
        else:
            return Response(
                {status_error_code_displayer(400): "Unable to parse natural language query"},
                status=status.HTTP_400_BAD_REQUEST
            )