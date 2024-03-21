from .views import(StorageItemListApiView)
from django.urls import path, include

urlpatterns = [
    path('api', StorageItemListApiView.as_view()),
]