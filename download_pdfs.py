import csv
import os
import requests
import re
import logging
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Ensure filename is not too long
    return filename[:200]

def get_filename_from_url(url):
    # Parse the URL and get the path
    parsed = urlparse(url)
    path = parsed.path
    
    # If it's an aspx page, create a filename using query parameters
    if '.aspx' in path.lower():
        # Use the PRID or last part of the URL
        if 'PRID=' in url:
            prid = re.search(r'PRID=(\d+)', url)
            if prid:
                return f"document_{prid.group(1)}.pdf"
    
    # Default to last part of path or generated name
    filename = os.path.basename(path) or 'document.pdf'
    return sanitize_filename(filename)

csv_file = 'pdfs.csv'
pdf_folder = 'pdfs'

if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        link = row['Link']
        if link:
            try:
                pdf_name = get_filename_from_url(link)
                pdf_path = os.path.join(pdf_folder, pdf_name)
                
                logger.info(f"Downloading {link} to {pdf_path}")
                response = requests.get(link)
                response.raise_for_status()
                
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                logger.info(f"Successfully downloaded {pdf_name}")
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {link}: {str(e)}")
            except OSError as e:
                logger.error(f"Failed to save file {pdf_path}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error processing {link}: {str(e)}")