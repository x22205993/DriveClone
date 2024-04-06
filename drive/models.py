import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Folder(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_empty = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    #FIXME: Is it a good idea to keep this empty ?

class File(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    object_key = models.CharField(max_length=300)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True) #TODO: We need to deifne root folder so as to not save blank
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)