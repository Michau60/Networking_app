import requests
from bs4 import BeautifulSoup

def get_public_ip_from_html():
    try:
        # Pobierz zawartość strony
        response = requests.get('https://michau.bieda.it/get_ip.php')
        response.raise_for_status()
        
        public_ip = BeautifulSoup(response.text, 'html.parser')

        return str(public_ip)
    except Exception as e:
        return f"Error: {e}"
