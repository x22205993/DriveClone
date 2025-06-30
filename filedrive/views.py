import uuid

from django.contrib.auth.models import User
from django.contrib.auth import logout
from filedrive.models import Item
from filedrive.serializers import ItemSerializer, UserSerializer
from rest_framework import mixins, generics, permissions, viewsets
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth import login
from filedrive.integrations import IntegrationException
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from rest_framework.permissions import IsAuthenticated, AllowAny
from filedrive.integrations import generate_presigned_url, delete_multiple_objects

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ItemViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    def get_queryset(self):
        owner = self.request.user
        #Here 0 is the root folder id is this hardcoding it ?
        parent_id = self.request.query_params.get('parent', None)
        return Item.objects.filter(owner=owner.id, parent=parent_id)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_destroy(self, instance):
        files_to_delete = []
        folders_to_delete = []
        items_to_delete = [instance]
        while items_to_delete:
            cur_item = items_to_delete.pop()
            if cur_item.is_dir:
                items = Item.objects.filter(parent=cur_item.id).all()
                print(items)
                items_to_delete.extend(items)
                folders_to_delete.append(cur_item)
            else:
                files_to_delete.append(cur_item)  
        resp = delete_multiple_objects([file.object_key for file in files_to_delete], cur_item.owner.id)
        
        for file in files_to_delete:
            file.delete()

        for folder in folders_to_delete:
            folder.delete()

    @action(detail=False, url_path='bulk-delete', methods=['delete'])
    def bulk_destroy(self, request):
        item_ids = self.request.query_params.get('ids', '').split(',')
        print(item_ids)
        for item_id in item_ids:
            item = Item.objects.get(id=item_id)
            print(item.id, item_id)
            self.perform_destroy(item)
        
        return Response({"message": "Deleted files"}, status=200)


        

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def presigned_url_view(request, *args, **kwargs):
    ''' 
        This function returns the presigned url from S3 to the frontend to upload the object
    '''
    try:
        object_key = uuid.uuid4()
        presigned_url = generate_presigned_url(object_key=object_key, 
                                            prefix=str(request.user.id),for_upload=True)
    except IntegrationException:
        return Response({"message": "Error while getting download url"}, status=500)
    return Response({"upload_url": presigned_url, "object_key": object_key}, status=200)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def presigned_url_for_download_view(request, item_id, *args, **kwargs):
    '''
        This function returns presigned url for object download
    '''
    try:
        file = Item.objects.get(id=item_id)
        presigned_url = generate_presigned_url(object_key=file.object_key, 
                                           prefix=str(request.user.id), 
                                           file_name=file.name, for_upload=False)
    except IntegrationException:
        return Response({"message": "Error while getting download url"}, status=500)
    return Response({"download_url": presigned_url}, status=200)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    if not request.user:
        return Response({"message": "Failed to Login"}, status=401)
    login(request, request.user)
    return Response({"message": "Login Successful"}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def logout_view(request):
    if not request.user:
        return Response({"message": "No logged in User found"}, status=400)
    logout(response)
    return Response({"message": "Logged out Successfully"}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def check_session_view(request):
    if request.user.is_authenticated:
        return Response({"message": "User is authenticated"}, status=200)
    return Response({"message": "User is not authenticated"}, status=403)