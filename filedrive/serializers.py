from rest_framework import serializers
from filedrive.models import Item
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'created_at', 'updated_at', 'object_key', 'parent', 'is_dir', 'size']