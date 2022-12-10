from eventos.models import SolicitudEvento


def get_solicitudes_evento(remitente, destinatario):
	try:
		return SolicitudEvento.objects.get(remitente=remitente, destinatario=destinatario, is_active=True)
	except SolicitudEvento.DoesNotExist:
		return False