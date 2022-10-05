from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('auth/', include('users.urls', namespace='users')),
    path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls', namespace='posts')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
handler403 = 'core.views.permission_denied'
