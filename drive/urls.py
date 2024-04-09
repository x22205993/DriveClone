from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import( FolderListView, FileListView, get_presigned_url, get_presigned_url_for_download, login_view, signup_view)

urlpatterns = [
    path('folders/<str:folder_id>/', FolderListView.as_view()),
    path('folders/', FolderListView.as_view()),
    path('folders/', FolderListView.as_view()),
    path('files/upload-url/', get_presigned_url), 
    path('files/<str:file_id>/download-url/', get_presigned_url_for_download),
    path('files/<str:file_id>/', FileListView.as_view()),
    path('files/', FileListView.as_view()),
    path('', FolderListView.as_view()),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('', FolderListView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
