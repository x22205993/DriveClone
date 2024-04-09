from django.db import models
from django.contrib.auth.models import User # pylint: disable=imported-auth-user

# Create your models here.

class Folder(models.Model):
    ''' Folder Model '''
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_empty = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

class File(models.Model):
    ''' File Model '''
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    object_key = models.CharField(max_length=300)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
