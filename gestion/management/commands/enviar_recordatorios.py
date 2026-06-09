import os
from datetime import timedelta, time, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from gestion.models import Cita
from landing.utils import enviar_whatsapp_recordatorio

class Command(BaseCommand):
    help = 'Envía recordatorios de WhatsApp a los clientes.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando revisión de recordatorios...")
        now = timezone.localtime()

        # Solo ejecutamos entre las 10 AM y las 7 PM (19:00)
        if not (10 <= now.hour <= 19):
            self.stdout.write(f"Hora actual ({now.hour}:00) fuera del horario de ejecución (10:00 - 19:00).")
            return

        citas = Cita.objects.filter(estado='Confirmada', recordatorio_enviado=False)
        enviados = 0

        for cita in citas:
            # Reconstruimos la fecha y hora de la cita en un objeto datetime local
            cita_dt = timezone.make_aware(datetime.combine(cita.fecha, cita.hora))
            
            # Caso 1: Revisión de las 7 PM para turnos del día siguiente antes de las 10 AM
            if now.hour == 19:
                if cita.fecha == now.date() + timedelta(days=1) and cita.hora < time(10, 0):
                    self.stdout.write(f"Enviando recordatorio (noche anterior) para {cita.telefono} - {cita_dt}")
                    enviar_whatsapp_recordatorio(cita)
                    cita.recordatorio_enviado = True
                    cita.save()
                    enviados += 1
            
            # Caso 2: Recordatorios normales de 3 horas antes (se chequea hasta 4 horas para no perder citas entre horas)
            # La cita debe ocurrir en el futuro pero en menos de 4 horas
            delta = cita_dt - now
            if timedelta(hours=0) < delta <= timedelta(hours=4):
                # Evitamos enviar ahora si la cita era de la mañana (ya debió enviarse anoche).
                if cita.hora >= time(10, 0) or cita.fecha > now.date():
                    self.stdout.write(f"Enviando recordatorio (3 hrs antes) para {cita.telefono} - {cita_dt}")
                    enviar_whatsapp_recordatorio(cita)
                    cita.recordatorio_enviado = True
                    cita.save()
                    enviados += 1

        self.stdout.write(self.style.SUCCESS(f"Revisión completada. Se enviaron {enviados} recordatorios."))
