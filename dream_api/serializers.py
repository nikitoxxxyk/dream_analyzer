from rest_framework import serializers
from .models import Dream

class DreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dream
        fields = ['id', 'user_id', 'text', 'interpretation', 'created_at']
