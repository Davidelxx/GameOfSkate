from django.db import models
from django.conf import settings
from django.utils import timezone

class Evento(models.Model):
    id              = models.AutoField(primary_key=True)
    nombre          = models.CharField(max_length=30)
    descripcion     = models.CharField(max_length=140, null=True, blank=True)
    creador         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="creador")
    participantes   = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="participantes")
    en_curso        = models.BooleanField(default=False)
    finalizado      = models.BooleanField(default=False)
    ganador         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="ganador")
    best_trick      = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.nombre
        
    def comenzar(self):
        self.en_curso = True
        self.save()
        solicitudes_pendientes = SolicitudEvento.objects.filter(evento=self)
        if solicitudes_pendientes:
            for solicitud in solicitudes_pendientes.all():
                if solicitud.is_active:
                    solicitud.is_active = False
                    solicitud.save()

    def finalizar(self, ganador, best_trick):
        self.ganador = ganador
        self.best_trick = best_trick
        self.en_curso = False
        self.finalizado = True
        self.save()

    def eliminar(self):
        self.delete()


class ListaEventos(models.Model):
    user	= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evento_user")
    eventos = models.ManyToManyField("eventos.Evento", related_name="eventos")

    def __str__(self):
        return self.user.username

    def anadir_evento(self, evento, user):
        if not evento in self.eventos.all():
            self.eventos.add(evento)
            self.save()
            evento = Evento.objects.get(id=evento.id)
            evento.participantes.add(user)
            evento.save()

    def eliminar_evento(self, evento):
        if evento in self.eventos.all():
            self.eventos.remove(evento)

    def actualizar_listas_eventos(self, evento, participantes):
        self.eliminar_evento(evento)

        for participante in participantes:
            lista_eventos_ajena = ListaEventos.objects.get(user=participante)
            lista_eventos_ajena.eliminar_evento(evento)

    def existe_evento(self, evento):
        if evento in self.eventos.all():
            return True
        return False 

class SolicitudEvento(models.Model):
    evento	    	= models.ForeignKey("eventos.Evento", on_delete=models.CASCADE, related_name=("evento_solicitud"))
    remitente	    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evento_remitente")
    destinatario	= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="evento_destinatario")
    is_active		= models.BooleanField(blank=False, null=False, default=True)
    timestamp		= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.remitente.username

    def aceptar(self):
        destinatario_lista_eventos = ListaEventos.objects.get(user=self.destinatario)

        if destinatario_lista_eventos:
            destinatario_lista_eventos.anadir_evento(self.evento, self.destinatario)
            self.is_active = False
            self.save()

    def rechazar(self):
        self.is_active = False
        self.save()

    def cancelar(self):
        self.is_active = False
        self.save()
