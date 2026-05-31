from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def barbero_required(view_func):
    """
    Decorador que asegura que el usuario tiene un perfil de Barbero.
    """
    def check_user(user):
        # 1. Verificamos si el usuario está activo
        if not user.is_authenticated:
            return False
        
        # 2. Verificamos si tiene el atributo 'barbero' (relación OneToOne)
        if hasattr(user, 'barbero'):
            return True
            
        # 3. Si no es barbero, lanzamos el error de permiso denegado 🚫
        raise PermissionDenied("No tienes permiso para acceder al panel de barberos.")

    return user_passes_test(check_user)(view_func)