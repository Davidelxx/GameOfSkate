from django.db import models
from django.conf import settings
from django.utils import timezone


class ListaAmigos(models.Model):
	user	= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
	amigos	= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="amigos") 

	def __str__(self):
		return self.user.username

	def anadir_amigo(self, cuenta):
		if not cuenta in self.amigos.all():
			self.amigos.add(cuenta)
			self.save()

	def eliminar_amigo(self, cuenta):
		if cuenta in self.amigos.all():
			self.amigos.remove(cuenta)

	def actualizar_listas_amigos(self, eliminado):
		lista_amigos_propia = self

		lista_amigos_propia.eliminar_amigo(eliminado)

		lista_amigos_ajena = ListaAmigos.objects.get(user=eliminado)
		lista_amigos_ajena.eliminar_amigo(lista_amigos_propia.user)

	def son_amigos(self, amigo):
		if amigo in self.amigos.all():
			return True
		return False


class SolicitudAmistad(models.Model):
	remitente		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="remitente")
	destinatario	= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="destinatario")
	is_active		= models.BooleanField(blank=False, null=False, default=True)
	timestamp		= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.remitente.username

	def aceptar(self):
		destinatario_lista_amigos = ListaAmigos.objects.get(user=self.destinatario)
		if destinatario_lista_amigos:
			destinatario_lista_amigos.anadir_amigo(self.remitente)
			remitente_lista_amigos = ListaAmigos.objects.get(user=self.remitente)
			if remitente_lista_amigos:
				remitente_lista_amigos.anadir_amigo(self.destinatario)
				self.is_active = False
				self.save()

	def rechazar(self):
		self.is_active = False
		self.save()

	def cancelar(self):
		self.is_active = False
		self.save()



















