from django.db import models

# Create your models here.
class StringAnalyzer(models.Model):
    id = models.CharField(max_length=100, primary_key=True, editable=False)
    value = models.TextField(unique=True, null=False, blank=False)
    properties = models.JSONField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    