from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
from django.views.decorators.http import require_GET
from .models import Folder, File
from .integrations import generate_presigned_url, delete_object, delete_multiple_objects, object_exists
import json
import uuid

#FIXME: Add Validations

class FolderListView(View):
    template_name = "folder_list.html"

    def get(self, request, *args, **kwargs):
        context = {}
        folder_id = self.kwargs.get('folder_id', None)
        if folder_id:
            folder = Folder.objects.get(id=folder_id) #TODO: maybe usie something to just get the parent_id value
            context['parent_folder_id'] = folder.parent_folder and folder.parent_folder.id
            print(context['parent_folder_id'])
        context['folder_id'] = folder_id
        context['folders'] = Folder.objects.filter(parent_folder=folder_id)
        context['files'] =  File.objects.filter(folder=folder_id)
        request.session['current_folder_id'] = folder_id 
        return render(request, 'folder_list.html', context)
    
    def post(self, request, *args, **kwargs):
        context = {}
        body_data = json.loads(request.body)
        print(body_data)
        folder_name = body_data.get('folder_name')
        current_folder_id = request.session.get('current_folder_id') #TODO: We don't really need to pass this to frontend this can be a security flaw
        new_folder = Folder.objects.create(name=folder_name, parent_folder_id=current_folder_id)

        return JsonResponse({"message": 'Folder Created Successfully',
                             "folder_id": new_folder.id}, status=200)

    def put(self, request, *args, **kwargs):
        folder_id = self.kwargs.get('folder_id')
        body_data = json.loads(request.body)
        update_folder_name = body_data.get('folder_name')
        print(update_folder_name)
        folder = Folder.objects.get(id=folder_id)
        folder.name = update_folder_name
        folder.save()
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
        folder_id = self.kwargs.get('folder_id')
        print(folder_id)
        folder = Folder.objects.get(id=folder_id)
        self._delete_folder(folder)
        # TODO: Actually check the response before deleting 
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)


    def _delete_folder(self, folder):
        folders_inside_folder = Folder.objects.filter(parent_folder=folder)
        for inner_folder in list(folders_inside_folder):
            self._delete_folder(inner_folder)
        print(folder.name)
        files_inside_folder = File.objects.filter(folder=folder)
        files_object_keys = list(map( lambda x: str(x.object_key),files_inside_folder))
        print(files_object_keys)
        s3_resp = delete_multiple_objects(files_object_keys)
        files_inside_folder.delete()
        folder.delete()
        # TODO: Check if they are getting deleted otherwise throw error
        # TODO: This similar code is used while deleting a file so move comon code to one function and use it at both places


class FileListView(View):

    def put(self, request, *args, **kwargs):
        file_id = self.kwargs.get('file_id')
        body_data = json.loads(request.body)
        update_file_name = body_data.get('file_name')
        print(update_file_name)
        file = File.objects.get(id=file_id)
        file.name = update_file_name
        file.save()
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
        file_name = request.GET.get('file_name')
        file_id = self.kwargs.get('file_id')
        current_folder_id = request.session.get('current_folder_id')
        print(current_folder_id)
        if current_folder_id:
            current_folder = Folder.objects.get(id=current_folder_id)
            current_folder.is_empty = False
            current_folder.save()
        else:
            current_folder = None
        print(type(file_id))
        file = File.objects.get(id=file_id)
        s3_resp = delete_object(file.object_key)
        file.delete() 
        # TODO: Actually check the response before deleting 
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)

    def post(self, request, *args, **kwargs):
        body_data = json.loads(request.body)
        print(body_data)
        object_key = body_data.get('object_key')
        file_name = body_data.get('file_name')
        folder_id = body_data.get('folder_id')
        folder = folder_id  and Folder.objects.get(folder_id)
        if object_exists(object_key):
            file = File.objects.create(
                name=file_name,
                object_key=object_key,
                folder=folder 
            )
            return JsonResponse({"message": "File Created Successfully", "id": file.id}, status=200) 
        else:
            return JsonResponse({"message": f"No Object with the given key exists - {object_key} "}, status=404)
    
    # TODO: Check If folder ID is valid
    # TODO: Handle S3 exceptions they should not be shown at frontend

# TODO: Check if file empty
# TODO: Folder id should be in backend only ?
# TODO: This is not the correct way to do things first generate object key and if only it gets create in s3 create it at your end 
@require_GET
def get_presigned_url(request, *args, **kwargs):
    object_key = uuid.uuid4()
    presigned_url = generate_presigned_url(object_key=object_key, for_upload=True)
    return JsonResponse({"presigned_url": presigned_url, "object_key": object_key})


# TODO: Duplicate code fix
# TODO: Check if file empty and file_id null
@require_GET
def get_presigned_url_for_download(request, file_id, *args, **kwargs):
    file = File.objects.get(id=file_id)
    presigned_url = generate_presigned_url(object_key=file.object_key, file_name=file.name, for_upload=False)
    return JsonResponse({"presigned_url": presigned_url})

