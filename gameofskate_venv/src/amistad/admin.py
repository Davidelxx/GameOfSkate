from django.contrib import admin

from amistad.models import ListaAmigos, SolicitudAmistad


class ListaAmigosAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user',]

    class Meta:
        model = ListaAmigos


admin.site.register(ListaAmigos, ListaAmigosAdmin)


class SolicitudAmistadAdmin(admin.ModelAdmin):
    list_filter = ['remitente', 'destinatario']
    list_display = ['remitente', 'destinatario',]
    search_fields = ['remitente__username', 'destinatario__username']

    class Meta:
        model = SolicitudAmistad


admin.site.register(SolicitudAmistad, SolicitudAmistadAdmin)












