from rest_framework import serializers
from drive.models import StorageItem

class StorageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageItem
        fields = ['id', 'item_name', 'created_at', 'is_dir', 'filepath', 'path_id']

