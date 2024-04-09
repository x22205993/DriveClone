from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Folder, File
from .integrations import generate_presigned_url, delete_object, delete_multiple_objects, object_exists, create_bucket
from .forms import LoginForm, SignupForm
import json
import uuid

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username, password)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Invalid username or password')
                messages.error(request, 'Invalid username or password.')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            resp = create_bucket(str(user.id)) #TODO: check if bucket is actually created
            if resp.status != 200:
                return JsonResponse({"message": "Error while creating bucket"}, status=500)
            return redirect('login') 
        else:
            request.session['signup_form_data'] = request.POST.dict()
            return redirect('signup')
    else:
        form_data = request.session.pop('signup_form_data', None)
        print(form_data)
        form = SignupForm(data=form_data)
    

    return render(request, 'signup.html', {'form': form,})

#FIXME: Add Validations
# TODO: Do I need to add bucket field in file and folder model also
class FolderListView(LoginRequiredMixin, View):
    template_name = "folder_list.html"

    def get(self, request, *args, **kwargs):
        context = {}
        folder_id = self.kwargs.get('folder_id', None)
        if folder_id:
            try:        
                folder = Folder.objects.get(id=folder_id) #TODO: maybe usie something to just get the parent_id value
                context['parent_folder_id'] = folder.parent_folder and folder.parent_folder.id
            except Folder.DoesNotExist:
                return JsonResponse({"message": "Folder Does not Exist"}, status=404)
        context['folder_id'] = folder_id
        context['folders'] = Folder.objects.filter(parent_folder=folder_id, user=request.user)
        context['files'] =  File.objects.filter(folder=folder_id, user=request.user)
        request.session['current_folder_id'] = folder_id 
        return render(request, 'folder_list.html', context)
    
    def post(self, request, *args, **kwargs):
        body_data = json.loads(request.body)
        folder_name = body_data.get('folder_name')
        current_folder_id = request.session.get('current_folder_id') #TODO: We don't really need to pass this to frontend this can be a security flaw
        if not folder_name:
            return JsonResponse({"message": 'Folder Name is mandatory'}, status=400)

        new_folder = Folder.objects.create(name=folder_name, parent_folder_id=current_folder_id, user=request.user)

        return JsonResponse({"message": 'Folder Created Successfully',
                             "folder_id": new_folder.id}, status=200)

    def put(self, request, *args, **kwargs):
        folder_id = self.kwargs.get('folder_id')
        body_data = json.loads(request.body)
        update_folder_name = body_data.get('folder_name')
        if not update_folder_name:
            return JsonResponse({"message": "Folder ID and New Folder Name is mandatory"}, status=400)
        try:
            folder = Folder.objects.get(id=folder_id, user=request.user)
        except Folder.DoesNotExist:
            return JsonResponse({"message": "Folder does not exist"}, status=404)
        folder.name = update_folder_name
        folder.save()
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
        folder_id = self.kwargs.get('folder_id')
        try:
            folder = Folder.objects.get(id=folder_id, user=request.user)
        except Folder.DoesNotExist:
            return JsonResponse({"message": "Folder does not exist"}, status=404)
        try:
            self._delete_folder(folder, str(request.user.id)) #TODO: make this thing common
        except Exception as e:
            return JsonResponse({"message": "Failed to Delete Folder", "error": str(e)}, status=500)
        # TODO: Actually check the response before deleting 
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)


    def _delete_folder(self, folder, bucket_name):
        folders_inside_folder = Folder.objects.filter(parent_folder=folder)
        for inner_folder in list(folders_inside_folder):
            self._delete_folder(inner_folder, bucket_name)
        print(folder.name)
        files_inside_folder = File.objects.filter(folder=folder)
        files_object_keys = list(map( lambda x: str(x.object_key),files_inside_folder))
        print(files_object_keys)
        try:
            s3_resp = delete_multiple_objects(bucket_name, files_object_keys)
            if s3_resp.status != 200:
                return JsonResponse({"message": "Error while Deleting File"}, status=500)
            files_inside_folder.delete()
            folder.delete()
        except Exception as e:
            raise Exception(f"Failed to Delete folder: {e}")

        # TODO: Check if they are getting deleted otherwise throw error
        # TODO: This similar code is used while deleting a file so move comon code to one function and use it at both places


class FileListView(LoginRequiredMixin, View):

    def put(self, request, *args, **kwargs):
        try:
            file_id = self.kwargs.get('file_id')
            if not file_id:
                return JsonResponse({"maeesage": "File ID not present"}, status=400)
            body_data = json.loads(request.body)
            update_file_name = body_data.get('file_name')
            print(update_file_name)
            file = File.objects.get(id=file_id, user=request.user)
            file.name = update_file_name
            file.save()
        except Exception:
            return JsonResponse({"message": "Error while Updating File Name"}, status=500)
        return JsonResponse({"message": "Updated Succesfully"}, status=200)
    
    def delete(self, request, *args, **kwargs):
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
            s3_resp = delete_object(str(request.user.id), file.object_key)
            if s3_resp.status != 200:
                return JsonResponse({"message": "Error while Deleting File"}, status=500)
            file.delete() 
        except Exception:
            return JsonResponse({"message": "Error while Deleteing File"}, status=500)
        # TODO: Actually check the response before deleting 
        return JsonResponse({"message": "File Deleted Successfully"}, status=200)

    def post(self, request, *args, **kwargs):
        try:
            body_data = json.loads(request.body)
            print(body_data)
            object_key = body_data.get('object_key')
            file_name = body_data.get('file_name')
            folder_id = body_data.get('folder_id')
            if not file_name or not object_key:
                return JsonResponse({"message": "File Name and Object key is required"}, status=400)
            folder = folder_id  and Folder.objects.get(id=folder_id, user=request.user)
            if object_exists(str(request.user.id), object_key):
                file = File.objects.create(
                    name=file_name,
                    object_key=object_key,
                    folder=folder,
                    user=request.user
                )
                return JsonResponse({"message": "File Created Successfully", "id": file.id}, status=200) 
            else:
                return JsonResponse({"message": f"No Object with the given key exists - {object_key} "}, status=404)
        except Exception:
            return JsonResponse({"message": "Error while creating file"}, status=500) 
    # TODO: Check If folder ID is valid
    # TODO: Handle S3 exceptions they should not be shown at frontend

# TODO: Check if file empty
# TODO: Folder id should be in backend only ?
# TODO: This is not the correct way to do things first generate object key and if only it gets create in s3 create it at your end 
@require_GET
@login_required
def get_presigned_url(request, *args, **kwargs):
    object_key = uuid.uuid4()
    presigned_url = generate_presigned_url(str(request.user.id), object_key=object_key, for_upload=True)
    return JsonResponse({"presigned_url": presigned_url, "object_key": object_key})


# TODO: Duplicate code fix
# TODO: Check if file empty and file_id null
@require_GET
@login_required
def get_presigned_url_for_download(request, file_id, *args, **kwargs):
    try:
        file = File.objects.get(id=file_id)
    except Exception:
        return JsonResponse({"message": "Error while generating presigned url for download"}, status=500)
    presigned_url = generate_presigned_url(str(request.user.id), object_key=file.object_key, file_name=file.name, for_upload=False)
    return JsonResponse({"presigned_url": presigned_url})

