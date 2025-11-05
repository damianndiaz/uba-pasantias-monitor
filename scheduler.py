#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UBA Pasantías Monitor - Main Scheduler Script
Automated monitoring of UBA Law Faculty internship offers with email notifications
"""

import schedule
import time
import json
import os
import logging
import sys
from datetime import datetime, timedelta
import signal
from typing import Optional

# Import our custom modules
from scraper import PasantiasWebScraper
from email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PasantiasMonitor:
    """Main monitoring class that coordinates scraping and notifications"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the monitor"""
        self.config_file = config_file
        self.scraper = PasantiasWebScraper()
        self.email_sender = EmailSender(config_file)
        self.running = True
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Ensure necessary directories exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        logger.info("UBA Pasantías Monitor initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def check_for_new_offers(self) -> bool:
        """
        Main monitoring function - checks for new offers and sends notifications
        Returns True if successful, False if there was an error
        """
        try:
            logger.info("Starting scheduled check for new pasantías offers")
            
            # Scrape current offers
            all_offers, new_offers = self.scraper.scrape()
            
            if not all_offers:
                logger.warning("No offers found during scraping")
                return False
            
            logger.info(f"Found {len(all_offers)} total offers, {len(new_offers)} new offers")
            
            # Send notifications for new offers
            if new_offers:
                logger.info(f"Sending notifications for {len(new_offers)} new offers")
                success = self.email_sender.send_notification(new_offers)
                
                if success:
                    logger.info("Email notifications sent successfully")
                    self._log_notification_sent(new_offers)
                else:
                    logger.error("Failed to send email notifications")
                    return False
            else:
                logger.info("No new offers found, no notifications to send")
            
            # Update last check time
            self._update_last_check_time()
            
            return True
            
        except Exception as e:
            logger.error(f"Error during scheduled check: {e}", exc_info=True)
            return False
    
    def _log_notification_sent(self, offers: list):
        """Log details of notifications sent"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'offers_notified': [offer['numero_busqueda'] for offer in offers],
            'total_offers': len(offers)
        }
        
        log_file = 'logs/notifications.json'
        
        # Load existing log
        notifications_log = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    notifications_log = json.load(f)
            except Exception as e:
                logger.error(f"Error loading notifications log: {e}")
        
        # Add new entry
        notifications_log.append(log_entry)
        
        # Keep only last 100 entries
        notifications_log = notifications_log[-100:]
        
        # Save updated log
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(notifications_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving notifications log: {e}")
    
    def _update_last_check_time(self):
        """Update the last successful check timestamp"""
        timestamp_file = 'data/last_check.json'
        
        data = {
            'last_check': datetime.now().isoformat(),
            'status': 'success'
        }
        
        try:
            with open(timestamp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error updating last check time: {e}")
    
    def get_last_check_time(self) -> Optional[datetime]:
        """Get the last successful check timestamp"""
        timestamp_file = 'data/last_check.json'
        
        if not os.path.exists(timestamp_file):
            return None
        
        try:
            with open(timestamp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return datetime.fromisoformat(data['last_check'])
        except Exception as e:
            logger.error(f"Error reading last check time: {e}")
            return None
    
    def run_manual_check(self):
        """Run a manual check (for testing or immediate execution)"""
        logger.info("Running manual check for new offers")
        success = self.check_for_new_offers()
        
        if success:
            print("✅ Manual check completed successfully")
        else:
            print("❌ Manual check failed - check logs for details")
        
        return success
    
    def setup_schedule(self):
        """Setup the automated schedule"""
        # Try to load configuration for scheduling
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                check_hours = config.get('monitoring_settings', {}).get('check_frequency_hours', 24)
            else:
                check_hours = 24
                logger.warning(f"Config file not found, using default check frequency: {check_hours} hours")
        
        except Exception as e:
            logger.error(f"Error loading schedule config: {e}")
            check_hours = 24
        
        # Schedule the job
        if check_hours >= 24:
            # Daily at specific time
            schedule.every().day.at("09:00").do(self.check_for_new_offers)
            logger.info("Scheduled daily check at 09:00")
        else:
            # Every X hours
            schedule.every(check_hours).hours.do(self.check_for_new_offers)
            logger.info(f"Scheduled check every {check_hours} hours")
    
    def run_scheduler(self):
        """Run the main scheduler loop"""
        logger.info("Starting UBA Pasantías Monitor scheduler")
        
        # Setup schedule
        self.setup_schedule()
        
        # Show next scheduled run
        next_run = schedule.next_run()
        if next_run:
            logger.info(f"Next scheduled check: {next_run}")
        
        print("\n🎓 UBA PASANTÍAS MONITOR INICIADO")
        print(f"⏰ Próxima revisión: {next_run}")
        print("🔄 El monitor revisará automáticamente la página de pasantías")
        print("📧 Te enviará un email cuando encuentre nuevas ofertas")
        print("\nPresiona Ctrl+C para detener el monitor\n")
        
        # Main scheduler loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait before retrying
        
        logger.info("UBA Pasantías Monitor stopped")
        print("\n👋 Monitor detenido. ¡Hasta luego!")
    
    def show_status(self):
        """Show current monitoring status"""
        print("\n📊 ESTADO DEL MONITOR UBA PASANTÍAS")
        print("=" * 50)
        
        # Last check time
        last_check = self.get_last_check_time()
        if last_check:
            print(f"🕐 Última revisión: {last_check.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Time since last check
            time_diff = datetime.now() - last_check
            if time_diff.days > 0:
                print(f"⏳ Hace: {time_diff.days} días, {time_diff.seconds//3600} horas")
            else:
                print(f"⏳ Hace: {time_diff.seconds//3600} horas, {(time_diff.seconds//60)%60} minutos")
        else:
            print("🕐 Última revisión: Nunca")
        
        # Next scheduled run
        next_run = schedule.next_run()
        if next_run:
            print(f"⏰ Próxima revisión: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Configuration status
        config_valid = self.email_sender.validate_config()
        print(f"⚙️  Configuración: {'✅ Válida' if config_valid else '❌ Incompleta'}")
        
        # Data files
        data_exists = os.path.exists('data/ofertas_pasantias.json')
        print(f"💾 Datos guardados: {'✅ Sí' if data_exists else '❌ No'}")
        
        # Notification logs
        notif_log_exists = os.path.exists('logs/notifications.json')
        if notif_log_exists:
            try:
                with open('logs/notifications.json', 'r', encoding='utf-8') as f:
                    notif_log = json.load(f)
                print(f"📧 Notificaciones enviadas: {len(notif_log)}")
            except:
                print("📧 Notificaciones enviadas: Error leyendo log")
        else:
            print("📧 Notificaciones enviadas: 0")
        
        print()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UBA Pasantías Monitor')
    parser.add_argument('--check', action='store_true', 
                       help='Run a manual check for new offers')
    parser.add_argument('--status', action='store_true', 
                       help='Show current monitoring status')
    parser.add_argument('--test-email', action='store_true', 
                       help='Send a test email notification')
    parser.add_argument('--config', default='config.json', 
                       help='Configuration file path (default: config.json)')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = PasantiasMonitor(args.config)
    
    if args.status:
        monitor.show_status()
    elif args.check:
        monitor.run_manual_check()
    elif args.test_email:
        print("Enviando email de prueba...")
        if monitor.email_sender.send_test_email():
            print("✅ Email de prueba enviado")
        else:
            print("❌ Error enviando email de prueba")
    else:
        # Run the scheduler
        monitor.run_scheduler()

if __name__ == "__main__":
    main()