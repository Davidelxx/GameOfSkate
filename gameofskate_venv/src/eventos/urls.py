from django.urls import path

from eventos.views import(
	crear_evento,
	solicitudes_eventos,
	aceptar_solicitud_evento,
	rechazar_solicitud_evento,
	lista_eventos_view,
	evento_view,
	comenzar_evento,
	eliminar_evento,
)

app_name = 'eventos'
urlpatterns = [
	path('crear_evento/', crear_evento, name='crear-evento'),
	path('lista_eventos/<user_id>', lista_eventos_view, name='lista-eventos'),
    path('solicitudes_eventos/<user_id>/', solicitudes_eventos, name='solicitudes-eventos'),
    path('aceptar_solicitud_evento/<solicitud_evento_id>/', aceptar_solicitud_evento, name='aceptar-solicitud-evento'),
    path('rechazar_solicitud_evento/<solicitud_evento_id>/', rechazar_solicitud_evento, name='rechazar-solicitud-evento'),
    path('evento/<evento_id>/', evento_view, name='evento-view'),
    path('comenzar_evento/<evento_id>/', comenzar_evento, name='comenzar-evento'),
	path('eliminar_evento/<evento_id>/', eliminar_evento, name='eliminar-evento'),
]