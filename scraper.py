#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UBA Pasantías Web Scraper
Scrapes pasantías offers from UBA Law Faculty website
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PasantiasWebScraper:
    """Web scraper for UBA Law Faculty pasantías offers"""
    
    def __init__(self):
        self.url = "https://www.derecho.uba.ar/academica/asuntos_estudiantiles/pasantias/ofertas.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data_file = "data/ofertas_pasantias.json"
        
    def fetch_page(self) -> Optional[BeautifulSoup]:
        """Fetch the main pasantías page"""
        try:
            logger.info(f"Fetching page: {self.url}")
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("Page fetched successfully")
            return soup
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return None
    
    def extract_offers(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract pasantías offers from the page"""
        offers = []
        
        try:
            # Find all offer sections - they typically have "Búsqueda Nº" pattern
            # Look for divs or sections containing offer information
            
            # First, let's find the main content area
            content = soup.find('div', class_='content') or soup.find('main') or soup
            
            # Look for offer patterns - typically contains "Búsqueda Nº" followed by number
            text_content = content.get_text()
            
            # Find all instances of "Búsqueda Nº" followed by numbers
            busqueda_pattern = r'Búsqueda\s*Nº\s*(\d+)'
            matches = list(re.finditer(busqueda_pattern, text_content, re.IGNORECASE))
            
            # Also look for emails in the full page content
            page_emails = self._extract_all_emails(soup)
            
            for i, match in enumerate(matches):
                try:
                    # Extract offer number
                    offer_number = match.group(1)
                    
                    # Find the start and end positions for this offer
                    start_pos = match.start()
                    end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text_content)
                    
                    # Extract the text for this specific offer
                    offer_text = text_content[start_pos:end_pos]
                    
                    # Extract details using regex patterns
                    offer_data = self._extract_offer_details(offer_text, offer_number, soup)
                    
                    # Try to find email for this specific offer in the page
                    if offer_data and not offer_data.get('contacto_email'):
                        offer_data['contacto_email'] = self._find_offer_email(offer_number, soup, page_emails)
                    
                    if offer_data:
                        offers.append(offer_data)
                        logger.info(f"Extracted offer #{offer_number}")
                    
                except Exception as e:
                    logger.error(f"Error extracting offer {i}: {e}")
                    continue
            
            logger.info(f"Total offers extracted: {len(offers)}")
            return offers
            
        except Exception as e:
            logger.error(f"Error extracting offers: {e}")
            return []
    
    def _extract_offer_details(self, offer_text: str, offer_number: str, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract detailed information from a single offer"""
        try:
            offer_data = {
                'numero_busqueda': offer_number,
                'fecha_publicacion': self._extract_fecha_publicacion(offer_text),
                'horario': self._extract_horario(offer_text),
                'asignacion_estimulo': self._extract_asignacion(offer_text),
                'area': self._extract_area(offer_text, soup),
                'contacto_email': None,  # Will be filled later with detailed page
                'mas_informacion_url': self._find_mas_informacion_url(offer_number, soup),
                'fecha_scraping': datetime.now().isoformat(),
                'texto_completo': offer_text.strip()
            }
            
            # Try to get additional details from the "MÁS INFORMACIÓN" link
            if offer_data['mas_informacion_url']:
                detailed_info = self._fetch_detailed_info(offer_data['mas_informacion_url'])
                if detailed_info:
                    offer_data.update(detailed_info)
            
            return offer_data
            
        except Exception as e:
            logger.error(f"Error extracting details for offer {offer_number}: {e}")
            return None
    
    def _extract_fecha_publicacion(self, text: str) -> Optional[str]:
        """Extract publication date from offer text"""
        fecha_pattern = r'Fecha\s*de\s*publicación:\s*(\d{1,2}-\d{1,2}-\d{4})'
        match = re.search(fecha_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_horario(self, text: str) -> Optional[str]:
        """Extract work schedule from offer text"""
        horario_pattern = r'Horario:\s*([^:]+?)(?=Asignación|$)'
        match = re.search(horario_pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_asignacion(self, text: str) -> Optional[str]:
        """Extract salary/stipend information from offer text"""
        asignacion_pattern = r'Asignación\s*estímulo:\s*\$?([\d.,]+)'
        match = re.search(asignacion_pattern, text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_area(self, text: str, soup: BeautifulSoup) -> Optional[str]:
        """Extract area/department information"""
        area_pattern = r'Area:\s*([^\n]+)'
        match = re.search(area_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Alternative: look for area in nearby headings
        for h2 in soup.find_all(['h2', 'h3'], string=re.compile(r'Area:', re.IGNORECASE)):
            return h2.get_text().replace('Area:', '').strip()
        
        return None
    
    def _find_mas_informacion_url(self, offer_number: str, soup: BeautifulSoup) -> Optional[str]:
        """Find the 'MÁS INFORMACIÓN' URL for the specific offer"""
        # Look for links containing "MÁS INFORMACIÓN" near the offer
        for link in soup.find_all('a', string=re.compile(r'MÁS\s*INFORMACIÓN', re.IGNORECASE)):
            href = link.get('href')
            if href and (offer_number in href or 'pasantias' in href):
                # Convert relative URL to absolute
                if href.startswith('/'):
                    return f"https://www.derecho.uba.ar{href}"
                elif href.startswith('http'):
                    return href
                else:
                    # For relative URLs, add the base domain only
                    return f"https://www.derecho.uba.ar/{href}"
        return None
    
    def _fetch_detailed_info(self, url: str) -> Dict:
        """Fetch additional information from the detailed offer page"""
        try:
            logger.info(f"Fetching detailed info from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            detailed_info = {}
            
            # Extract email address (often appears 24 hours after publication)
            text_content = soup.get_text()
            
            # Look for the specific email pattern that appears after "envíe un mail adjuntando su CV a:"
            email_context_pattern = r'envíe\s+un\s+mail\s+adjuntando\s+su\s+cv\s+a:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            context_match = re.search(email_context_pattern, text_content, re.IGNORECASE)
            
            if context_match:
                detailed_info['contacto_email'] = context_match.group(1)
            else:
                # Fallback: look for any email that's not a general UBA email
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                email_matches = re.findall(email_pattern, text_content)
                
                # Filter out generic UBA emails
                exclude_emails = [
                    'diralumnos@derecho.uba.ar',
                    'posgrado@derecho.uba.ar', 
                    'biblio@derecho.uba.ar',
                    'pasantia@derecho.uba.ar'  # This is generic
                ]
                
                for email in email_matches:
                    if email.lower() not in [e.lower() for e in exclude_emails]:
                        detailed_info['contacto_email'] = email
                        break
            
            # Extract additional details like requirements, description, etc.
            detailed_info['descripcion_completa'] = self._clean_text(text_content)
            
            return detailed_info
            
        except Exception as e:
            logger.error(f"Error fetching detailed info from {url}: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()
    
    def _extract_all_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract all email addresses from the page"""
        emails = []
        
        # Get all text content
        text_content = soup.get_text()
        
        # Find all email patterns
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found_emails = re.findall(email_pattern, text_content)
        
        # Filter out common non-contact emails
        exclude_patterns = [
            'diralumnos@derecho.uba.ar',
            'areageneroest@derecho.uba.ar', 
            'posgrado@derecho.uba.ar',
            'biblio@derecho.uba.ar'
        ]
        
        for email in found_emails:
            if email.lower() not in [e.lower() for e in exclude_patterns]:
                emails.append(email)
        
        return list(set(emails))  # Remove duplicates
    
    def _find_offer_email(self, offer_number: str, soup: BeautifulSoup, page_emails: List[str]) -> Optional[str]:
        """Find specific email for an offer"""
        
        # First check if we can get the email from the detailed page
        mas_info_url = self._find_mas_informacion_url(offer_number, soup)
        if mas_info_url:
            try:
                detailed_info = self._fetch_detailed_info(mas_info_url)
                if detailed_info.get('contacto_email'):
                    return detailed_info['contacto_email']
            except:
                pass
        
        # If detailed page fails, look in main page
        # First, look for emails near the offer number in the HTML
        offer_pattern = f"Búsqueda\\s*Nº\\s*{offer_number}"
        
        # Split the HTML into sections and look for emails near our offer
        html_text = str(soup)
        
        # Find position of our offer
        match = re.search(offer_pattern, html_text, re.IGNORECASE)
        if match:
            # Look in a window around the offer (2000 characters before and after)
            start_pos = max(0, match.start() - 2000)
            end_pos = min(len(html_text), match.end() + 2000)
            offer_section = html_text[start_pos:end_pos]
            
            # Look for emails in this section
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            section_emails = re.findall(email_pattern, offer_section)
            
            # Return the first email found in this section that's not a general UBA email
            for email in section_emails:
                if 'derecho.uba.ar' not in email.lower() or offer_number in email:
                    return email
        
        # If no specific email found, return the first non-standard email from the page
        for email in page_emails:
            if 'derecho.uba.ar' not in email.lower():
                return email
        
        return None
    
    def load_previous_data(self) -> Dict:
        """Load previously scraped data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading previous data: {e}")
                return {}
        return {}
    
    def save_data(self, offers: List[Dict]) -> None:
        """Save scraped data to JSON file"""
        try:
            # Load existing data
            existing_data = self.load_previous_data()
            
            # Create a dictionary with offer numbers as keys for easy lookup
            offers_dict = {offer['numero_busqueda']: offer for offer in offers}
            
            # Update existing data
            if 'ofertas' not in existing_data:
                existing_data['ofertas'] = {}
            
            existing_data['ofertas'].update(offers_dict)
            existing_data['ultima_actualizacion'] = datetime.now().isoformat()
            
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Save updated data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Data saved to {self.data_file}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def find_new_offers(self, current_offers: List[Dict]) -> List[Dict]:
        """Find new offers by comparing with previously saved data"""
        try:
            previous_data = self.load_previous_data()
            previous_offers = previous_data.get('ofertas', {})
            
            new_offers = []
            for offer in current_offers:
                offer_number = offer['numero_busqueda']
                if offer_number not in previous_offers:
                    new_offers.append(offer)
                    logger.info(f"New offer found: #{offer_number}")
            
            return new_offers
            
        except Exception as e:
            logger.error(f"Error finding new offers: {e}")
            return current_offers  # Return all offers if comparison fails
    
    def scrape(self) -> tuple[List[Dict], List[Dict]]:
        """
        Main scraping method
        Returns: (all_offers, new_offers)
        """
        logger.info("Starting pasantías scraping process")
        
        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Fetch and parse the page
        soup = self.fetch_page()
        if not soup:
            logger.error("Failed to fetch page, aborting scrape")
            return [], []
        
        # Extract offers
        current_offers = self.extract_offers(soup)
        if not current_offers:
            logger.warning("No offers found on page")
            return [], []
        
        # Find new offers
        new_offers = self.find_new_offers(current_offers)
        
        # Save all current offers
        self.save_data(current_offers)
        
        logger.info(f"Scraping completed. Total offers: {len(current_offers)}, New offers: {len(new_offers)}")
        
        return current_offers, new_offers

def main():
    """Test the scraper"""
    scraper = PasantiasWebScraper()
    all_offers, new_offers = scraper.scrape()
    
    print(f"\n=== RESULTADO DEL SCRAPING ===")
    print(f"Total ofertas encontradas: {len(all_offers)}")
    print(f"Ofertas nuevas: {len(new_offers)}")
    
    if new_offers:
        print("\n=== NUEVAS OFERTAS ===")
        for offer in new_offers:
            print(f"\nOFERTA #{offer['numero_busqueda']}")
            print(f"Fecha: {offer.get('fecha_publicacion', 'N/A')}")
            print(f"Área: {offer.get('area', 'N/A')}")
            print(f"Horario: {offer.get('horario', 'N/A')}")
            print(f"Asignación: ${offer.get('asignacion_estimulo', 'N/A')}")
            if offer.get('contacto_email'):
                print(f"Email: {offer['contacto_email']}")

if __name__ == "__main__":
    main()