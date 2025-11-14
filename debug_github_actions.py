#!/usr/bin/env python3
"""
Debugging script for GitHub Actions email issues
"""

import os
import json
from email_sender_ai import AIEmailSender

def debug_github_actions():
    """Debug GitHub Actions configuration"""
    
    print("=== GITHUB ACTIONS DEBUG ===\n")
    
    # Check environment variables
    print("1. Environment Variables:")
    required_vars = [
        'SENDER_EMAIL', 'EMAIL_PASSWORD', 'SENDER_PASSWORD', 
        'RECIPIENT_EMAIL', 'SMTP_SERVER', 'SMTP_PORT', 
        'OPENAI_API_KEY', 'GITHUB_ACTIONS'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive info
            if 'PASSWORD' in var or 'KEY' in var:
                display_value = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                display_value = value
            print(f"   ✓ {var}: {display_value}")
        else:
            print(f"   ✗ {var}: Not set")
    
    # Check config file
    print(f"\n2. Config File:")
    if os.path.exists('config.json'):
        print("   ✓ config.json exists")
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            print("   ✓ config.json is valid JSON")
            print(f"   ✓ Has sender_email: {'email_settings' in config and 'sender_email' in config.get('email_settings', {})}")
            print(f"   ✓ Has openai key: {'ai_settings' in config and 'openai_api_key' in config.get('ai_settings', {})}")
        except Exception as e:
            print(f"   ✗ Error reading config.json: {e}")
    else:
        print("   ✗ config.json does not exist")
    
    # Test email sender initialization
    print(f"\n3. Email Sender Test:")
    try:
        sender = AIEmailSender()
        print("   ✓ AIEmailSender initialized")
        
        valid_config = sender.validate_config()
        print(f"   {'✓' if valid_config else '✗'} Configuration valid: {valid_config}")
        
        user_emails = sender.ai_agent.get_user_emails()
        print(f"   ✓ Users configured: {len(user_emails)}")
        for user_id, email in user_emails.items():
            print(f"     - {user_id}: {email}")
            
    except Exception as e:
        print(f"   ✗ Error initializing email sender: {e}")
    
    # Test OpenAI
    print(f"\n4. OpenAI Test:")
    try:
        from ai_agent import AIJobApplicationAgent
        agent = AIJobApplicationAgent()
        print("   ✓ AI Agent initialized")
        
        # Test with sample offer
        sample_offer = {
            'numero_busqueda': 'TEST',
            'area': 'Test Area',
            'horario': '9 a 13 hs',
            'asignacion_estimulo': '50000'
        }
        
        result = agent.generate_personalized_email(sample_offer, 'damian')
        print(f"   {'✓' if result['success'] else '✗'} AI email generation: {result['success']}")
        
    except Exception as e:
        print(f"   ✗ Error testing OpenAI: {e}")
    
    print(f"\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_github_actions()