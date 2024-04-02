import uuid
from django.db import models

# Create your models here.


class PathMap(models.Model):
    path =  models.CharField(max_length=200)

class StorageItem(models.Model):
    item_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_dir = models.BooleanField(default=False)
    filepath = models.CharField(max_length=200, null=True, blank=True)
    path_id = models.ForeignKey(PathMap, on_delete=models.CASCADE)
    object_id = models.UUIDField(default=uuid.uuid4, editable=False)

