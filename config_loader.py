#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration loader for GitHub Actions and local environments
"""

import json
import os
from typing import Dict

def load_config() -> Dict:
    """Load configuration from environment variables or config.json file"""
    
    # Check if running in GitHub Actions (environment variables)
    if os.getenv('GITHUB_ACTIONS'):
        print("🔄 Running in GitHub Actions - Using environment variables")
        
        config = {
            "email_settings": {
                "smtp_server": os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                "smtp_port": int(os.getenv('SMTP_PORT', '587')),
                "sender_email": os.getenv('SENDER_EMAIL'),
                "sender_password": os.getenv('EMAIL_PASSWORD'),
                "sender_name": "UBA Pasantías Monitor"
            },
            "notification_settings": {
                "recipient_email": os.getenv('RECIPIENT_EMAIL'),
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
        
        # Validate required environment variables
        required_vars = ['SENDER_EMAIL', 'EMAIL_PASSWORD', 'RECIPIENT_EMAIL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
            
        return config
    
    else:
        # Running locally - use config.json
        print("🏠 Running locally - Using config.json")
        
        config_file = "config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"Config file {config_file} not found. Please create it first.")

def save_config_for_actions():
    """Helper function to show what environment variables to set in GitHub"""
    
    if os.path.exists("config.json"):
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("\n🔧 Para configurar GitHub Actions, necesitas estos secretos:")
        print("=" * 60)
        print(f"SENDER_EMAIL={config['email_settings']['sender_email']}")
        print(f"EMAIL_PASSWORD={config['email_settings']['sender_password']}")
        print(f"RECIPIENT_EMAIL={config['notification_settings']['recipient_email']}")
        print(f"SMTP_SERVER={config['email_settings']['smtp_server']}")
        print(f"SMTP_PORT={config['email_settings']['smtp_port']}")
        print("=" * 60)
    else:
        print("❌ No se encontró config.json")

if __name__ == "__main__":
    save_config_for_actions()