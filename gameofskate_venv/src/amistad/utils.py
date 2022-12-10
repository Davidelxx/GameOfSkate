from amistad.models import SolicitudAmistad


def get_solicitudes_amistad(remitente, destinatario):
	try:
		return SolicitudAmistad.objects.get(remitente=remitente, destinatario=destinatario, is_active=True)
	except SolicitudAmistad.DoesNotExist:
		return False