"""
URL configuration for cinelog_project project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from movies import views as movie_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', movie_views.login_view, name='login'),
    path('logout/', movie_views.logout_view, name='logout'),
    path('', include('movies.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

