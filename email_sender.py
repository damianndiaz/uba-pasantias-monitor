#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Notification System for UBA Pasantías Monitor
Sends email notifications when new internship offers are found
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import json
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class EmailSender:
    """Handles email notifications for new pasantías offers"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize with configuration file"""
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load email configuration from file or environment variables"""
        try:
            # Try to load from config_loader (handles both local and GitHub Actions)
            from config_loader import load_config
            config = load_config()
            logger.info("Email configuration loaded successfully")
            return config
        except ImportError:
            # Fallback to original method if config_loader not available
            return self._load_config_fallback()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._load_config_fallback()
    
    def _load_config_fallback(self) -> Dict:
        """Fallback configuration loading method"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("Email configuration loaded successfully (fallback)")
                return config
            else:
                logger.warning(f"Configuration file {self.config_file} not found, creating template")
                self.create_config_template()
                return {}
        except Exception as e:
            logger.error(f"Error loading configuration (fallback): {e}")
            return {}
    
    def create_config_template(self):
        """Create a template configuration file"""
        template_config = {
            "email_settings": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "tu_email@gmail.com",
                "sender_password": "tu_app_password_aqui",
                "sender_name": "UBA Pasantías Monitor"
            },
            "notification_settings": {
                "recipient_email": "tu_email_destino@gmail.com",
                "subject_template": "🎯 Nueva Pasantía UBA Disponible - Oferta #{numero}",
                "send_summary": True,
                "send_individual": True
            },
            "monitoring_settings": {
                "check_frequency_hours": 24,
                "retry_attempts": 3,
                "timeout_seconds": 30
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, ensure_ascii=False, indent=2)
            logger.info(f"Template configuration created at {self.config_file}")
            print(f"\n⚠️  IMPORTANTE: Completa la configuración en {self.config_file}")
            print("   - Agrega tu email y contraseña de aplicación")
            print("   - Configura el email de destino")
            print("   - Para Gmail, necesitas generar una 'Contraseña de aplicación'")
        except Exception as e:
            logger.error(f"Error creating template config: {e}")
    
    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        if not self.config:
            logger.error("No configuration available")
            return False
        
        required_keys = [
            ('email_settings', 'sender_email'),
            ('email_settings', 'sender_password'),
            ('notification_settings', 'recipient_email')
        ]
        
        for section, key in required_keys:
            if section not in self.config or key not in self.config[section]:
                logger.error(f"Missing required configuration: {section}.{key}")
                return False
            
            value = self.config[section][key]
            if not value or 'tu_email' in str(value) or 'password_aqui' in str(value):
                logger.error(f"Configuration not properly set: {section}.{key}")
                return False
        
        return True
    
    def create_email_content(self, offers: List[Dict]) -> tuple[str, str]:
        """Create HTML and text content for email notification"""
        
        if not offers:
            return "", ""
        
        # HTML Content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; }
                .header { background: #003366; color: white; padding: 20px; border-radius: 5px; text-align: center; }
                .offer { background: #f9f9f9; border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }
                .offer-title { color: #003366; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .offer-detail { margin: 8px 0; }
                .label { font-weight: bold; color: #666; }
                .value { color: #333; }
                .email-link { background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 3px; display: inline-block; margin-top: 10px; }
                .footer { margin-top: 30px; padding: 20px; background: #f1f1f1; border-radius: 5px; font-size: 12px; color: #666; text-align: center; }
                .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Nueva Pasantía UBA Detectada</h1>
                    <p>Facultad de Derecho - Universidad de Buenos Aires</p>
                </div>
        """
        
        # Add offers
        for offer in offers:
            html_content += f"""
                <div class="offer">
                    <div class="offer-title">📋 Búsqueda N° {offer.get('numero_busqueda', 'N/A')}</div>
                    <div class="offer-detail">
                        <span class="label">📅 Fecha de Publicación:</span>
                        <span class="value">{offer.get('fecha_publicacion', 'No especificada')}</span>
                    </div>
                    <div class="offer-detail">
                        <span class="label">🏢 Área:</span>
                        <span class="value">{offer.get('area', 'No especificada')}</span>
                    </div>
                    <div class="offer-detail">
                        <span class="label">🕐 Horario:</span>
                        <span class="value">{offer.get('horario', 'No especificado')}</span>
                    </div>
                    <div class="offer-detail">
                        <span class="label">💰 Asignación Estímulo:</span>
                        <span class="value">${offer.get('asignacion_estimulo', 'No especificada')}</span>
                    </div>
            """
            
            # Add contact email if available
            if offer.get('contacto_email'):
                html_content += f"""
                    <div class="offer-detail">
                        <span class="label">📧 Email de Contacto:</span>
                        <a href="mailto:{offer['contacto_email']}" class="email-link">{offer['contacto_email']}</a>
                    </div>
                """
            else:
                html_content += """
                    <div class="warning">
                        ⏰ <strong>Nota:</strong> El email de contacto se publica automáticamente 24 horas después de la oferta.
                        Revisa la página web para obtener la información de contacto actualizada.
                    </div>
                """
            
            # Add more info link if available
            if offer.get('mas_informacion_url'):
                html_content += f"""
                    <div class="offer-detail">
                        <a href="{offer['mas_informacion_url']}" class="email-link">🔗 Ver Más Información</a>
                    </div>
                """
            
            html_content += "</div>"
        
        html_content += f"""
                <div class="footer">
                    <p><strong>🔗 Enlace Original:</strong> <a href="https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php">Página de Pasantías UBA</a></p>
                    <p>📊 Este email fue generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                    <p>⚠️ <strong>Importante:</strong> La oficina de Pasantías no recepciona los CV ni forma parte del proceso de selección. Envía tu CV directamente al email de contacto de cada oferta.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text Content (fallback)
        text_content = f"""
🎓 NUEVA PASANTÍA UBA DETECTADA
Facultad de Derecho - Universidad de Buenos Aires

{"="*50}
        """
        
        for i, offer in enumerate(offers, 1):
            text_content += f"""
OFERTA {i}: Búsqueda N° {offer.get('numero_busqueda', 'N/A')}
{"="*30}
📅 Fecha: {offer.get('fecha_publicacion', 'No especificada')}
🏢 Área: {offer.get('area', 'No especificada')}
🕐 Horario: {offer.get('horario', 'No especificado')}
💰 Asignación: ${offer.get('asignacion_estimulo', 'No especificada')}
"""
            if offer.get('contacto_email'):
                text_content += f"📧 Email: {offer['contacto_email']}\n"
            else:
                text_content += "⏰ Email de contacto: Se publica 24hs después de la oferta\n"
            
            if offer.get('mas_informacion_url'):
                text_content += f"🔗 Más info: {offer['mas_informacion_url']}\n"
            
            text_content += "\n"
        
        text_content += f"""
{"="*50}
🔗 Página original: https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php
📊 Email generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}

⚠️  IMPORTANTE: La oficina de Pasantías no recepciona los CV ni forma parte 
del proceso de selección. Envía tu CV directamente al email de contacto de cada oferta.
        """
        
        return html_content, text_content
    
    def send_notification(self, offers: List[Dict]) -> bool:
        """Send email notification for new offers"""
        
        if not offers:
            logger.info("No offers to send")
            return True
        
        if not self.validate_config():
            logger.error("Invalid configuration, cannot send email")
            return False
        
        try:
            # Get email settings
            email_settings = self.config['email_settings']
            notification_settings = self.config['notification_settings']
            
            # Create email content
            html_content, text_content = self.create_email_content(offers)
            
            # Setup email message
            msg = MIMEMultipart('alternative')
            
            # Subject
            if len(offers) == 1:
                subject = notification_settings['subject_template'].format(
                    numero=offers[0]['numero_busqueda']
                )
            else:
                subject = f"🎯 {len(offers)} Nuevas Pasantías UBA Disponibles"
            
            msg['Subject'] = subject
            msg['From'] = formataddr((email_settings['sender_name'], email_settings['sender_email']))
            msg['To'] = notification_settings['recipient_email']
            
            # Attach text and HTML content
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            logger.info(f"Sending email notification for {len(offers)} offers")
            
            context = ssl.create_default_context()
            with smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port']) as server:
                server.starttls(context=context)
                server.login(email_settings['sender_email'], email_settings['sender_password'])
                
                text = msg.as_string()
                server.sendmail(
                    email_settings['sender_email'], 
                    notification_settings['recipient_email'], 
                    text
                )
            
            logger.info("Email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration"""
        
        if not self.validate_config():
            return False
        
        test_offer = [{
            'numero_busqueda': 'TEST',
            'fecha_publicacion': datetime.now().strftime('%d-%m-%Y'),
            'area': 'Área de Prueba',
            'horario': 'Horario de prueba',
            'asignacion_estimulo': '0',
            'contacto_email': 'test@test.com',
            'mas_informacion_url': 'https://example.com'
        }]
        
        logger.info("Sending test email")
        return self.send_notification(test_offer)

def main():
    """Test the email system"""
    print("=== PRUEBA DEL SISTEMA DE EMAIL ===")
    
    email_sender = EmailSender()
    
    # Check if config exists and is valid
    if not email_sender.validate_config():
        print("❌ Configuración no válida. Completa el archivo config.json")
        return
    
    # Send test email
    print("Enviando email de prueba...")
    if email_sender.send_test_email():
        print("✅ Email de prueba enviado correctamente")
    else:
        print("❌ Error enviando email de prueba")

if __name__ == "__main__":
    main()