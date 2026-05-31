# landing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Esta es la ruta raíz de la landing page (ej: www.tudominio.com/)
    path('', views.index_view, name='landing_index'),
    path('ajax/servicios/', views.obtener_servicios_por_sede, name='ajax_servicios'),
    path('ajax/horarios-dia/', views.obtener_horarios_dia, name='horarios_dia'),
    path('ajax/barberos/', views.obtener_barberos_por_sede, name='ajax_barberos'),
    path('ajax/citas-ocupadas/', views.obtener_citas_ocupadas, name='citas_ocupadas'),
    path('ajax/eventos-calendario/', views.obtener_eventos_calendario, name='eventos_calendario'),
    path('ajax/verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('ajax/crear-cita-pendiente/', views.crear_cita_pendiente, name='crear_cita_pendiente'),
    path('ajax/confirmar-codigo-otp/', views.confirmar_codigo_otp, name='confirmar_codigo_otp'),
    path('ajax/cancelar-reserva-pendiente/', views.cancelar_reserva_pendiente, name='cancelar_reserva_pendiente'),
]
