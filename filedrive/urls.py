from rest_framework import routers, views
from filedrive.views import ItemViewSet, UserViewSet, login_view, logout_view, check_session_view, presigned_url_view, presigned_url_for_download_view
from django.urls import include, path

router = routers.SimpleRouter()
router.register(r'items', ItemViewSet, 'items')
router.register(r'users', UserViewSet)

urlpatterns = [
    path('login', login_view),
    path('logout', logout_view),
    path('check-session', check_session_view),
    path('upload-url', presigned_url_view),
    path('items/<str:item_id>/download-url', presigned_url_for_download_view)

]

urlpatterns += router.urls