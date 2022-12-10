from django.contrib import admin
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from personal.views import (
	no_login_view
)

from cuenta.views import (
    register_view,
    login_view,
    logout_view,
    buscar_usuarios_view,
)

urlpatterns = [
	path('', no_login_view, name='home'),
    path('cuenta/', include('cuenta.urls', namespace='cuenta')),
	path('admin/', admin.site.urls),
    path('amistad/', include('amistad.urls', namespace='amistad')),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('register/', register_view, name="register"),
    path('buscar/', buscar_usuarios_view, name="buscar"),
    path('eventos/', include('eventos.urls', namespace='eventos')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)