from rest_framework import serializers
from .models import StringAnalyzer


class StringAnalyzerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringAnalyzer
        # exclude = []
        fields = "__all__"
        read_only_fields = ["properties", "id", "created_at"]
