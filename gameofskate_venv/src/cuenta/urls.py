from django.urls import path

from cuenta.views import (
	cuenta_view,
	editar_cuenta_view,
	eliminar_cuenta,
)

app_name = 'cuenta'

urlpatterns = [
	path('<user_id>/', cuenta_view, name="view"),
	path('<user_id>/editar/', editar_cuenta_view, name="editar"),
	path('eliminar_cuenta/<user_id>/', eliminar_cuenta, name='eliminar-cuenta'),
]