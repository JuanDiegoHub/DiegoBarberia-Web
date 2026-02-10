import calendar
from django.shortcuts import render
from .models import sede # Asegúrate de importar tu modelo Sede
from django.http import JsonResponse
from .models import Usuario, sede
from datetime import datetime

from django.http import JsonResponse
from .models import Usuario
from inicio.models import Barbero  # <--- Importamos el modelo donde SÍ están las fotos

def obtener_barberos_por_sede(request):
    sede_id = request.GET.get('sede_id')
    
    # 1. Buscamos los usuarios con rol barbero en esa sede
    usuarios_barberos = Usuario.objects.filter(role='barbero', sede_id=sede_id)
    
    data = []
    for u in usuarios_barberos:
        # 2. Intentamos buscar su foto en el modelo Barbero de la app 'inicio'
        # Buscamos por nombre (o por el campo que compartan)
        info_extra = Barbero.objects.filter(nombre__icontains=u.first_name).first()
        
        foto_url = '/static/inicio/img/default-barber.png'
        if info_extra and info_extra.foto:
            foto_url = info_extra.foto.url

        data.append({
            'id': u.id,
            'nombre': f"{u.first_name} {u.last_name}" if u.first_name else u.username,
            'url_foto': foto_url
        })
    
    return JsonResponse(data, safe=False)
def reservar_cita(request):
    sedes = sede.objects.all()
    hoy = datetime.now()
    
    # Obtenemos los días del mes actual
    # monthrange devuelve (dia_semana_donde_empieza, numero_de_dias)
    _, num_dias = calendar.monthrange(hoy.year, hoy.month)
    dias_del_mes = range(1, num_dias + 1)

    return render(request, 'usuarios/reservar_cita.html', {
        'sedes': sedes,
        'dias_del_mes': dias_del_mes,
        'mes_nombre': hoy.strftime('%B'), # Nombre del mes en inglés (luego lo traducimos)
        'anio': hoy.year
    })