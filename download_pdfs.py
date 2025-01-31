
import csv
import os
import requests

csv_file = 'pdfs.csv'
pdf_folder = 'pdfs'

if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        link = row['Link']
        if link:
            pdf_name = link.split('/')[-1]
            pdf_path = os.path.join(pdf_folder, pdf_name)
            response = requests.get(link)
            with open(pdf_path, 'wb') as pdf_file:
                pdf_file.write(response.content)