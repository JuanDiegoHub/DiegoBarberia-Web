from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_barbero, name='dashboard_barbero'),
    path('citas/', views.mis_citas_barbero, name='mis_citas_barbero'),
    path('horario/', views.mi_horario_barbero, name='mi_horario_barbero'),
]