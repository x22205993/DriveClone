from .views import(StorageItemListApiView, StorageItemDetail)
from django.urls import path, include

urlpatterns = [
    path('', StorageItemListApiView.as_view()),
    path('<int:pk>/', StorageItemDetail.as_view()),
    path('upload/', StorageItemDetail.as_view())
]