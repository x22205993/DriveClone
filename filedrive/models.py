from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    object_key = models.CharField(max_length=300, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_dir = models.BooleanField(default=False)
    size = models.FloatField(default=0)

    # shared_users = models.ManyToManyField(User, related_name="shared_items", null=True)

