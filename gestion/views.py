from django.utils import timezone  # Solo deja esta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import Barbero, Cita, Sede, HorarioSede, HorarioBarbero, Servicio
from django.contrib.auth.models import User, Group
from .forms import BarberoForm, ServicioForm
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden


def es_dueno_o_superuser(user):
    if user.is_anonymous:
        return False
    return getattr(user, 'is_superuser', False) or user.groups.filter(name='Dueño').exists()

def login_view(request):
    if request.method == 'POST':
        usuario_input = request.POST.get('username')
        clave_input = request.POST.get('password')
        
        user = authenticate(request, username=usuario_input, password=clave_input)
        
        if user is not None:
            login(request, user)
            
            # --- AQUÍ ESTÁ EL TRUCO ---
            if hasattr(user, 'barbero'):
                # Si tiene perfil de barbero, va a su nueva app
                return redirect('dashboard_barbero')
            else:
                # Si es administrador/dueño, va al dashboard general
                return redirect('dashboard') 
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            
    return render(request, 'gestion/login.html')

def logout_view(request):
    """Cierra la sesión de cualquier perfil (admin, barbero) y redirige al login."""
    logout(request)
    return redirect('login')

# gestion/views.py
from datetime import timedelta

def auto_completar_citas():
    # Buscar citas En_Atencion cuya hora_llegada fue hace más de 2 horas
    limite = timezone.now() - timedelta(hours=2)
    citas_vencidas = Cita.objects.filter(estado='En_Atencion', hora_llegada__lte=limite)
    for cita in citas_vencidas:
        cita.estado = 'Completada'
        cita.save()

@login_required
def dashboard_view(request):
    user = request.user
    hoy = timezone.now().date()
    
    auto_completar_citas()
    
    if es_dueno_o_superuser(user):
        barberos_qs = Barbero.objects.filter(estado__iexact='activo')
        citas_qs = Cita.objects.select_related('barbero', 'servicio', 'barbero__sede').all()
        
        sede_id = request.GET.get('sede')
        if sede_id:
            citas_qs = citas_qs.filter(barbero__sede_id=sede_id)
            
        citas_hoy_qs = citas_qs.filter(fecha=hoy)
        citas_activas_hoy = citas_hoy_qs.filter(estado__in=['Confirmada', 'En_Atencion']).order_by('hora')
        servicios_qs = Servicio.objects.filter(activo=True)
        sedes = Sede.objects.all()
    else:
        mi_sede = Sede.objects.filter(administrador=user).first()
        sedes = None
        if mi_sede:
            barberos_qs = Barbero.objects.filter(sede=mi_sede, estado__iexact='activo')
            citas_qs = Cita.objects.select_related('barbero', 'servicio').filter(barbero__sede=mi_sede)
            citas_hoy_qs = citas_qs.filter(fecha=hoy)
            citas_activas_hoy = citas_hoy_qs.filter(estado__in=['Confirmada', 'En_Atencion']).order_by('hora')
            servicios_qs = Servicio.objects.filter(sede=mi_sede, activo=True)
        else:
            barberos_qs = Barbero.objects.none()
            citas_qs = Cita.objects.none()
            citas_hoy_qs = Cita.objects.none()
            citas_activas_hoy = Cita.objects.none()
            servicios_qs = Servicio.objects.none()

    # Estadísticas de hoy
    citas_hoy_real = citas_hoy_qs.count()
    citas_confirmadas_hoy = citas_hoy_qs.filter(estado='Confirmada').count()
    citas_completadas_hoy = citas_hoy_qs.filter(estado='Completada').count()
    citas_pendientes_hoy = citas_hoy_qs.filter(estado='Pendiente').count()
    
    from django.db.models import Sum
    ingresos_hoy = citas_hoy_qs.filter(estado='Completada').aggregate(total=Sum('servicio__precio'))['total'] or 0
    
    # Gráfico semanal (últimos 7 días)
    import datetime
    inicio_semana = hoy - datetime.timedelta(days=6)
    citas_semana = citas_qs.filter(fecha__gte=inicio_semana, fecha__lte=hoy, estado='Confirmada')
    
    citas_por_dia = {}
    for i in range(7):
        d = inicio_semana + datetime.timedelta(days=i)
        citas_por_dia[d] = 0
        
    for c in citas_semana:
        if c.fecha in citas_por_dia:
            citas_por_dia[c.fecha] += 1
            
    dias_semana_abrev = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    chart_labels = []
    chart_data = []
    for d, count in sorted(citas_por_dia.items()):
        day_label = f"{dias_semana_abrev[d.weekday()]} {d.day}"
        chart_labels.append(day_label)
        chart_data.append(count)

    context = {
        'total_barberos_activos': barberos_qs.count(),
        'total_servicios_activos': servicios_qs.count(),
        'citas_hoy_real': citas_hoy_real,
        'citas_confirmadas_hoy': citas_confirmadas_hoy,
        'citas_completadas_hoy': citas_completadas_hoy,
        'citas_pendientes_hoy': citas_pendientes_hoy,
        'ingresos_hoy': ingresos_hoy,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'citas_activas_hoy': citas_activas_hoy,
        'sedes': sedes,
        'sede_seleccionada': request.GET.get('sede', ''),
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def lista_barberos(request):
    if es_dueno_o_superuser(request.user):
        barberos = Barbero.objects.all()
    else:
        # Accedemos directamente a la sede que administra el usuario
        try:
            # 'sede_administrada' es el related_name que tienes en el modelo Sede
            sede_de_la_admin = request.user.sede_administrada 
            barberos = Barbero.objects.filter(sede=sede_de_la_admin)
        except Sede.DoesNotExist:
            barberos = Barbero.objects.none()
            
    return render(request, 'gestion/barberos_list.html', {'barberos': barberos})


@login_required
def crear_barbero(request):
    user_actual = request.user
    
    if request.method == 'POST':
        # Pasamos el usuario al formulario para validaciones internas
        form = BarberoForm(request.POST, request.FILES, user=user_actual)
        
        usuario_login = request.POST.get('username')
        clave_login = request.POST.get('password')

        if form.is_valid():
            # 1. Validar que el nombre de usuario de Django no exista
            if User.objects.filter(username=usuario_login).exists():
                messages.error(request, "Este nombre de usuario ya está en uso.")
                return render(request, 'gestion/barbero_form.html', {'form': form})

            # 2. Creamos el objeto barbero en memoria
            barbero = form.save(commit=False)

            # --- LÓGICA AUTOMÁTICA DE SEDE Y ESTADO ---
            if not es_dueno_o_superuser(user_actual):
                # Buscamos la sede vinculada al administrador logueado
                mi_sede = Sede.objects.filter(administrador=user_actual).first()
                if mi_sede:
                    barbero.sede = mi_sede
                else:
                    messages.error(request, "Error: No tienes una sede asignada para crear personal.")
                    return render(request, 'gestion/barbero_form.html', {'form': form})
                
                # Forzamos el estado a 'activo' cuando lo crea un admin de sede
                barbero.estado = 'activo'
            # ------------------------------------------

            # 3. Crear el usuario de Django para el login
            nuevo_usuario = User.objects.create_user(
                username=usuario_login, 
                password=clave_login
            )

            # --- NUEVA FUNCIONALIDAD: ASIGNACIÓN AL GRUPO BARBEROS ---
            # Buscamos el grupo 'barberos' (en minúsculas como lo definimos en el admin)
            grupo_barberos, _ = Group.objects.get_or_create(name='barberos')
            nuevo_usuario.groups.add(grupo_barberos)
            # --------------------------------------------------------

            # 4. Vincular el perfil de Barbero con el usuario de Django y guardar
            barbero.user = nuevo_usuario
            barbero.save()
            
            # Mensaje de éxito dinámico según la sede asignada
            nombre_sede = barbero.sede.nombre if barbero.sede else "General"
            messages.success(request, f"Barbero {barbero.nombre} creado con éxito en sede {nombre_sede}.")
            return redirect('lista_barberos')
    else:
        form = BarberoForm(user=user_actual)
    
    return render(request, 'gestion/barbero_form.html', {'form': form})

@login_required
def editar_barbero(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    if request.method == 'POST':
        form = BarberoForm(request.POST, request.FILES, instance=barbero)
        if form.is_valid():
            form.save()
            return redirect('lista_barberos')
    else:
        form = BarberoForm(instance=barbero)
    
    return render(request, 'gestion/barbero_form.html', {
        'form': form,
        'editando': True,
        'barbero': barbero
    })

@login_required
def vacaciones_barbero_logico(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    barbero.estado = 'vacaciones'
    barbero.save()
    return redirect('lista_barberos')

@login_required
def eliminar_barbero_definitivo(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    # Aquí es donde a futuro pondremos: if barbero.citas_activas.exists(): ...
    barbero.estado = 'inactivo'
    barbero.save()
    return redirect('lista_barberos')

@login_required
def activar_barbero(request, pk):
    barbero = get_object_or_404(Barbero, pk=pk)
    barbero.estado = 'activo'
    barbero.save()
    return redirect('lista_barberos')

def puede_agendar(telefono, fecha_seleccionada):
    # Contamos cuántas citas confirmadas tiene ese número en esa fecha
    citas_del_dia = Cita.objects.filter(
        telefono=telefono, 
        fecha=fecha_seleccionada,
        estado='Confirmada' # Solo contamos las que ya son reales
    ).count()

    return citas_del_dia < 2

from django.contrib.auth.decorators import user_passes_test
from .forms import RegistroAdminSedeForm

@user_passes_test(es_dueno_o_superuser)
def crear_administrador_sede(request):
    if request.method == 'POST':
        form = RegistroAdminSedeForm(request.POST)
        if form.is_valid():
            # 1. Crear el usuario en la tabla auth_user
            nuevo_admin = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                is_staff=True  # Recomendado: para que pueda entrar al dashboard
            )
            
            # --- NUEVO: ASIGNACIÓN AUTOMÁTICA AL GRUPO ---
            # Buscamos el grupo (o lo creamos si no existe por error)
            grupo_admins, _ = Group.objects.get_or_create(name='administradores')
            nuevo_admin.groups.add(grupo_admins)
            # ---------------------------------------------

            # 2. Vincularlo con la sede seleccionada
            sede = form.cleaned_data['sede']
            sede.administrador = nuevo_admin
            sede.save()

            messages.success(request, f"¡Éxito! {nuevo_admin.first_name} ahora administra la sede {sede.nombre}")
            return redirect('lista_administradores') # Te sugiero volver a la lista para ver el cambio
    else:
        form = RegistroAdminSedeForm()
    
    return render(request, 'gestion/crear_admin.html', {'form': form})

@user_passes_test(es_dueno_o_superuser)
def lista_administradores(request):
    # Traemos todas las sedes y sus administradores (usando select_related para que sea rápido)
    sedes = Sede.objects.select_related('administrador').all()
    
    return render(request, 'gestion/lista_administradores.html', {'sedes': sedes})

@user_passes_test(es_dueno_o_superuser)
def editar_admin(request, sede_id):
    sede = get_object_or_404(Sede, id=sede_id)
    
    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre_real')
        # Actualizamos el first_name del usuario de Django vinculado
        if sede.administrador:
            admin_user = sede.administrador
            admin_user.first_name = nuevo_nombre
            admin_user.save()
            
            messages.success(request, f"Datos de {admin_user.username} actualizados correctamente.")
        
        return redirect('lista_administradores') # Reemplaza con el nombre de tu url de lista

    return render(request, 'gestion/editar_admin_modal.html', {'sede': sede})

# Vista para quitar el rol de administrador de la sede
@user_passes_test(es_dueno_o_superuser)
def quitar_admin(request, sede_id):
    sede = get_object_or_404(Sede, id=sede_id)
    nombre_admin = sede.administrador.username if sede.administrador else "el encargado"
    
    # Simplemente ponemos el campo administrador en None
    sede.administrador = None
    sede.save()
    
    messages.warning(request, f"{nombre_admin} ya no es el administrador de la sede {sede.nombre}.")
    return redirect('lista_administradores') # Reemplaza con el nombre de tu url de lista

# C:\Users\CSJ\Desktop\Barberia\gestion\views.py

# C:\Users\CSJ\Desktop\Barberia\gestion\views.py
@login_required
def asignar_admin_sede(request):
    # 1. Buscamos el grupo como lo creaste en la imagen (minúsculas)
    # Si por alguna razón no existe, lo crea automáticamente.
    grupo_admins, created = Group.objects.get_or_create(name='administradores')

    # 2. Sedes que no tienen administrador asignado
    sedes_libres = Sede.objects.filter(administrador__isnull=True)
    
    # 3. Filtramos:
    # - Que pertenezcan al grupo 'administradores'
    # - Que no tengan sede asignada
    # - Que no seas tú (el superusuario)
    admins_disponibles = User.objects.filter(
        groups=grupo_admins,
        sede_administrada__isnull=True, 
        is_superuser=False
    )

    if request.method == 'POST':
        sede_id = request.POST.get('sede_id')
        admin_id = request.POST.get('admin_id')
        
        if sede_id and admin_id:
            sede = get_object_or_404(Sede, id=sede_id)
            admin = get_object_or_404(User, id=admin_id)
            
            sede.administrador = admin
            sede.save()
            
            messages.success(request, f"¡Éxito! {admin.username} ha sido vinculado a la sede {sede.nombre}.")
            return redirect('lista_administradores')

    return render(request, 'gestion/asignar_admin.html', {
        'sedes_libres': sedes_libres,
        'admins_disponibles': admins_disponibles
    })

@user_passes_test(es_dueno_o_superuser)
def eliminar_administrador_total(request, sede_id):
    sede = get_object_or_404(Sede, id=sede_id)
    
    if sede.administrador:
        user_a_eliminar = sede.administrador
        username = user_a_eliminar.username
        
        # 1. Liberamos la sede primero
        sede.administrador = None
        sede.save()
        
        # 2. Eliminación Lógica: Deshabilitamos el acceso al sistema
        user_a_eliminar.is_active = False
        user_a_eliminar.save()
        messages.error(request, f"El administrador {username} ha sido deshabilitado y la sede {sede.nombre} quedó libre.")
    else:
        messages.warning(request, "Esta sede no tiene un administrador asignado.")
        
    return redirect('lista_administradores')

@login_required
def citas_globales_view(request):
    user = request.user
    
    # Check permissions: only superuser or admin of a sede
    if not (es_dueno_o_superuser(user) or Sede.objects.filter(administrador=user).exists()):
        return HttpResponseForbidden("No tienes permiso para ver esta sección.")
        
    # Get all barberos and sedes for filtering
    if es_dueno_o_superuser(user):
        barberos = Barbero.objects.all()
        citas = Cita.objects.select_related('barbero', 'servicio', 'barbero__sede').all()
        sedes = Sede.objects.all()
    else:
        mi_sede = Sede.objects.filter(administrador=user).first()
        barberos = Barbero.objects.filter(sede=mi_sede)
        citas = Cita.objects.select_related('barbero', 'servicio').filter(barbero__sede=mi_sede)
        sedes = Sede.objects.filter(id=mi_sede.id)

    # Apply filters
    fecha_filtro = request.GET.get('fecha')
    barbero_filtro = request.GET.get('barbero')
    estado_filtro = request.GET.get('estado')
    sede_filtro = request.GET.get('sede')

    # Por defecto mostrar solo historial
    if not estado_filtro:
        citas = citas.filter(estado__in=['Completada', 'Cancelada', 'No_Asistio'])

    if fecha_filtro:
        citas = citas.filter(fecha=fecha_filtro)
    if barbero_filtro:
        citas = citas.filter(barbero_id=barbero_filtro)
    if estado_filtro:
        citas = citas.filter(estado=estado_filtro)
    if sede_filtro and es_dueno_o_superuser(user):
        citas = citas.filter(barbero__sede_id=sede_filtro)

    citas = citas.order_by('-fecha', '-hora')

    context = {
        'citas': citas,
        'barberos': barberos,
        'sedes': sedes,
        'fecha_filtro': fecha_filtro,
        'barbero_filtro': barbero_filtro,
        'estado_filtro': estado_filtro,
        'sede_filtro': sede_filtro,
    }
    return render(request, 'gestion/citas_globales.html', context)

@login_required
def cambiar_estado_cita(request, cita_id, nuevo_estado):
    cita = get_object_or_404(Cita, id=cita_id)
    user = request.user
    is_barbero = hasattr(user, 'barbero')
    
    # Check permission
    if is_barbero:
        if cita.barbero != user.barbero:
            return HttpResponseForbidden("No puedes modificar citas de otros barberos.")
        
        # Validación: El barbero solo puede finalizar si el cliente ya llegó
        if nuevo_estado == 'Completada' and cita.estado != 'En_Atencion':
            messages.error(request, "No puedes finalizar el servicio. El administrador aún no ha confirmado que el cliente llegó a su cita.")
            return redirect(request.GET.get('next', 'dashboard_barbero'))
            
    else:
        if not es_dueno_o_superuser(user):
            mi_sede = Sede.objects.filter(administrador=user).first()
            if not mi_sede or cita.barbero.sede != mi_sede:
                return HttpResponseForbidden("No puedes modificar citas de otra sede.")
                
    if nuevo_estado in ['Confirmada', 'En_Atencion', 'No_Asistio', 'Completada', 'Cancelada', 'Pendiente']:
        cita.estado = nuevo_estado
        if nuevo_estado == 'Confirmada':
            cita.verificado = True
        elif nuevo_estado == 'En_Atencion':
            cita.verificado = True
            cita.hora_llegada = timezone.now()
            
        cita.save()
        messages.success(request, f"Cita actualizada a {cita.get_estado_display()} con éxito.")
        
    next_url = request.GET.get('next', 'dashboard')
    if next_url == 'citas_globales':
        return redirect('citas_globales')
    elif next_url == 'dashboard_barbero':
        return redirect('dashboard_barbero')
    elif next_url == 'mis_citas_barbero':
        return redirect('mis_citas_barbero')
    return redirect('dashboard')

@login_required
def horarios_view(request):
    user = request.user
    
    # 1. Determine Sede
    if es_dueno_o_superuser(user):
        sedes = Sede.objects.all()
        sede_id = request.GET.get('sede_id') or request.POST.get('sede_id')
        if sede_id:
            sede = get_object_or_404(Sede, id=sede_id)
        else:
            sede = sedes.first()
    else:
        sede = Sede.objects.filter(administrador=user).first()
        sedes = Sede.objects.filter(id=sede.id) if sede else Sede.objects.none()

    if not sede:
        messages.error(request, "No tienes una sede asociada o no hay sedes en el sistema.")
        return redirect('dashboard')

    # 2. Initialize Sede Schedules if they do not exist
    for i in range(7):
        HorarioSede.objects.get_or_create(
            sede=sede,
            dia_semana=i,
            defaults={'hora_apertura': '08:00', 'hora_cierre': '20:00', 'cerrado': False}
        )

    # 3. Handle Sede Schedule POST
    if request.method == 'POST' and 'guardar_sede' in request.POST:
        for i in range(7):
            apertura = request.POST.get(f'apertura_{i}', '08:00')
            cierre = request.POST.get(f'cierre_{i}', '20:00')
            cerrado = request.POST.get(f'cerrado_{i}') == 'on'
            
            horario = HorarioSede.objects.get(sede=sede, dia_semana=i)
            horario.hora_apertura = apertura
            horario.hora_cierre = cierre
            horario.cerrado = cerrado
            horario.save()
            
        messages.success(request, "Horario de la sede guardado correctamente.")
        return redirect(f"{request.path}?sede_id={sede.id}")

    # 4. Barberos in this Sede
    barberos = Barbero.objects.filter(sede=sede, estado='activo')
    barbero = None
    barbero_id = request.GET.get('barbero_id') or request.POST.get('barbero_id')
    
    if barbero_id:
        barbero = get_object_or_404(Barbero, id=barbero_id, sede=sede)
        # Initialize Barbero Schedule
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

    # 5. Handle Barbero Schedule POST
    if request.method == 'POST' and 'guardar_barbero' in request.POST and barbero:
        for i in range(7):
            entrada = request.POST.get(f'entrada_{i}', '08:00')
            salida = request.POST.get(f'salida_{i}', '20:00')
            almuerzo_inicio = request.POST.get(f'almuerzo_inicio_{i}') or None
            almuerzo_fin = request.POST.get(f'almuerzo_fin_{i}') or None
            descanso = request.POST.get(f'descanso_{i}') == 'on'
            
            horario = HorarioBarbero.objects.get(barbero=barbero, dia_semana=i)
            horario.hora_entrada = entrada
            horario.hora_salida = salida
            horario.inicio_almuerzo = almuerzo_inicio
            horario.fin_almuerzo = almuerzo_fin
            horario.dia_descanso = descanso
            horario.save()
            
        messages.success(request, f"Horario del barbero {barbero.nombre} guardado correctamente.")
        return redirect(f"{request.path}?sede_id={sede.id}&barbero_id={barbero.id}")

    horarios_sede = HorarioSede.objects.filter(sede=sede).order_by('dia_semana')
    horarios_barbero = HorarioBarbero.objects.filter(barbero=barbero).order_by('dia_semana') if barbero else None

    # Helper mapping to send days of week
    dias_semana_nombres = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles',
        3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }

    context = {
        'sedes': sedes,
        'sede_actual': sede,
        'barberos': barberos,
        'barbero_actual': barbero,
        'horarios_sede': horarios_sede,
        'horarios_barbero': horarios_barbero,
        'dias_nombres': dias_semana_nombres,
    }
    return render(request, 'gestion/horarios.html', context)

@user_passes_test(es_dueno_o_superuser)
def lista_servicios(request):
    servicios = Servicio.objects.all().select_related('sede')
    return render(request, 'gestion/servicios.html', {'servicios': servicios})

@user_passes_test(es_dueno_o_superuser)
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save()
            messages.success(request, f"Servicio {servicio.nombre} creado con éxito.")
            return redirect('servicios_list')
    else:
        form = ServicioForm()
    return render(request, 'gestion/servicio_form.html', {'form': form})

@user_passes_test(es_dueno_o_superuser)
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Servicio {servicio.nombre} actualizado con éxito.")
            return redirect('servicios_list')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'gestion/servicio_form.html', {'form': form, 'editando': True})

@user_passes_test(es_dueno_o_superuser)
def eliminar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    nombre = servicio.nombre
    servicio.delete()
    messages.warning(request, f"Servicio {nombre} eliminado correctamente.")
    return redirect('servicios_list')
from .forms import CrearSedeForm

@user_passes_test(es_dueno_o_superuser)
def crear_sede(request):
    if request.method == 'POST':
        form = CrearSedeForm(request.POST)
        if form.is_valid():
            # Obtener el administrador seleccionado (puede ser None)
            admin_seleccionado = form.cleaned_data.get('administrador')

            # Crear la sede y asignarle el administrador
            nueva_sede = Sede.objects.create(
                nombre=form.cleaned_data['sede_nombre'],
                direccion=form.cleaned_data['sede_direccion'],
                administrador=admin_seleccionado
            )
            
            # Generar horarios por defecto para la nueva sede
            for i in range(7):
                HorarioSede.objects.create(
                    sede=nueva_sede,
                    dia_semana=i,
                    hora_apertura='08:00',
                    hora_cierre='20:00',
                    cerrado=True if i >= 5 else False
                )

            admin_msg = f" y se asignó a '{admin_seleccionado.first_name or admin_seleccionado.username}'" if admin_seleccionado else " (sin administrador asignado aún)"
            messages.success(request, f"Sede '{nueva_sede.nombre}' creada exitosamente{admin_msg}.")
            return redirect('lista_administradores')
    else:
        form = CrearSedeForm()

    return render(request, 'gestion/crear_sede.html', {'form': form})
