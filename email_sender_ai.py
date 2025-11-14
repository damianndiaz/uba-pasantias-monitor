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
import urllib.parse
from ai_agent import AIJobApplicationAgent

# Setup logging
logger = logging.getLogger(__name__)

class AIEmailSender:
    """Enhanced email sender with AI-powered personalized application emails"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize with configuration file"""
        self.config_file = config_file
        self.config = self.load_config()
        self.ai_agent = AIJobApplicationAgent()
    
    def load_config(self) -> Dict:
        """Load configuration from file or environment variables"""
        # Try to load from file first
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        
        # Fallback to environment variables (for GitHub Actions)
        config = {
            "email_settings": {
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "sender_email": os.getenv("SENDER_EMAIL", ""),
                "sender_password": os.getenv("SENDER_PASSWORD", ""),
                "sender_name": os.getenv("SENDER_NAME", "UBA Pasantías Monitor")
            },
            "notification_settings": {
                "recipient_email": os.getenv("RECIPIENT_EMAIL", ""),
                "subject_template": "🎓 Nueva Pasantía UBA Detectada - {total} ofertas",
                "subject_single": "🎓 Nueva Pasantía UBA: {titulo}"
            },
            "monitoring_settings": {
                "check_frequency_hours": int(os.getenv("CHECK_FREQUENCY_HOURS", "24")),
                "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
                "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "30"))
            }
        }
        
        if config["email_settings"]["sender_email"]:
            logger.info("Configuration loaded from environment variables")
            return config
        
        # Create template config file if none exists
        self.create_template_config()
        return {}
    
    def create_template_config(self):
        """Create a template configuration file"""
        template_config = {
            "email_settings": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "tu_email@gmail.com",
                "sender_password": "tu_password_de_aplicacion_aqui",
                "sender_name": "UBA Pasantías Monitor"
            },
            "notification_settings": {
                "recipient_email": "destinatario@email.com",
                "subject_template": "🎓 Nueva Pasantía UBA Detectada - {total} ofertas",
                "subject_single": "🎓 Nueva Pasantía UBA: {titulo}"
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
    
    def create_ai_enhanced_offer_html(self, offer: Dict[str, str]) -> str:
        """Create HTML content for a single offer with AI enhancement"""
        # Generate AI-powered email content
        ai_content = self.ai_agent.generate_personalized_email(offer)
        
        # Extract email components for mailto link
        ai_subject = ai_content.get('subject', f"Consulta sobre pasantía - {offer.get('numero_busqueda', offer.get('titulo', ''))}")
        ai_body = ai_content.get('body', f"Estimados,\n\nMe dirijo a ustedes para expresar mi interés en la pasantía.")
        
        # URL encode the email content for mailto link
        encoded_subject = urllib.parse.quote(ai_subject)
        encoded_body = urllib.parse.quote(ai_body)
        
        # Create preview of AI content (first 200 chars)
        preview_body = ai_body[:200] + "..." if len(ai_body) > 200 else ai_body
        
        contact_email = offer.get('contacto_email', offer.get('contacto', ''))
        offer_title = offer.get('numero_busqueda', offer.get('numero', offer.get('titulo', 'Sin título')))
        
        return f"""
        <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
            <h3 style="color: #0056b3; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #0056b3; padding-bottom: 8px;">
                📋 {offer_title}
            </h3>
            
            <div style="margin-bottom: 15px;">
                <p><strong>📅 Fecha de publicación:</strong> {offer.get('fecha_publicacion', offer.get('fecha', 'No especificada'))}</p>
                <p><strong>🏢 Empresa:</strong> {offer.get('area', 'No especificada')}</p>
                <p><strong>🕒 Horario:</strong> {offer.get('horario', 'No especificado')}</p>
                <p><strong>💰 Asignación Estímulo:</strong> ${offer.get('asignacion_estimulo', offer.get('remuneracion', 'No especificada'))}</p>
                <p><strong>📍 Lugar:</strong> {offer.get('lugar', 'No especificado')}</p>
                {f'<p><strong>📧 Contacto:</strong> {contact_email}</p>' if contact_email else '<p><strong>⏰ Email de contacto:</strong> Se publica 24hs después de la oferta</p>'}
                {f'<p><strong>🔗 Más información:</strong> <a href="{offer.get("mas_informacion_url", offer.get("url", ""))}" style="color: #0056b3;">Ver detalles</a></p>' if offer.get('mas_informacion_url') or offer.get('url') else ''}
            </div>
            
            {self.create_ai_buttons_section(contact_email, encoded_subject, encoded_body, offer_title) if contact_email else self.create_pending_contact_section()}
            
            {self.create_ai_preview_section(ai_content) if ai_content and ai_content.get('body') else ''}
        </div>
        """
    
    def create_ai_buttons_section(self, contact_email: str, encoded_subject: str, encoded_body: str, offer_title: str = "") -> str:
        """Create the AI-enhanced buttons section"""
        simple_subject = f"Consulta sobre pasantía - {offer_title}" if offer_title else "Consulta sobre pasantía"
        encoded_simple_subject = urllib.parse.quote(simple_subject)
        
        return f"""
        <div style="text-align: center; margin-top: 20px; padding: 15px; background-color: #ffffff; border-radius: 8px; border: 1px solid #e0e0e0;">
            <h4 style="color: #333; margin-bottom: 15px; font-size: 16px;">💼 Opciones de Aplicación</h4>
            
            <a href="mailto:{contact_email}?subject={encoded_subject}&body={encoded_body}" 
               style="background-color: #28a745; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; margin: 5px 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
               🤖 Aplicar con IA (Email Personalizado)
            </a>
            
            <a href="mailto:{contact_email}?subject={encoded_simple_subject}" 
               style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: normal; display: inline-block; margin: 5px 10px; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
               📧 Email Simple
            </a>
        </div>
        """
    
    def create_pending_contact_section(self) -> str:
        """Create section for offers without contact info yet"""
        return f"""
        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 15px; margin-top: 15px; text-align: center;">
            <h4 style="color: #856404; margin-bottom: 10px;">⏰ Información de Contacto Pendiente</h4>
            <p style="color: #856404; margin: 5px 0;">El email de contacto se publicará automáticamente 24 horas después de la oferta.</p>
            <p style="color: #856404; margin: 5px 0; font-size: 14px;">Revisa la página web para obtener la información actualizada.</p>
            <a href="https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php" 
               style="color: #856404; text-decoration: underline;">
               🔗 Ver página de ofertas
            </a>
        </div>
        """
    
    def create_ai_preview_section(self, ai_content: Dict[str, str]) -> str:
        """Create a preview section showing the AI-generated email content"""
        if not ai_content or not ai_content.get('body'):
            return ""
            
        # Truncate body for preview
        preview_body = ai_content.get('body', '')[:300] + "..." if len(ai_content.get('body', '')) > 300 else ai_content.get('body', '')
        
        return f"""
        <div style="background-color: #e8f4fd; border: 1px solid #b8daff; border-radius: 8px; padding: 15px; margin-top: 15px;">
            <h4 style="color: #004085; font-size: 16px; margin-bottom: 10px;">
                🤖 Vista previa del email generado por IA:
            </h4>
            <p style="margin: 8px 0;"><strong>Asunto:</strong> <em>{ai_content.get('subject', 'Sin asunto')}</em></p>
            <div style="background-color: #ffffff; padding: 12px; border-radius: 5px; margin: 10px 0; border-left: 3px solid #007bff;">
                <p style="margin: 0; font-size: 14px; color: #333; line-height: 1.4;">{preview_body}</p>
            </div>
            <p style="font-size: 12px; color: #6c757d; font-style: italic; margin: 5px 0;">
                💡 El email completo personalizado se abrirá al hacer clic en "Aplicar con IA"
            </p>
        </div>
        """
    
    def create_enhanced_email_content(self, offers: List[Dict]) -> tuple[str, str]:
        """Create enhanced HTML and text content for email notification with AI features"""
        
        # HTML content with modern styling
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nueva Oportunidad de Pasantía - UBA</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; }}
        .header {{ background: linear-gradient(135deg, #003366, #0056b3); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 300; }}
        .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 25px; }}
        .ai-badge {{ background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block; margin-bottom: 20px; }}
        .footer {{ margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px; font-size: 13px; color: #666; text-align: center; border-top: 1px solid #dee2e6; }}
        .university-link {{ color: #003366; text-decoration: none; }}
        .timestamp {{ color: #888; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Nueva Oportunidad de Pasantía</h1>
            <p>Facultad de Derecho - Universidad de Buenos Aires</p>
        </div>
        <div class="content">
            <div class="ai-badge">🤖 Con Asistente de IA para Aplicaciones Personalizadas</div>
        """
        
        # Add enhanced offers
        for offer in offers:
            html_content += self.create_ai_enhanced_offer_html(offer)
        
        # Footer
        html_content += f"""
        </div>
        <div class="footer">
            <p><strong>📊 Información del Monitor:</strong></p>
            <p>Email generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
            <p>🔗 <a href="https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php" class="university-link">Ver página oficial de ofertas</a></p>
            <p style="margin-top: 15px; font-size: 11px;">
                ⚠️ <strong>IMPORTANTE:</strong> La oficina de Pasantías no recepciona los CV ni forma parte del proceso de selección.<br>
                Envía tu CV directamente al email de contacto de cada oferta usando los botones de aplicación.
            </p>
            <p style="margin-top: 10px; font-size: 11px; color: #28a745;">
                🤖 <strong>Nuevo:</strong> Los emails con IA están personalizados según tu perfil profesional para mayor efectividad.
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        # Text content
        text_content = f"""
🎓 NUEVA PASANTÍA UBA DETECTADA (Con Asistente IA 🤖)
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
                text_content += f"🤖 Email personalizado con IA disponible en la versión HTML\n"
            else:
                text_content += "⏰ Email de contacto: Se publica 24hs después de la oferta\n"
            
            if offer.get('mas_informacion_url'):
                text_content += f"🔗 Más info: {offer['mas_informacion_url']}\n"
            
            text_content += "\n"
        
        text_content += f"""
{"="*50}
🔗 Página original: https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php
📊 Email generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
🤖 Nuevo: Emails con IA personalizados disponibles (ver versión HTML)

⚠️ IMPORTANTE: La oficina de Pasantías no recepciona los CV ni forma parte 
del proceso de selección. Envía tu CV directamente al email de contacto de cada oferta.
        """
        
        return html_content, text_content
    
    def send_notification(self, offers: List[Dict]) -> bool:
        """Send email notification for new offers with AI enhancements"""
        
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
            
            # Create enhanced email content
            html_content, text_content = self.create_enhanced_email_content(offers)
            
            # Setup email message
            msg = MIMEMultipart('alternative')
            
            # Subject
            if len(offers) == 1:
                offer_title = offers[0].get('numero_busqueda', offers[0].get('numero', offers[0].get('titulo', 'Nueva oferta')))
                if 'subject_single' in notification_settings:
                    subject = notification_settings['subject_single'].format(titulo=offer_title)
                else:
                    subject = f"🎓 Nueva Pasantía UBA: {offer_title}"
            else:
                if 'subject_template' in notification_settings:
                    subject = notification_settings['subject_template'].format(total=len(offers))
                else:
                    subject = f"🎓 Nueva Pasantía UBA Detectada - {len(offers)} ofertas"
            
            subject += " 🤖 (Con IA)"  # Add AI indicator to subject
            
            # Email headers
            msg['From'] = formataddr((email_settings['sender_name'], email_settings['sender_email']))
            msg['To'] = notification_settings['recipient_email']
            msg['Subject'] = subject
            
            # Anti-spam headers
            msg['X-Mailer'] = 'UBA Pasantias Monitor v2.0'
            msg['X-Priority'] = '3'
            msg['X-MSMail-Priority'] = 'Normal'
            msg['Importance'] = 'Normal'
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port']) as server:
                server.starttls(context=context)
                server.login(email_settings['sender_email'], email_settings['sender_password'])
                
                text = msg.as_string()
                server.sendmail(email_settings['sender_email'], notification_settings['recipient_email'], text)
            
            logger.info(f"AI-enhanced notification email sent successfully to {notification_settings['recipient_email']} for {len(offers)} offers")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send AI-enhanced notification email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email with sample AI-enhanced content"""
        
        # Create test offers with current offers data
        test_offers = [
            {
                "numero": "3366 (Test)",
                "numero_busqueda": "3366",
                "empresa": "Industria Textil Cladd",
                "area": "Industria Textil",
                "fecha_publicacion": "10/11/2024",
                "horario": "9 a 13 hs",
                "asignacion_estimulo": "500.000",
                "lugar": "CABA",
                "contacto_email": "test@example.com",
                "mas_informacion_url": "https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/2025/industria-textil-cladd"
            }
        ]
        
        logger.info("Sending AI-enhanced test email")
        return self.send_notification(test_offers)

if __name__ == "__main__":
    # Test the AI-enhanced email sender
    sender = AIEmailSender()
    
    # Test offers
    test_offers = [
        {
            "numero_busqueda": "2024-001",
            "fecha_publicacion": "15/01/2024",
            "area": "Derecho Comercial",
            "horario": "Lunes a Viernes 9:00 a 13:00",
            "asignacion_estimulo": "50000",
            "contacto_email": "rrhh@empresa.com",
            "mas_informacion_url": "https://ejemplo.com/info"
        }
    ]
    
    # Test email sending
    if sender.validate_config():
        success = sender.send_notification(test_offers)
        print(f"Test email sent: {success}")
    else:
        print("Configuration not valid - check config.json")