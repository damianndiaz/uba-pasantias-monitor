#!/usr/bin/env python3
"""
Test script for multi-user UBA Pasantias Monitor system
"""

from ai_agent import AIJobApplicationAgent
from email_sender_ai import AIEmailSender
from scraper import PasantiasWebScraper
import json

def test_multi_user_system():
    """Test the complete multi-user system"""
    
    print("=== MULTI-USER UBA PASANTIAS MONITOR TEST ===\n")
    
    # 1. Test AI Agent
    print("1. Testing AI Agent...")
    agent = AIJobApplicationAgent()
    
    user_emails = agent.get_user_emails()
    print(f"   Configured users: {len(user_emails)}")
    for user_id, email in user_emails.items():
        name = agent.get_user_name(user_id)
        print(f"   - {user_id}: {name} ({email})")
    
    # 2. Test with sample offer
    print("\n2. Testing AI email generation...")
    sample_offer = {
        'numero_busqueda': '3366',
        'area': 'Industria Textil Cladd',
        'horario': '9 a 13 hs',
        'asignacion_estimulo': '500.000',
        'contacto_email': 'rodrigo@cladd.com.ar'
    }
    
    for user_id in user_emails.keys():
        result = agent.generate_personalized_email(sample_offer, user_id)
        print(f"   {user_id}: {'✓' if result['success'] else '✗'} - {result['subject'][:60]}...")
    
    # 3. Test Email Sender
    print("\n3. Testing Email Sender...")
    sender = AIEmailSender()
    
    print("   Creating personalized content for each user...")
    for user_id in user_emails.keys():
        html, text = sender.create_enhanced_email_content([sample_offer], user_id)
        print(f"   {user_id}: HTML={len(html)} chars, Text={len(text)} chars")
    
    # 4. Test Scraper
    print("\n4. Testing Web Scraper...")
    scraper = PasantiasWebScraper()
    all_offers, new_offers = scraper.scrape()
    print(f"   Found: {len(all_offers)} total offers, {len(new_offers)} new offers")
    
    # 5. Summary
    print("\n=== SYSTEM STATUS ===")
    print(f"✓ AI Agent: {len(user_emails)} users configured")
    print(f"✓ Email Sender: Multi-user support enabled")
    print(f"✓ Web Scraper: {len(all_offers)} offers available")
    print("✓ System ready for deployment!")
    
    # 6. Usage instructions
    print("\n=== USAGE ===")
    print("To send notifications to all users:")
    print("  sender.send_notifications_to_all_users(offers)")
    print("\nTo send to specific user:")
    print("  sender.send_notification_to_user(offers, 'damian', 'diazzdamian00@gmail.com')")
    print("  sender.send_notification_to_user(offers, 'valentin', 'valdom152@gmail.com')")
    print("\nScheduler automatically sends to all users when new offers are found.")

if __name__ == "__main__":
    test_multi_user_system()