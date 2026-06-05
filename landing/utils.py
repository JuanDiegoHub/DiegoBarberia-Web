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