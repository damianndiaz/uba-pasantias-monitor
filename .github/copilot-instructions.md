# UBA Pasantías Monitor

This project monitors the UBA Law Faculty internship offers page and sends email notifications when new offers are posted.

## Technologies
- Python 3.x
- Web scraping with requests and BeautifulSoup
- Email notifications with smtplib
- Automated scheduling with schedule library
- JSON for data persistence

## Features
- Automatic daily monitoring of pasantías page
- Detection of new offers by comparing with stored data
- Email notifications with offer details and contact information
- Configurable email settings via config file
- Logging of all activities

## Project Structure
- `scraper.py`: Web scraping module
- `email_sender.py`: Email notification system  
- `scheduler.py`: Main script with automation
- `config.json`: Configuration file for email settings
- `data/`: Directory for storing offer data
- `logs/`: Directory for log files