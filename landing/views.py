from .utils import enviar_whatsapp_otp, enviar_whatsapp_confirmacion_cliente
# landing/views.py
from django.shortcuts import render
from django.http import JsonResponse
from gestion.models import Barbero, Cita, Sede, Servicio, HorarioSede, HorarioBarbero
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
import json
import random
from datetime import timedelta, datetime, time
from django.utils import timezone

def liberar_citas_pendientes():
    limite = timezone.now() - timedelta(minutes=10)
    Cita.objects.filter(estado='Pendiente', fecha_creacion__lte=limite).delete()

def index_view(request):
    liberar_citas_pendientes()
    # Traemos todas las sedes registradas en la base de datos
    sedes = Sede.objects.all() 
    
    context = {
        'sedes': sedes,  # Esta es la variable que el HTML usará en el {% for %}
    }
    return render(request, 'landing/index.html', context)



def obtener_barberos_por_sede(request):
    sede_id = request.GET.get('sede_id')
    barberos_db = Barbero.objects.filter(sede_id=sede_id, estado='activo') # Filtramos solo activos
    
    # Creamos una lista manual para estructurar bien el JSON
    lista_barberos = []
    for barber in barberos_db:
        # Obtenemos la URL de la imagen si existe, sino una por defecto
        if barber.imagen:
            imagen_url = barber.imagen.url
        else:
            # Asegúrate de tener una imagen por defecto en static/landing/img/
            imagen_url = '/static/landing/img/default-avatar.png'
            
        lista_barberos.append({
            'id': barber.id,
            'nombre': barber.nombre,
            'imagen_url': imagen_url, # <--- ENVIAMOS LA URL DE LA IMAGEN
        })
        
    return JsonResponse(lista_barberos, safe=False)
 # Asegúrate de importar tu modelo Cita

def obtener_citas_ocupadas(request):
    barbero_id = request.GET.get('barbero_id')
    # Traemos solo citas confirmadas o pendientes (que bloquean el horario)
    citas = Cita.objects.filter(
        barbero_id=barbero_id, 
        estado__in=['Confirmada', 'Pendiente']
    )
    
    eventos = []
    for cita in citas:
        # Combinamos fecha y hora para el formato ISO de FullCalendar
        start_datetime = f"{cita.fecha}T{cita.hora}"
        eventos.append({
            'title': 'Ocupado',
            'start': start_datetime,
            'color': '#ef4444', # Rojo para indicar ocupado
            'display': 'background' # Sombrea la casilla en rojo
        })
    
    return JsonResponse(eventos, safe=False)

def obtener_eventos_calendario(request):
    barbero_id = request.GET.get('barbero_id')
    
    # 1. Obtener Citas (Ocupadas y Pendientes)
    citas = Cita.objects.filter(barbero_id=barbero_id)
    eventos = []
    
    for cita in citas:
        color = '#ef4444' if cita.estado == 'Confirmada' else '#f59e0b' # Rojo vs Naranja (Pendiente)
        eventos.append({
            'id': f"cita_{cita.id}",
            'title': 'Ocupado' if cita.estado == 'Confirmada' else 'En proceso...',
            'start': f"{cita.fecha}T{cita.hora}",
            'color': color,
            'extendedProps': {'tipo': 'cita'}
        })

    # 2. Obtener Horarios de Descanso (Comentado ya que no existe modelo HorarioDescanso)
    # descansos = HorarioDescanso.objects.filter(barbero_id=barbero_id)
    # for d in descansos:
    #     eventos.append({
    #         'title': 'No Disponible',
    #         'start': f"{d.fecha}T{d.hora_inicio}",
    #         'end': f"{d.fecha}T{d.hora_fin}",
    #         'color': '#374151', # Gris oscuro para descansos
    #         'display': 'background',
    #         'extendedProps': {'tipo': 'descanso'}
    #     })
        
    return JsonResponse(eventos, safe=False)

def verificar_disponibilidad(request):
    fecha_hora_str = request.GET.get('fecha_hora')
    barbero_id = request.GET.get('barbero_id')
    
    # El string viene como 2026-03-31T12:00:00-05:00
    fecha_str = fecha_hora_str.split('T')[0]
    hora_str = fecha_hora_str.split('T')[1][:8]

    existe = Cita.objects.filter(
        barbero_id=barbero_id,
        fecha=fecha_str,
        hora=hora_str,
        estado__in=['Confirmada', 'Pendiente']
    ).exists()

    return JsonResponse({'disponible': not existe})

def obtener_servicios_por_sede(request):
    sede_id = request.GET.get('sede_id')
    servicios_db = Servicio.objects.filter(sede_id=sede_id, activo=True)
    lista_servicios = []
    for s in servicios_db:
        lista_servicios.append({
            'id': s.id,
            'nombre': s.nombre,
            'precio': str(s.precio),
            'duracion': s.duracion_minutos
        })
    return JsonResponse(lista_servicios, safe=False)

def obtener_horarios_dia(request):
    liberar_citas_pendientes()
    
    barbero_id = request.GET.get('barbero_id')
    fecha = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio_id')
    
    if not barbero_id or not fecha:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
        
    try:
        barbero = Barbero.objects.get(id=barbero_id)
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except (Barbero.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Barbero o fecha inválida'}, status=400)
        
    servicio = None
    if servicio_id:
        try:
            servicio = Servicio.objects.get(id=servicio_id, activo=True)
        except Servicio.DoesNotExist:
            pass
            
    dia_semana = fecha_obj.weekday()
    
    # 1. Validar horario de la sede
    horario_sede, _ = HorarioSede.objects.get_or_create(
        sede=barbero.sede,
        dia_semana=dia_semana,
        defaults={
            'hora_apertura': time(8, 0),
            'hora_cierre': time(20, 0),
            'cerrado': False
        }
    )
    if horario_sede.cerrado:
        return JsonResponse({'slots': [], 'mensaje': 'La sede se encuentra cerrada este día.'})
        
    # 2. Validar horario del barbero
    horario_barbero, _ = HorarioBarbero.objects.get_or_create(
        barbero=barbero,
        dia_semana=dia_semana,
        defaults={
            'hora_entrada': time(8, 0),
            'hora_salida': time(20, 0),
            'dia_descanso': False
        }
    )
    if horario_barbero.dia_descanso:
        return JsonResponse({'slots': [], 'mensaje': 'El barbero seleccionado tiene día de descanso.'})
        
    # 3. Auxiliares para tiempo a minutos
    def time_to_minutes(t):
        if isinstance(t, str):
            parts = t.split(':')
            return int(parts[0]) * 60 + int(parts[1])
        return t.hour * 60 + t.minute
        
    entrada_mins = time_to_minutes(horario_barbero.hora_entrada)
    salida_mins = time_to_minutes(horario_barbero.hora_salida)
    apertura_mins = time_to_minutes(horario_sede.hora_apertura)
    cierre_mins = time_to_minutes(horario_sede.hora_cierre)
    
    start_mins = max(entrada_mins, apertura_mins)
    end_mins = min(salida_mins, cierre_mins)
    
    almuerzo_start = time_to_minutes(horario_barbero.inicio_almuerzo) if horario_barbero.inicio_almuerzo else None
    almuerzo_end = time_to_minutes(horario_barbero.fin_almuerzo) if horario_barbero.fin_almuerzo else None
    
    duracion = servicio.duracion_minutos if servicio else 40
    
    # 4. Obtener citas existentes
    citas_db = Cita.objects.filter(barbero=barbero, fecha=fecha_obj, estado__in=['Confirmada', 'Pendiente'])
    citas_intervalos = []
    for c in citas_db:
        c_start = time_to_minutes(c.hora)
        c_dur = c.servicio.duracion_minutos if c.servicio else 40
        c_end = c_start + c_dur
        citas_intervalos.append({
            'start': c_start,
            'end': c_end,
            'estado': c.estado
        })
        
    # 5. Generar slots
    slots = []
    current_mins = start_mins
    
    now_local = timezone.localtime()
    es_hoy = (fecha_obj == now_local.date())
    ahora_mins = now_local.hour * 60 + now_local.minute

    while current_mins + duracion <= end_mins:
        # Validar si se cruza con el almuerzo
        es_almuerzo = False
        if almuerzo_start is not None and almuerzo_end is not None:
            if not (current_mins + duracion <= almuerzo_start or current_mins >= almuerzo_end):
                es_almuerzo = True
                
        if es_almuerzo:
            current_mins += 40
            continue
            
        # Validar si se cruza con citas
        estado_slot = 'Disponible'
        for cita_int in citas_intervalos:
            if not (current_mins + duracion <= cita_int['start'] or current_mins >= cita_int['end']):
                if cita_int['estado'] == 'Confirmada':
                    estado_slot = 'Ocupado'
                else:
                    estado_slot = 'Pendiente'
                break
                
        # Validar si la hora ya pasó (solo para hoy)
        if es_hoy and current_mins <= ahora_mins:
            estado_slot = 'Pasado'
                
        h = current_mins // 60
        m = current_mins % 60
        time_str = f"{h:02d}:{m:02d}"
        
        suffix = 'am' if h < 12 else 'pm'
        h_12 = h if h <= 12 else h - 12
        if h_12 == 0:
            h_12 = 12
        time_display = f"{h_12}:{m:02d} {suffix}"
        
        slots.append({
            'hora': time_str,
            'hora_formateada': time_display,
            'estado': estado_slot
        })
        
        current_mins += 40
        
    return JsonResponse({'slots': slots})

import re

@require_POST
def crear_cita_pendiente(request):
    # 1. Rate Limit por IP (10 por hora)
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f"citas_ip_{ip}"
    intentos_ip = cache.get(cache_key, 0)
    
    if intentos_ip >= 10:
        return JsonResponse({'success': False, 'message': 'Has superado el límite de intentos por hora. Por favor, intenta más tarde.'})
    
    cache.set(cache_key, intentos_ip + 1, timeout=3600)

    data = json.loads(request.body)
        
    telefono = data.get('telefono')
    # 1. Validar formato del teléfono
    if not telefono or not re.match(r'^\+?1?\d{9,15}$', telefono):
        return JsonResponse({'success': False, 'message': 'Formato de teléfono inválido (debe tener entre 9 y 15 dígitos).'})

    # 2. Rate limiting: máx 3 citas por día para la fecha seleccionada
    fecha_reserva = data.get('fecha')
    citas_del_dia = Cita.objects.filter(
        telefono=telefono,
        fecha=fecha_reserva
    ).exclude(estado='Cancelada').count()
    
    if citas_del_dia >= 3:
        return JsonResponse({
            'success': False, 
            'limite_excedido': True,
            'message': 'Has alcanzado el límite de 3 citas por día para este número. Si deseas agendar más, contáctanos directamente.'
        })

    # 3. Validar si el cliente ya tiene una cita agendada a esa misma hora
    hora_reserva = data.get('hora')
    cita_misma_hora = Cita.objects.filter(
        telefono=telefono,
        fecha=fecha_reserva,
        hora=hora_reserva
    ).exclude(estado__in=['Cancelada', 'No_Asistio']).exists()

    if cita_misma_hora:
        return JsonResponse({
            'success': False, 
            'message': 'Ya tienes una cita agendada a esta misma hora con otro barbero. Por favor, selecciona un horario diferente.'
        })

    # Generar un código aleatorio de 6 dígitos
    codigo = str(random.randint(100000, 999999))
    
    try:
        barbero = Barbero.objects.get(id=data['barbero_id'])
        
        # Buscar el servicio
        servicio_id = data.get('servicio_id')
        servicio = None
        if servicio_id:
            try:
                servicio = Servicio.objects.get(id=servicio_id, activo=True)
            except Servicio.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'El servicio seleccionado no está activo o no existe.'})

        # Creamos la cita en estado Pendiente
        cita = Cita.objects.create(
            barbero=barbero,
            servicio=servicio,
            fecha=data['fecha'],
            hora=data['hora'],
            telefono=telefono,
            cliente_nombre=data.get('nombre', 'Cliente'),
            codigo_verificacion=codigo,
            estado='Pendiente'
        )
        
        respuesta_wa = enviar_whatsapp_otp(telefono, codigo)
        
        if respuesta_wa is None or respuesta_wa.get('error'):
            # Eliminar cita porque no se pudo enviar el mensaje
            cita.delete()
            error_msg = respuesta_wa.get('error') if respuesta_wa else 'Error de conexión con el servidor de WhatsApp (UltraMsg).'
            return JsonResponse({'success': False, 'message': f'No se pudo enviar el código por WhatsApp. Detalle: {error_msg}'})
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@require_POST
def confirmar_codigo_otp(request):
    data = json.loads(request.body)
    telefono = data.get('telefono')
    codigo_ingresado = data.get('codigo')
        
    try:
        # Buscamos la última cita pendiente de ese teléfono
        cita = Cita.objects.filter(telefono=telefono, estado='Pendiente').latest('fecha_creacion')
        
        # Validar expiración (10 minutos)
        if timezone.now() - cita.fecha_creacion > timedelta(minutes=10):
            cita.delete()
            return JsonResponse({'verificado': False, 'message': 'El código OTP ha expirado (límite de 10 minutos). Por favor solicita una nueva cita.'})

        if cita.codigo_verificacion == codigo_ingresado:
            cita.estado = 'Confirmada'
            cita.verificado = True
            cita.save()
            enviar_whatsapp_confirmacion_cliente(cita)
            return JsonResponse({'verificado': True})
        else:
            cita.intentos_verificacion += 1
            cita.save()
            if cita.intentos_verificacion >= 3:
                cita.delete()
                return JsonResponse({'verificado': False, 'message': 'Demasiados intentos fallidos. Tu reserva ha sido eliminada por seguridad.'})
            return JsonResponse({'verificado': False, 'message': f'Código incorrecto. Te quedan {3 - cita.intentos_verificacion} intentos.'})
            
    except Cita.DoesNotExist:
        return JsonResponse({'verificado': False, 'message': 'No se encontró una reserva pendiente'})

@require_POST
def cancelar_reserva_pendiente(request):
    data = json.loads(request.body)
    telefono = data.get('telefono')
    barbero_id = data.get('barbero_id')
    fecha = data.get('fecha')
    hora = data.get('hora')
    
    if telefono and barbero_id and fecha and hora:
        citas_a_borrar = Cita.objects.filter(
            telefono=telefono, 
            barbero_id=barbero_id,
            fecha=fecha,
            hora=hora,
            estado='Pendiente'
        )
        citas_a_borrar.delete()
        return JsonResponse({'status': 'eliminada'})
        
    return JsonResponse({'status': 'no_data'}, status=400)