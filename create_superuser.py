import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Crear superusuario desde variables de entorno
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

if password and not User.objects.filter(username=username).exists():
    superuser = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superusuario '{username}' creado exitosamente.")
else:
    if not password:
        print("No se encontró DJANGO_SUPERUSER_PASSWORD en las variables de entorno. Superusuario no creado.")
    else:
        print(f"El superusuario '{username}' ya existe.")

# Asegurar que los grupos necesarios existan
for nombre_grupo in ['administradores', 'barberos', 'Dueño']:
    grupo, creado = Group.objects.get_or_create(name=nombre_grupo)
    if creado:
        print(f"Grupo '{nombre_grupo}' creado.")
    else:
        print(f"Grupo '{nombre_grupo}' ya existe.")
