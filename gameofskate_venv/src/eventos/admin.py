from django.contrib import admin

from eventos.models import Evento, SolicitudEvento, ListaEventos

class EventoAdmin(admin.ModelAdmin):
    list_filter = ['nombre']
    list_display = ['nombre']
    search_fields = ['nombre', 'creador__username', 'evento__nombre']

    class Meta:
        model = Evento


admin.site.register(Evento, EventoAdmin)

class ListaEventosAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user',]

    class Meta:
        model = ListaEventos


admin.site.register(ListaEventos, ListaEventosAdmin)


class SolicitudEventoAdmin(admin.ModelAdmin):
    list_filter = ['remitente', 'destinatario']
    list_display = ['remitente', 'destinatario',]
    search_fields = ['remitente__username', 'destinatario__username']

    class Meta:
        model = SolicitudEvento


admin.site.register(SolicitudEvento, SolicitudEventoAdmin)