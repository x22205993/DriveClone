import json
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.http import require_GET
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from drive import json_loads_suppress_exc

from .models import Folder, File
from .integrations import generate_presigned_url, delete_object, \
    delete_multiple_objects, object_exists, IntegrationException

INVALID_REQUEST_BODY_ERROR = "Invalid Request Body"

class FolderListView(LoginRequiredMixin, View):
    ''' Handler for CRUD operations of Folder Model '''
    template_name = "main.html"
    def get(self, request, *args, **kwargs):
        ''' Get all the files and folders inside the current folder. '''
        context = {}
        folder_id = self.kwargs.get('folder_id', None)
        if folder_id:    
            folder = Folder.objects.get(id=folder_id, user=request.user)
            context['parent_folder_id'] = folder.parent_folder and folder.parent_folder.id
        context['folder_id'] = folder_id
        context['folders'] = Folder.objects.filter(parent_folder=folder_id, user=request.user)
        context['files'] =  File.objects.filter(folder=folder_id, user=request.user)
        request.session['current_folder_id'] = folder_id 
        return render(request, 'main.html', context)
    
    def post(self, request, *args, **kwargs):
        ''' Create a new Folder Object '''
        body_data = json_loads_suppress_exc(request.body)
        if not body_data:
            return JsonResponse({"message": INVALID_REQUEST_BODY_ERROR}, status=400)
        folder_name = body_data.get('folder_name')
        current_folder_id = request.session.get('current_folder_id')
        if not folder_name:
            return JsonResponse({"message": 'Folder Name is mandatory'}, status=400)
        Folder.objects.create(
            name=folder_name, parent_folder_id=current_folder_id, user=request.user)
        return JsonResponse({"message": "Folder created succesfully "}, status=200)

    def put(self, request, *args, **kwargs):
        ''' Update Folder Name '''
        folder_id = self.kwargs.get('folder_id')
        body_data = json_loads_suppress_exc(request.body)
        if not body_data:
            return JsonResponse({"message": INVALID_REQUEST_BODY_ERROR}, status=400)
        update_folder_name = body_data.get('folder_name')
        if not update_folder_name:
            return JsonResponse(
                {"message": "Folder ID and New Folder Name is mandatory"}, status=400)
        folder = Folder.objects.get(id=folder_id, user=request.user)
        folder.name = update_folder_name
        folder.save()
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
        ''' To delete a folder '''
        folder_id = self.kwargs.get('folder_id')
        folder = Folder.objects.get(id=folder_id, user=request.user)
        try:
            self._delete_folder(folder, str(request.user.id))
        except IntegrationException as e:
            return JsonResponse({"message": "Failed to Delete Folder"}, status=500)
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)


    def _delete_folder(self, folder, object_prefix):
        '''
            This Function ensures to recursively 
            delete all the files and folder inside 
            the folder that needs to be deleted
        '''
        folders_inside_folder = Folder.objects.filter(parent_folder=folder)
        for inner_folder in list(folders_inside_folder):
            self._delete_folder(inner_folder, object_prefix)
        print(folder.name)
        files_inside_folder = File.objects.filter(folder=folder)
        files_object_keys = list(map( lambda x: str(x.object_key),files_inside_folder))
        if files_object_keys:
            delete_multiple_objects(files_object_keys, object_prefix)
            files_inside_folder.delete()
        folder.delete()

class FileListView(LoginRequiredMixin, View):
    ''' Handler for CRUD operations of File Object '''

    def put(self, request, *args, **kwargs):
        ''' To rename a file '''
        file_id = self.kwargs.get('file_id')
        if not file_id:
            return JsonResponse({"message": "File ID not present"}, status=400)
        body_data = json_loads_suppress_exc(request.body)
        if not body_data:
            return JsonResponse({"message": INVALID_REQUEST_BODY_ERROR}, status=400)
        update_file_name = body_data.get('file_name')
        print(update_file_name)
        file = File.objects.get(id=file_id, user=request.user)
        file.name = update_file_name
        file.save()
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
        ''' To Delete a file object '''
        try:
            file_id = self.kwargs.get('file_id')
            if not file_id:
                return JsonResponse({"message": "File ID not present"}, status=400)
            current_folder_id = request.session.get('current_folder_id')
            print(current_folder_id)
            if current_folder_id:
                current_folder = Folder.objects.get(id=current_folder_id, user=request.user)
                current_folder.is_empty = False
                current_folder.save()
            else:
                current_folder = None
            print(type(file_id))
            file = File.objects.get(id=file_id, user=request.user)
            delete_object(file.object_key, str(request.user.id))
            file.delete() 
        except IntegrationException as e:
            print(str(e))
            return JsonResponse({"message": "Error while Deleteing File"}, status=500)
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)

    def post(self, request, *args, **kwargs):
        ''' 
            To Create a file object. Since the file is uploaded to S3 through frontend. 
            When the upload is completed from frontend it initiates call to this function
            which then again verifies that the object has been uploaded to S3 and only 
            then it creates a file object in our database
        '''
        try:
            body_data = json.loads(request.body)
            print(body_data)
            object_key = body_data.get('object_key')
            file_name = body_data.get('file_name')
            folder_id = body_data.get('folder_id')
            if not file_name or not object_key:
                return JsonResponse({"message": "File Name and Object key is required"}, status=400)
            folder=None
            if folder_id:
                folder = Folder.objects.get(id=folder_id, user=request.user)
            if object_exists(object_key, str(request.user.id)):
                file = File.objects.create(
                    name=file_name,
                    object_key=object_key,
                    folder=folder,
                    user=request.user
                )
                return JsonResponse(
                    {"message": "File Created Successfully", "id": file.id}, status=200) 
            return JsonResponse(
                {"message": f"No Object with the given key exists - {object_key} "}, status=404)
        except IntegrationException as e:
            print(str(e))
            return JsonResponse(
                {"message": "Error while creating file"}, status=500) 

@require_GET
@login_required
def get_presigned_url(request, *args, **kwargs):
    ''' 
        This function returns the presigned url from S3 to the frontend to upload the object
    '''
    try:
        object_key = uuid.uuid4()
        presigned_url = generate_presigned_url(object_key=object_key, 
                                            prefix=str(request.user.id),for_upload=True)
    except IntegrationException:
        return JsonResponse({"message": "Error while getting download url"}, status=500)
    return JsonResponse({"presigned_url": presigned_url, "object_key": object_key}, status=200)

@require_GET
@login_required
def get_presigned_url_for_download(request, file_id, *args, **kwargs):
    '''
        This function returns presigned url for object download
    '''
    try:
        file = File.objects.get(id=file_id)
        presigned_url = generate_presigned_url(object_key=file.object_key, 
                                           prefix=str(request.user.id), 
                                           file_name=file.name, for_upload=False)
    except IntegrationException:
        return JsonResponse({"message": "Error while getting download url"}, status=500)
    return JsonResponse({"presigned_url": presigned_url}, status=200)
