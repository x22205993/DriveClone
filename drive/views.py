from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PathMap, StorageItem
from .serializers import StorageItemSerializer

# Create your views here.
class StorageItemListApiView(APIView):
    def get(self, request, format=None):
        # path_map = PathMap.objects.filter(id=request.path_id)
        # storage_items = StorageItem.objects.filter(path_id=path_map.id)
        print(request.__dict__)
        storage_items = StorageItem.objects.filter()
        serializer = StorageItemSerializer(storage_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
