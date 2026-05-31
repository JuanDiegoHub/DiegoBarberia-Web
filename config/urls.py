"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from gestion import views # Asegúrate de que esto esté bien

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('barberos/', views.lista_barberos, name='lista_barberos'),
    path('barberos/nuevo/', views.crear_barbero, name='crear_barbero'),
    path('barberos/editar/<int:pk>/', views.editar_barbero, name='editar_barbero'),
    path('barberos/vacaciones/<int:pk>/', views.vacaciones_barbero_logico, name='vacaciones_barbero'),
    path('barberos/eliminar/<int:pk>/', views.eliminar_barbero_definitivo, name='eliminar_barbero_definitivo'),
    path('barberos/activar/<int:pk>/', views.activar_barbero, name='activar_barbero'),
    path('barbero/', include('panel_barbero.urls')),
    path('administradores/', views.lista_administradores, name='lista_administradores'),
    path('administradores/nuevo/', views.crear_administrador_sede, name='crear_admin'),
    path('sedes/nueva/', views.crear_sede, name='crear_sede'),
    path('admins/editar/<int:sede_id>/', views.editar_admin, name='editar_admin'),
    path('admins/eliminar/<int:sede_id>/', views.quitar_admin, name='quitar_admin'),
    path('admins/asignar/', views.asignar_admin_sede, name='asignar_admin_sede'),
    path('admins/eliminar-total/<int:sede_id>/', views.eliminar_administrador_total, name='eliminar_admin_total'),
    path('citas/', views.citas_globales_view, name='citas_globales'),
    path('citas/cambiar-estado/<int:cita_id>/<str:nuevo_estado>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
    path('horarios/', views.horarios_view, name='horarios_sede'),
    path('servicios/', views.lista_servicios, name='servicios_list'),
    path('servicios/nuevo/', views.crear_servicio, name='crear_servicio'),
    path('servicios/editar/<int:pk>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:pk>/', views.eliminar_servicio, name='eliminar_servicio'),
] 

# ESTA ES LA CLAVE: Debe estar FUERA de los corchetes, al final del archivo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)