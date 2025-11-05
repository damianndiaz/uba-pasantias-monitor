#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UBA Pasantías Monitor - Configuration Setup Wizard
Interactive configuration setup for easy first-time configuration
"""

import json
import os
import getpass
from email_sender import EmailSender

def main():
    print("🎓 UBA PASANTÍAS MONITOR - ASISTENTE DE CONFIGURACIÓN")
    print("=" * 60)
    print()
    
    # Check if config already exists
    if os.path.exists("config.json"):
        print("⚠️  Ya existe un archivo config.json")
        response = input("¿Quieres sobrescribirlo? (s/N): ").lower().strip()
        if response not in ['s', 'si', 'sí', 'yes', 'y']:
            print("Configuración cancelada.")
            return
    
    print("Vamos a configurar tu monitor paso a paso...\n")
    
    # Email settings
    print("📧 CONFIGURACIÓN DE EMAIL")
    print("-" * 30)
    
    sender_email = input("Tu email (desde donde se enviarán las notificaciones): ").strip()
    
    print("\n💡 IMPORTANTE: Para Gmail necesitas una 'Contraseña de aplicación'")
    print("   1. Ve a tu cuenta Google → Seguridad")
    print("   2. Activa verificación en 2 pasos")
    print("   3. Genera una contraseña de aplicación")
    print("   4. Usa esa contraseña aquí (no tu contraseña normal)\n")
    
    sender_password = getpass.getpass("Contraseña de aplicación (no se mostrará al escribir): ").strip()
    
    recipient_email = input("Email donde quieres recibir las notificaciones: ").strip()
    
    # SMTP settings
    print("\n🌐 CONFIGURACIÓN SMTP")
    print("-" * 30)
    print("1. Gmail (smtp.gmail.com:587)")
    print("2. Outlook/Hotmail (smtp-mail.outlook.com:587)")
    print("3. Otro servidor")
    
    smtp_choice = input("Elige tu proveedor (1-3) [1]: ").strip() or "1"
    
    if smtp_choice == "1":
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
    elif smtp_choice == "2":
        smtp_server = "smtp-mail.outlook.com" 
        smtp_port = 587
    else:
        smtp_server = input("Servidor SMTP: ").strip()
        smtp_port = int(input("Puerto SMTP [587]: ").strip() or "587")
    
    # Monitoring settings
    print("\n⏰ CONFIGURACIÓN DE MONITOREO")
    print("-" * 30)
    
    print("¿Con qué frecuencia quieres revisar? (horas)")
    print("- 24: Una vez al día (recomendado)")
    print("- 12: Dos veces al día")
    print("- 6: Cada 6 horas")
    
    frequency = int(input("Frecuencia en horas [24]: ").strip() or "24")
    
    # Create configuration
    config = {
        "email_settings": {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "sender_email": sender_email,
            "sender_password": sender_password,
            "sender_name": "UBA Pasantías Monitor"
        },
        "notification_settings": {
            "recipient_email": recipient_email,
            "subject_template": "🎯 Nueva Pasantía UBA Disponible - Oferta #{numero}",
            "send_summary": True,
            "send_individual": True
        },
        "monitoring_settings": {
            "check_frequency_hours": frequency,
            "retry_attempts": 3,
            "timeout_seconds": 30
        }
    }
    
    # Save configuration
    try:
        with open("config.json", "w", encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Configuración guardada exitosamente!")
        
        # Test configuration
        print("\n🧪 PROBANDO CONFIGURACIÓN...")
        email_sender = EmailSender()
        
        if email_sender.validate_config():
            print("✅ Configuración válida")
            
            # Ask if user wants to send test email
            test_email = input("\n¿Quieres enviar un email de prueba? (S/n): ").lower().strip()
            if test_email not in ['n', 'no']:
                print("Enviando email de prueba...")
                if email_sender.send_test_email():
                    print("✅ Email de prueba enviado correctamente")
                else:
                    print("❌ Error enviando email de prueba")
        else:
            print("❌ Error en la configuración")
    
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("\nPróximos pasos:")
    print("1. Ejecuta 'python scheduler.py --status' para ver el estado")
    print("2. Ejecuta 'python scheduler.py --check' para una revisión manual")
    print("3. Ejecuta 'python scheduler.py' para iniciar el monitor automático")
    print("\n¡Ya estás listo para recibir notificaciones de nuevas pasantías!")

if __name__ == "__main__":
    main()