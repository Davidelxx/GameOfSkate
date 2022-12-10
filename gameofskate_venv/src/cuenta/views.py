from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.conf import settings

from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core import files
import os
import base64
import json

from cuenta.forms import RegistrationForm, CuentaAuthenticationForm, ActualizarCuentaForm
from cuenta.models import Cuenta
from amistad.utils import get_solicitudes_amistad
from amistad.estado_solicitud_amistad import EstadoSolicitudAmistad
from amistad.models import ListaAmigos, SolicitudAmistad

from eventos.utils import get_solicitudes_evento
from eventos.estado_solicitud_evento import EstadoSolicitudEvento
from eventos.models import ListaEventos, SolicitudEvento


TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


def buscar_usuarios_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated:
		context = {}
		if request.method == "GET":
			busqueda = request.GET.get("q")
			if len(busqueda) > 0:
				resultados = Cuenta.objects.filter(email__icontains=busqueda).filter(username__icontains=busqueda).distinct()
				cuentas = []
				lista_amigos = ListaAmigos.objects.get(user=user)
				for cuenta in resultados:
					cuentas.append((cuenta, lista_amigos.son_amigos(cuenta)))
				context['cuentas'] = cuentas
	else:
		return redirect("login")
				
	return render(request, "cuenta/resultados_busqueda.html", context)



def register_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated: 
		return HttpResponse("Ya estás autenticado como " + str(user.email))

	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			cuenta = authenticate(email=email, password=raw_password)
			login(request, cuenta)
			destino = kwargs.get("next")
			if destino:
				return redirect(destino)
			return redirect('home')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'cuenta/register.html', context)


def logout_view(request):
	logout(request)
	return redirect("home")


def login_view(request, *args, **kwargs):
	context = {}

	user = request.user
	if user.is_authenticated: 
		return redirect("home")

	destino = get_redirect_if_exists(request)

	if request.POST:
		form = CuentaAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				if destino:
					return redirect(destino)
				return redirect("home")

	else:
		form = CuentaAuthenticationForm()

	context['login_form'] = form

	return render(request, "cuenta/login.html", context)


def get_redirect_if_exists(request):
	redirect = None
	if request.GET:
		if request.GET.get("next"):
			redirect = str(request.GET.get("next"))
	return redirect


def cuenta_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated:
		context = {}
		user_id = kwargs.get("user_id")
		try:
			cuenta = Cuenta.objects.get(pk=user_id)
		except:
			return HttpResponse("Algo ha ido mal.")
		if cuenta:
			context['id'] = cuenta.id
			context['username'] = cuenta.username
			context['email'] = cuenta.email
			context['profile_image'] = cuenta.profile_image.url
			context['hide_email'] = cuenta.hide_email

			try:
				lista_amigos = ListaAmigos.objects.get(user=cuenta)
			except ListaAmigos.DoesNotExist:
				lista_amigos = ListaAmigos(user=cuenta)
				lista_amigos.save()
			amigos = lista_amigos.amigos.all()
			context['amigos'] = amigos

			try:
				lista_eventos = ListaEventos.objects.get(user=cuenta)
			except ListaEventos.DoesNotExist:
				lista_eventos = ListaEventos(user=cuenta)
				lista_eventos.save()
			eventos = lista_eventos.eventos.all()
			context['eventos'] = eventos
		
			is_self = True
			is_friend = False
			solicitud_amistad_enviada = EstadoSolicitudAmistad.NO_SOLICITUD.value
			solicitudes_amistad = None
			solicitud_evento_enviada = EstadoSolicitudEvento.NO_SOLICITUD.value
			solicitudes_evento = None
			if user != cuenta:
				is_self = False
				if amigos.filter(pk=user.id):
					is_friend = True
					if get_solicitudes_evento(remitente=cuenta, destinatario=user) != False:
						solicitud_evento_enviada = EstadoSolicitudEvento.SOLICITUD_RECIBIDA.value
						context['solicitud_evento_pendiente_id'] = get_solicitudes_evento(remitente=cuenta, destinatario=user).id
					elif get_solicitudes_evento(remitente=user, destinatario=cuenta) != False:
						solicitud_evento_enviada = EstadoSolicitudEvento.SOLICITUD_ENVIADA.value
					else:
						solicitud_evento_enviada = EstadoSolicitudEvento.NO_SOLICITUD.value
				else:
					is_friend = False
					if get_solicitudes_amistad(remitente=cuenta, destinatario=user) != False:
						solicitud_amistad_enviada = EstadoSolicitudAmistad.SOLICITUD_RECIBIDA.value
						context['solicitud_amistad_pendiente_id'] = get_solicitudes_amistad(remitente=cuenta, destinatario=user).id
					elif get_solicitudes_amistad(remitente=user, destinatario=cuenta) != False:
						solicitud_amistad_enviada = EstadoSolicitudAmistad.SOLICITUD_ENVIADA.value
					else:
						solicitud_amistad_enviada = EstadoSolicitudAmistad.NO_SOLICITUD.value
			else:
				try:
					solicitudes_amistad = SolicitudAmistad.objects.filter(destinatario=user, is_active=True)
					solicitudes_evento = SolicitudEvento.objects.filter(destinatario=user, is_active=True)
				except:
					pass
				
			context['is_self'] = is_self
			context['is_friend'] = is_friend
			context['solicitud_amistad_enviada'] = solicitud_amistad_enviada
			context['solicitudes_amistad'] = solicitudes_amistad
			context['solicitud_evento_enviada'] = solicitud_evento_enviada
			context['solicitudes_evento'] = solicitudes_evento
			context['BASE_URL'] = settings.BASE_URL
	else:
		return redirect("login")

	return render(request, "cuenta/cuenta.html", context)


def editar_cuenta_view(request, *args, **kwargs):
	user = request.user
	if  user.is_authenticated:
		user_id = kwargs.get("user_id")
		cuenta = Cuenta.objects.get(pk=user_id)
		if cuenta.pk != user.pk and not user.is_admin:
			return HttpResponse("No puedes editar el perfil de otra persona.")
		context = {}
		if request.POST:
			form = ActualizarCuentaForm(request.POST, request.FILES, instance=cuenta)
			if form.is_valid():
				form.save()
				return redirect("cuenta:view", user_id=cuenta.pk)
			else:
				form = ActualizarCuentaForm(request.POST, instance=cuenta,
					initial={
						"id": cuenta.pk,
						"email": cuenta.email, 
						"username": cuenta.username,
						"profile_image": cuenta.profile_image,
						"hide_email": cuenta.hide_email,
					}
				)
				context['form'] = form
		else:
			form = ActualizarCuentaForm(
				initial={
						"id": cuenta.pk,
						"email": cuenta.email, 
						"username": cuenta.username,
						"profile_image": cuenta.profile_image,
						"hide_email": cuenta.hide_email,
					}
				)
			context['form'] = form
		context['user_id'] = user_id
	else:
		return redirect("login")
		
	return render(request, "cuenta/editar_cuenta.html", context)


def eliminar_cuenta(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        cuenta = Cuenta.objects.get(id=user_id)
        cuenta.eliminar()
    else:
        return redirect("login")
        
    return redirect("home")
