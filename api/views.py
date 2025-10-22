from .serializers import StringAnalyzerSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from .models import StringAnalyzer
from rest_framework.response import Response
from rest_framework import status
from .utils import status_error_code_displayer, get_sha256_hash, is_palindrome, unique_character, word_count, character_map, nlf, query_set_logic
from datetime import datetime, timezone
from rest_framework.exceptions import NotFound
from django.db.models import Q

class StringAnalyzerListAndCreateAPIView(ListCreateAPIView):
    serializer_class = StringAnalyzerSerializer

    def base_get_queryset(self):
        return StringAnalyzer.objects.all()

    def get_queryset(self):
        query = self.base_get_queryset()

        qs = query_set_logic(self, query)
    
        return qs
    

    def list(self, request, *args, **kwargs):
        
        request_parameters = request.query_params
        request_parameters_keys = request_parameters.keys()
        
        try:
            self.filters = {}
            if "is_palindrome" in request_parameters_keys:
                self.filters["is_palindrome" ] = bool(request_parameters["is_palindrome"])
            if "min_length" in request_parameters_keys:
                self.filters["min_length" ] = int(request_parameters["min_length"])
            if "max_length" in request_parameters_keys:
                self.filters["max_length" ] = int(request_parameters["max_length"])
            if "word_count" in request_parameters_keys:
                self.filters[ "word_count" ] = int(request_parameters["word_count"])
            if "contains_character" in request_parameters_keys:
                self.filters["contains_character"] =  str(request_parameters["contains_character"])

        except Exception as e:
            return Response(
                {status_error_code_displayer(400): "Invalid query parameter values or types"
                 },
                status=status.HTTP_400_BAD_REQUEST
            )
        

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        data = {
            "data" : serializer.data,
            "count" : len(serializer.data),
            "filters_applied": request_parameters
        }

        return Response(data)
    
    def create(self, request, *args, **kwargs):

        data = self.request.data.copy()


        if "value" not in data.keys():
            return Response(
                {status_error_code_displayer(400): "Invalid request body or missing 'value' field"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(data["value"], str): 
            return Response(
                {status_error_code_displayer(422): 'Invalid data type for "value" (must be string)'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        if self.base_get_queryset().filter(value = data["value"]).exists():
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
        properties = {
            "length": len(value),
            "is_palindrome": is_palindrome(value),
            "unique_characters": unique_character(value),
            "word_count": word_count(value),
            "sha256_hash": hashed_value,
            "character_frequency_map": character_map(value)
        }

        serializer.save(id = hashed_value, properties = properties)

    
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

        query = query_set_logic(self, query)

        return query
    
    
    def list(self, request, *args, **kwargs):
        request_parameters = request.query_params


        if "query" not in request_parameters.keys():
            return Response(
                {status_error_code_displayer(400): "Unable to parse natural language query"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

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
                    "interpreted_query":  {
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