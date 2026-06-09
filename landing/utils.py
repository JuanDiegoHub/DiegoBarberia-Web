import requests
import os

def enviar_whatsapp_otp(telefono, codigo):
    # Reemplaza con tus datos reales de UltraMsg
    instance_id = os.environ.get('ULTRAMSG_INSTANCE_ID', 'instance168078') 
    token = os.environ.get('ULTRAMSG_TOKEN', 'c0ei1ripkatzmzbc')
    
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    numero_limpio = ''.join(filter(str.isdigit, telefono))
    if not numero_limpio.startswith('57'):
        numero_limpio = f"57{numero_limpio}"


    cuerpo_mensaje = (
        "💈 *BARBERAPP IBAGUÉ* 💈\n\n"
        f"Tu código de seguridad es: *{codigo}*\n\n"
        "Ingresa este código en la web para confirmar tu cita. ¡Te esperamos!"
    )

    payload = {
        "token": token,
        "to": numero_limpio,
        "body": cuerpo_mensaje
    }
    
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        # ESTO ES VITAL: Nos dirá qué responde UltraMsg
        print(f"--- DIAGNÓSTICO ULTRAMSG ---")
        print(f"Estado HTTP: {response.status_code}")
        print(f"Respuesta Body: {response.text}")
        print(f"codigo enviado: {codigo} al número: {numero_limpio}")
        return response.json()
    except Exception as e:
        print(f"--- ERROR DE CONEXIÓN ---")
        print(f"Detalle: {str(e)}")
        return {'error': f'Excepción interna: {str(e)}'}

def enviar_whatsapp_reagendamiento(telefono, nombre_cliente, fecha, hora, motivo, sede_nombre):
    instance_id = os.environ.get('ULTRAMSG_INSTANCE_ID', 'instance168078') 
    token = os.environ.get('ULTRAMSG_TOKEN', 'c0ei1ripkatzmzbc')
    
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    numero_limpio = ''.join(filter(str.isdigit, telefono))
    if not numero_limpio.startswith('57'):
        numero_limpio = f"57{numero_limpio}"

    cuerpo_mensaje = (
        "💈 *BARBERAPP IBAGUÉ - AVISO DE REAGENDAMIENTO* 💈\n\n"
        f"Hola *{nombre_cliente}*,\n\n"
        f"Te informamos que tu cita ha sido reagendada desde nuestra administración.\n\n"
        f"📅 *Nueva Fecha:* {fecha}\n"
        f"⏰ *Nueva Hora:* {hora}\n"
        f"📍 *Sede:* {sede_nombre}\n"
        f"⚠️ *Motivo:* {motivo}\n\n"
        "Te pedimos disculpas por los inconvenientes. ¡Te esperamos en tu nuevo horario!\n\n"
        "⚠️ *Si este nuevo horario no te funciona*, por favor escribe a este WhatsApp para asignarte una hora adecuada."
    )

    payload = {
        "token": token,
        "to": numero_limpio,
        "body": cuerpo_mensaje
    }
    
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def enviar_whatsapp_nueva_cita_admin(telefono, nombre_cliente, fecha, hora, barbero_nombre, sede_nombre):
    instance_id = os.environ.get('ULTRAMSG_INSTANCE_ID', 'instance168078') 
    token = os.environ.get('ULTRAMSG_TOKEN', 'c0ei1ripkatzmzbc')
    
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    numero_limpio = ''.join(filter(str.isdigit, telefono))
    if not numero_limpio.startswith('57'):
        numero_limpio = f"57{numero_limpio}"

    cuerpo_mensaje = (
        "💈 *BARBERAPP IBAGUÉ - NUEVA CITA CONFIRMADA* 💈\n\n"
        f"Hola *{nombre_cliente}*,\n\n"
        f"Te informamos que desde la administración te hemos agendado una nueva cita. ¡Te esperamos!\n\n"
        f"📅 *Día:* {fecha}\n"
        f"⏰ *Hora:* {hora}\n"
        f"✂️ *Barbero:* {barbero_nombre}\n"
        f"📍 *Sede:* {sede_nombre}\n\n"
        "¡Gracias por preferirnos!"
    )

    payload = {
        "token": token,
        "to": numero_limpio,
        "body": cuerpo_mensaje
    }
    
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def enviar_whatsapp_confirmacion_cliente(cita):
    instance_id = os.environ.get('ULTRAMSG_INSTANCE_ID', 'instance168078') 
    token = os.environ.get('ULTRAMSG_TOKEN', 'c0ei1ripkatzmzbc')
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    numero_limpio = ''.join(filter(str.isdigit, cita.telefono))
    if not numero_limpio.startswith('57'):
        numero_limpio = f"57{numero_limpio}"

    servicio_nombre = cita.servicio.nombre if cita.servicio else "Servicio general"
    fecha_str = cita.fecha.strftime('%d/%m/%Y')
    hora_str = cita.hora.strftime('%I:%M %p')

    cuerpo_mensaje = (
        "💈 *BARBERAPP IBAGUÉ - CITA CONFIRMADA* 💈\n\n"
        f"Hola, tu cita ha sido agendada con éxito.\n\n"
        f"📅 *Día:* {fecha_str}\n"
        f"⏰ *Hora:* {hora_str}\n"
        f"✨ *Servicio:* {servicio_nombre}\n"
        f"✂️ *Barbero:* {cita.barbero.nombre}\n"
        f"📍 *Sede:* {cita.barbero.sede.nombre}\n\n"
        "💡 *Recomendación:* Por favor llega 10 minutos antes de tu cita.\n\n"
        "¡Te esperamos!"
    )

    payload = {
        "token": token,
        "to": numero_limpio,
        "body": cuerpo_mensaje
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    try:
        requests.post(url, data=payload, headers=headers)
    except:
        pass

def enviar_whatsapp_recordatorio(cita):
    instance_id = os.environ.get('ULTRAMSG_INSTANCE_ID', 'instance168078') 
    token = os.environ.get('ULTRAMSG_TOKEN', 'c0ei1ripkatzmzbc')
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    
    numero_limpio = ''.join(filter(str.isdigit, cita.telefono))
    if not numero_limpio.startswith('57'):
        numero_limpio = f"57{numero_limpio}"

    servicio_nombre = cita.servicio.nombre if cita.servicio else "Servicio general"
    fecha_str = cita.fecha.strftime('%d/%m/%Y')
    hora_str = cita.hora.strftime('%I:%M %p')

    cuerpo_mensaje = (
        "💈 *BARBERAPP IBAGUÉ - RECORDATORIO DE CITA* 💈\n\n"
        f"Hola, te recordamos que tienes una cita próxima con nosotros:\n\n"
        f"📅 *Día:* {fecha_str}\n"
        f"⏰ *Hora:* {hora_str}\n"
        f"✨ *Servicio:* {servicio_nombre}\n"
        f"✂️ *Barbero:* {cita.barbero.nombre}\n"
        f"📍 *Sede:* {cita.barbero.sede.nombre}\n\n"
        "💡 *Recomendación:* Por favor llega 10 minutos antes de tu cita.\n\n"
        "⚠️ *Si no puedes asistir*, por favor escribe a este WhatsApp para reagendar tu cita.\n\n"
        "¡Te esperamos!"
    )

    payload = {
        "token": token,
        "to": numero_limpio,
        "body": cuerpo_mensaje
    }
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    try:
        requests.post(url, data=payload, headers=headers)
    except:
        pass