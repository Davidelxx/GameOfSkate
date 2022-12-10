from django.shortcuts import render, redirect
from django.http import HttpResponse

from eventos.models import Evento, ListaEventos, SolicitudEvento
from eventos.utils import get_solicitudes_evento
from eventos.estado_solicitud_evento import EstadoSolicitudEvento

from amistad.models import ListaAmigos, SolicitudAmistad
from cuenta.models import Cuenta

import json

def lista_eventos_view(request, *args, **kwargs):
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
                lista_eventos = ListaEventos.objects.get(user=this_user)
            except ListaEventos.DoesNotExist:
                return HttpResponse(f"No se encontró una lista de eventos para {this_user.username}")
			
            if user != this_user:
                lista_amigos = ListaAmigos.objects.get(user=this_user)
                if not user in lista_amigos.amigos.all():
                    return HttpResponse("No puedes ver la lista de eventos de este usuario porque no sois amigos.")

            eventos_en_curso = []
            eventos_pendientes = []
            eventos_finalizados = []
            auth_user_lista_eventos = ListaEventos.objects.get(user=user)
            for evento in lista_eventos.eventos.all():
                if evento.en_curso:
                    eventos_en_curso.append(evento)
                elif evento.finalizado:
                    eventos_finalizados.append(evento)
                else:
                    eventos_pendientes.append(evento)
                    
            context['eventos_en_curso'] = eventos_en_curso
            context['eventos_pendientes'] = eventos_pendientes
            context['eventos_finalizados'] = eventos_finalizados
    else:		
        return redirect("login")
    return render(request, "eventos/lista_eventos.html", context)


def crear_evento(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated: 
        context = {}
        if request.POST:
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            participantes = request.POST.getlist('participantes')
            evento = Evento.objects.create(nombre=nombre, creador=user, descripcion=descripcion)
            evento.participantes.add(user)
            evento.save()
            lista_eventos = ListaEventos.objects.get(user=user)
            lista_eventos.eventos.add(evento)
            lista_eventos.save()

            for participante in participantes:
                cuenta = Cuenta.objects.get(pk=participante)
                solicitud_evento = SolicitudEvento.objects.create(evento=evento, remitente=user, destinatario=cuenta)
                solicitud_evento.save()

            return redirect('home')
        else:
            amigos = []
            lista_amigos = ListaAmigos.objects.get(user=user)
            for amigo in lista_amigos.amigos.all():
                amigos.append(amigo)
            context['amigos'] = amigos
    else:
        redirect("login")

    return render(request, 'eventos/crear_evento.html', context)



def solicitudes_eventos(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		cuenta = Cuenta.objects.get(pk=user_id)
		if cuenta == user:
			solicitudes_eventos = SolicitudEvento.objects.filter(destinatario=cuenta, is_active=True)
			context['solicitudes_eventos'] = solicitudes_eventos
		else:
			return HttpResponse("No puedes ver las invitaciones a eventos de otros usuarios")
	else:
		redirect("login")
	return render(request, "eventos/solicitudes_eventos.html", context)


def aceptar_solicitud_evento(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		solicitud_evento_id = kwargs.get("solicitud_evento_id")
		if solicitud_evento_id:
			solicitud_evento = SolicitudEvento.objects.get(pk=solicitud_evento_id)
			if solicitud_evento.destinatario == user:
				if solicitud_evento: 
					notificacion_actualizada = solicitud_evento.aceptar()
					payload['response'] = "Invitación a evento aceptada."

				else:
					payload['response'] = "Algo ha ido mal."
			else:
				payload['response'] = "Esa invitación a evento no es para tí."
		else:
			payload['response'] = "No se pudo aceptar la invitación a evento."
	else:
		payload['response'] = "Debes estar autenticado para aceptar una invitación a evento."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def rechazar_solicitud_evento(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		solicitud_evento_id = kwargs.get("solicitud_evento_id")
		if solicitud_evento_id:
			solicitud_evento = SolicitudEvento.objects.get(pk=solicitud_evento_id)
			if solicitud_evento.destinatario == user:
				if solicitud_evento: 
					notificacion_actualizada = solicitud_evento.rechazar()
					payload['response'] = "Invitación a evento rechazada."
				else:
					payload['response'] = "Algo ha ido mal."
			else:
				payload['response'] = "Esa invitación a evento no es para tí."
		else:
			payload['response'] = "No se pudo rechazar la invitación a evento."
	else:
		payload['response'] = "Debes estar autenticado para rechazar una invitación a evento."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def evento_view(request, *args, **kwargs):
    context = {}
    user = request.user
    context['user'] = user
    if user.is_authenticated:
        evento_id = kwargs.get("evento_id")
        if evento_id:
            try:
                evento = Evento.objects.get(id=evento_id)
            except Evento.DoesNotExist:
                return HttpResponse("El evento no existe.")
        else:
            return HttpResponse("Algo ha ido mal.")

        if request.method == "GET":
            context['evento'] = evento
            if user == evento.creador:
                es_creador = True
            else:
                es_creador = False
            context['es_creador'] = es_creador

            context['participantes'] = []
            for participante in evento.participantes.all():
                context['participantes'].append(participante)

            num_invitaciones_pendientes = SolicitudEvento.objects.filter(evento=evento).count() - evento.participantes.all().count() + 1
            context['num_invitaciones_pendientes'] = num_invitaciones_pendientes
        
        else:
            ganador_id = request.POST['ganador']
            ganador = Cuenta.objects.get(pk=ganador_id)
            best_trick = request.POST['best_trick']
            evento.finalizar(ganador, best_trick)
    else:
        return redirect("login")

    return render(request, "eventos/evento.html", context)


def comenzar_evento(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        evento_id = kwargs.get('evento_id')
        evento = Evento.objects.get(id=evento_id)
        evento.comenzar()
    else:
        return redirect("login")
        
    return redirect('../../evento/'+evento_id)

def eliminar_evento(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        evento_id = kwargs.get('evento_id')
        evento = Evento.objects.get(id=evento_id)
        evento.eliminar()
    else:
        return redirect("login")
        
    return redirect('../../../cuenta/'+str(user.pk))
