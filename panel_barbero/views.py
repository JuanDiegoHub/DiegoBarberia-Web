from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from .decorators import barbero_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from gestion.models import Cita, HorarioBarbero, Barbero
from gestion.views import auto_completar_citas

@login_required
def dashboard_barbero(request):
    try:
        barbero = request.user.barbero
    except Barbero.DoesNotExist:
        return redirect('login')

    auto_completar_citas()

    hoy = timezone.now().date()
    
    # Filtramos: Solo sus citas Y que sean de hoy
    citas_hoy = Cita.objects.filter(
        barbero=barbero, 
        fecha=hoy
    ).order_by('hora')

    context = {
        'barbero': barbero,
        'citas_hoy': citas_hoy,
        'total_hoy': citas_hoy.count(),
    }
    return render(request, 'panel_barbero/dashboard.html', context)

@barbero_required
def mis_citas_barbero(request):
    try:
        barbero = request.user.barbero
    except Barbero.DoesNotExist:
        return redirect('login')
        
    auto_completar_citas()

    citas = Cita.objects.filter(barbero=barbero)
    
    # Filters
    fecha_filtro = request.GET.get('fecha')
    estado_filtro = request.GET.get('estado')
    
    if fecha_filtro:
        citas = citas.filter(fecha=fecha_filtro)
    if estado_filtro:
        citas = citas.filter(estado=estado_filtro)
        
    citas = citas.order_by('-fecha', '-hora')
    
    context = {
        'barbero': barbero,
        'citas': citas,
        'fecha_filtro': fecha_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'panel_barbero/mis_citas.html', context)

@barbero_required
def mi_horario_barbero(request):
    barbero = request.user.barbero
    # Get or create daily records if they don't exist
    for i in range(7):
        HorarioBarbero.objects.get_or_create(
            barbero=barbero,
            dia_semana=i,
            defaults={
                'hora_entrada': '08:00',
                'hora_salida': '20:00',
                'inicio_almuerzo': '12:00',
                'fin_almuerzo': '13:00',
                'dia_descanso': False
            }
        )
        
    horarios = HorarioBarbero.objects.filter(barbero=barbero).order_by('dia_semana')
    
    context = {
        'barbero': barbero,
        'horarios': horarios,
    }
    return render(request, 'panel_barbero/mi_horario.html', context)