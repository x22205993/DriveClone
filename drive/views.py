from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PathMap, StorageItem
from .integrations import generate_presigned_url
from .serializers import StorageItemSerializer

#FIXME: Add Validations
#FIXME: do we have to make copy of request here use request params instead?
# Create your views here.
class StorageItemListApiView(APIView):
    def get(self, request, format=None):
        storage_items = StorageItem.objects.all()
        serializer = StorageItemSerializer(storage_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        data = request.data.copy()
        path = data.get('path')
        path_map, created = PathMap.objects.get_or_create(path=path)
        data.update({"path_id": path_map.id})
        data.update({"filepath": "/filepath/filepath1"})
        serializer = StorageItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StorageItemDetail(APIView):
    def get(self, request, pk):
        try:
            storage_item = StorageItem.objects.get(pk=pk)
            presigned_url = generate_presigned_url(storage_item.object_id)
            return Response(presigned_url, status=status.HTTP_200_OK)
        except StorageItem.DoesNotExist:
            raise status.Http404
    
    def post(self, request):
        try:
            file_name = request.data.get('filename')
            path = request.data.get('path')
            print(file_name, path, request)
            path_map, created = PathMap.objects.get_or_create(path=path)
            storage_item = StorageItem(
                item_name=file_name,
                path_id=path_map,
                is_dir=False
            )
            storage_item.save()
            presigned_url = generate_presigned_url(storage_item.object_id, for_upload=True)
            return Response(presigned_url, status=status.HTTP_200_OK)
        except StorageItem.DoesNotExist:
            raise status.Http404
    