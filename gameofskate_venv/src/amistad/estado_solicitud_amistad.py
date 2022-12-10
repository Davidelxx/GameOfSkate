from enum import Enum


class EstadoSolicitudAmistad(Enum):
	NO_SOLICITUD = -1
	SOLICITUD_RECIBIDA = 0
	SOLICITUD_ENVIADA = 1
