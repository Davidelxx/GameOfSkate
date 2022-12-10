from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from cuenta.models import Cuenta
from amistad.models import SolicitudAmistad, ListaAmigos


def lista_amigos_view(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		if user_id:
			try:
				this_user = Cuenta.objects.get(pk=user_id)
				context['this_user'] = this_user
			except Cuenta.DoesNotExist:
				return HttpResponse("El usuario no existe.")
			try:
				lista_amigos = ListaAmigos.objects.get(user=this_user)
			except ListaAmigos.DoesNotExist:
				return HttpResponse(f"No se encontró una lista de amigos para {this_user.username}")
			
			if user != this_user:
				if not user in lista_amigos.amigos.all():
					return HttpResponse("No puedes ver la lista de amigos de este usuario porque no sois amigos.")
			amigos = []
			auth_user_lista_amigos = ListaAmigos.objects.get(user=user)
			for amigo in lista_amigos.amigos.all():
				amigos.append((amigo, auth_user_lista_amigos.son_amigos(amigo)))
			context['amigos'] = amigos
	else:		
		return redirect("login")

	return render(request, "amistad/lista_amigos.html", context)


def solicitudes_amistad(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		cuenta = Cuenta.objects.get(pk=user_id)
		if cuenta == user:
			solicitudes_amistad = SolicitudAmistad.objects.filter(destinatario=cuenta, is_active=True)
			context['solicitudes_amistad'] = solicitudes_amistad
		else:
			return HttpResponse("No puedes ver las solicitudes de amistad de otros usuarios")
	else:
		redirect("login")
	return render(request, "amistad/solicitudes_amistad.html", context)


def enviar_solicitud_amistad(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("destinatario_user_id")
		if user_id:
			destinatario = Cuenta.objects.get(pk=user_id)
			try:
				solicitudes_amistad = SolicitudAmistad.objects.filter(remitente=user, destinatario=destinatario)
				try:
					for solicitud in solicitudes_amistad:
						if solicitud.is_active:
							raise Exception("Ya le has enviado una solicitud de amistad a este usuario.")
					solicitud_amistad = SolicitudAmistad(remitente=user, destinatario=destinatario)
					solicitud_amistad.save()
					payload['response'] = "Solicitud de amistad enviada."
				except Exception as e:
					payload['response'] = str(e)
			except SolicitudAmistad.DoesNotExist:
				solicitud_amistad = SolicitudAmistad(remitente=user, destinatario=destinatario)
				solicitud_amistad.save()
				payload['response'] = "Solicitud de amistad enviada."

			if payload['response'] == None:
				payload['response'] = "Algo ha ido mal."
		else:
			payload['response'] = "No se pudo enviar la solicitud de amistad."
	else:
		payload['response'] = "Debes estar autenticado para enviar una solicitud de amistad."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def aceptar_solicitud_amistad(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		solicitud_amistad_id = kwargs.get("solicitud_amistad_id")
		if solicitud_amistad_id:
			solicitud_amistad = SolicitudAmistad.objects.get(pk=solicitud_amistad_id)
			if solicitud_amistad.destinatario == user:
				if solicitud_amistad: 
					notificacion_actualizada = solicitud_amistad.aceptar()
					payload['response'] = "Solicitud de amistad aceptada."

				else:
					payload['response'] = "Algo ha ido mal."
			else:
				payload['response'] = "Esa solicitud de amistad no es para tí."
		else:
			payload['response'] = "No se pudo aceptar la solicitud de amistad."
	else:
		payload['response'] = "Debes estar autenticado para aceptar una solicitud de amistad."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def eliminar_amigo(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("destinatario_user_id")
		if user_id:
			try:
				eliminado = Cuenta.objects.get(pk=user_id)
				lista_amigos = ListaAmigos.objects.get(user=user)
				lista_amigos.actualizar_listas_amigos(eliminado)
				payload['response'] = "Amigo eliminado con éxito."
			except Exception as e:
				payload['response'] = f"Algo ha ido mal: {str(e)}"
		else:
			payload['response'] = "No se pudo eliminar ese amigo."
	else:
		payload['response'] = "Debes estar autenticado para eliminar un amigo."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def rechazar_solicitud_amistad(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		solicitud_amistad_id = kwargs.get("solicitud_amistad_id")
		if solicitud_amistad_id:
			solicitud_amistad = SolicitudAmistad.objects.get(pk=solicitud_amistad_id)
			if solicitud_amistad.destinatario == user:
				if solicitud_amistad: 
					notificacion_actualizada = solicitud_amistad.rechazar()
					payload['response'] = "Solicitud de amistad rechazada."
				else:
					payload['response'] = "Algo ha ido mal."
			else:
				payload['response'] = "Esa solicitud de amistad no es para tí."
		else:
			payload['response'] = "No se pudo rechazar la solicitud de amistad."
	else:
		payload['response'] = "Debes estar autenticado para rechazar una solicitud de amistad."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def cancelar_solicitud_amistad(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("destinatario_user_id")
		if user_id:
			destinatario = Cuenta.objects.get(pk=user_id)
			try:
				solicitudes_amistad = SolicitudAmistad.objects.filter(remitente=user, destinatario=destinatario, is_active=True)
			except SolicitudAmistad.DoesNotExist:
				payload['response'] = "La solicitud de amistad no existe."

			if len(solicitudes_amistad) > 1:
				for request in solicitudes_amistad:
					request.cance()
				payload['response'] = "Solicitud de amistad cancelada."
			else:
				solicitudes_amistad.first().cancelar()
				payload['response'] = "Solicitud de amistad cancelada."
		else:
			payload['response'] = "No se pudo cancelar la solicitud de amistad."
	else:
		payload['response'] = "Debes estar autenticado para cancelar una solicitud de amistad."
	return HttpResponse(json.dumps(payload), content_type="application/json")
























