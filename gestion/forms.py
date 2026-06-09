from django import forms
from .models import Barbero

class BarberoForm(forms.ModelForm):
    # 1. Campos extra para el sistema de login
    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juan_barber'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Asigna una clave'})
    )

    class Meta:
        model = Barbero
        fields = ['nombre', 'apellido', 'username', 'password', 'especialidad', 'sede', 'imagen', 'estado']
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sede': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        
        # --- NUEVA FUNCIÓN: AUTOMATIZACIÓN DE ESTADO ---
        # 1. Marcamos 'activo' como valor inicial por defecto
        self.fields['estado'].initial = 'activo'
        
        # 2. Si no es superusuario (Milton o Sharol), quitamos obligatoriedad
        # de Sede y Estado porque se asignarán automáticamente en la vista.
        if user and not user.is_superuser:
            self.fields['sede'].required = False
            self.fields['estado'].required = False
# gestion/forms.py
# En gestion/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Sede

class RegistroAdminSedeForm(forms.Form):
    # Definimos el widget con la clase CSS para cada campo
    username = forms.CharField(
        label="Usuario para el Admin",
        widget=forms.TextInput(attrs={'class': 'form-control-minimal'})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control-minimal'})
    )
    first_name = forms.CharField(
        label="Nombre del Encargado",
        widget=forms.TextInput(attrs={'class': 'form-control-minimal'})
    )
    # Para el select de sede, también añadimos la clase
    sede = forms.ModelChoiceField(
        queryset=Sede.objects.filter(administrador__isnull=True),
        label="Seleccionar Sede para asignar",
        empty_label="-- Selecciona una sede disponible --",
        widget=forms.Select(attrs={'class': 'form-control-minimal'}) # O 'form-select' si prefieres el estilo por defecto de bootstrap
    )

from .models import HorarioSede, HorarioBarbero

class HorarioSedeForm(forms.ModelForm):
    class Meta:
        model = HorarioSede
        fields = ['hora_apertura', 'hora_cierre', 'cerrado']
        widgets = {
            'hora_apertura': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'hora_cierre': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'cerrado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class HorarioBarberoForm(forms.ModelForm):
    class Meta:
        model = HorarioBarbero
        fields = ['hora_entrada', 'hora_salida', 'inicio_almuerzo', 'fin_almuerzo', 'dia_descanso']
        widgets = {
            'hora_entrada': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'hora_salida': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'inicio_almuerzo': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'fin_almuerzo': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control-minimal'}),
            'dia_descanso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'descripcion', 'precio', 'duracion_minutos', 'sede', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control-minimal', 'placeholder': 'Ej: Corte Clásico'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control-minimal', 'rows': 3, 'placeholder': 'Descripción del servicio...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control-minimal', 'placeholder': '0.00'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control-minimal', 'placeholder': '30'}),
            'sede': forms.Select(attrs={'class': 'form-control-minimal'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CrearSedeForm(forms.Form):
    # Datos de la sede
    sede_nombre = forms.CharField(
        label='Nombre de la Sede',
        widget=forms.TextInput(attrs={'class': 'form-control-minimal', 'placeholder': 'Ej: Sede Norte'})
    )
    sede_direccion = forms.CharField(
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control-minimal', 'placeholder': 'Ej: Av. Principal 123'})
    )
    
    administrador = forms.ModelChoiceField(
        queryset=User.objects.none(),
        label="Seleccionar Administrador",
        empty_label="-- Selecciona un administrador disponible --",
        widget=forms.Select(attrs={'class': 'form-select-minimal'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth.models import Group
        grupo_admins, _ = Group.objects.get_or_create(name='administradores')
        self.fields['administrador'].queryset = User.objects.filter(
            groups=grupo_admins,
            sede_administrada__isnull=True,
            is_superuser=False
        )

from .models import Cita

class CitaManualForm(forms.ModelForm):
    # Campos extra para el reagendamiento
    MOTIVO_CHOICES = [
        ('', 'Seleccione un motivo'),
        ('barbero_no_disponible', 'Barbero no se encuentra disponible'),
        ('dia_descanso', 'Día no disponible por descanso'),
        ('otro', 'Otro'),
    ]
    motivo_reagendamiento = forms.ChoiceField(
        choices=MOTIVO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control-minimal', 'id': 'id_motivo_reagendamiento'})
    )
    motivo_otro = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control-minimal', 'rows': 2, 'id': 'id_motivo_otro', 'placeholder': 'Especifique el motivo...'})
    )

    class Meta:
        model = Cita
        fields = ['telefono', 'cliente_nombre', 'barbero', 'servicio', 'fecha', 'hora']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control-minimal', 'placeholder': 'Ej: 3000000000'}),
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control-minimal', 'placeholder': 'Nombre del Cliente'}),
            'barbero': forms.Select(attrs={'class': 'form-control-minimal', 'id': 'select-barbero'}),
            'servicio': forms.Select(attrs={'class': 'form-control-minimal', 'id': 'select-servicio'}),
            'fecha': forms.HiddenInput(attrs={'id': 'id_fecha_hidden'}),
            'hora': forms.HiddenInput(attrs={'id': 'id_hora_hidden'}),
        }

    def __init__(self, *args, **kwargs):
        self.sede = kwargs.pop('sede', None)
        super().__init__(*args, **kwargs)
        
        self.fields['servicio'].required = True
        
        if self.sede:
            self.fields['barbero'].queryset = Barbero.objects.filter(sede=self.sede, estado='activo')
            self.fields['servicio'].queryset = Servicio.objects.filter(sede=self.sede, activo=True)
