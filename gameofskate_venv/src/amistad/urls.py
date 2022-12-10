from django.urls import path

from amistad.views import(
	enviar_solicitud_amistad,
	solicitudes_amistad,
	aceptar_solicitud_amistad,
	eliminar_amigo,
	rechazar_solicitud_amistad,
	cancelar_solicitud_amistad,
	lista_amigos_view,
)

app_name = 'amistad'

urlpatterns = [
	path('lista_amigos/<user_id>', lista_amigos_view, name='lista-amigos'),
	path('eliminar_amigo/', eliminar_amigo, name='eliminar-amigo'),
    path('enviar_solicitud_amistad/', enviar_solicitud_amistad, name='enviar-solicitud-amistad'),
    path('cancelar_solicitud_amistad/', cancelar_solicitud_amistad, name='cancelar-solicitud-amistad'),
    path('solicitudes_amistad/<user_id>/', solicitudes_amistad, name='solicitudes-amistad'),
    path('aceptar_solicitud_amistad/<solicitud_amistad_id>/', aceptar_solicitud_amistad, name='aceptar-solicitud-amistad'),
    path('rechazar_solicitud_amistad/<solicitud_amistad_id>/', rechazar_solicitud_amistad, name='rechazar-solicitud-amistad'),
]