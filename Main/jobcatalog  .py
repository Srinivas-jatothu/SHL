import requests
from bs4 import BeautifulSoup
import time
import os
import fitz  # PyMuPDF for PDF text extraction
import csv

# Function to fetch page content
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the webpage: {url}, status code: {response.status_code}")
        return None

# Function to parse the product catalog page and extract job solution names, links, and attributes
def parse_job_catalog(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    job_solutions = []

    # Find the rows in the table (each row is a job solution)
    rows = soup.find_all('tr', {'data-course-id': True})

    for row in rows:
        job_name_tag = row.find('td', class_='custom__table-heading__title').find('a')
        job_name = job_name_tag.get_text(strip=True)
        job_url = "https://www.shl.com" + job_name_tag['href']  # Complete URL for the job solution
        
        # Scrape detailed information from the individual job solution page
        job_details = fetch_job_details(job_url)
        
        job_solutions.append({
            'Job Name': job_name,
            'URL': job_url,
            **job_details
        })
        
        # To avoid too many requests in a short time, we add a small delay
        time.sleep(1)
    
    return job_solutions

# Function to scrape detailed information from the job page
def fetch_job_details(url):
    page_content = fetch_page(url)
    if not page_content:
        return {}
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract the description of the job
    description_tag = soup.find('div', class_='product-catalogue-training-calendar__row')
    description = description_tag.find('p').get_text(strip=True) if description_tag else "No description available"
    
    # Extract other relevant information, e.g., job levels, languages, assessment length
    job_levels = "Not specified"
    job_levels_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Job levels')
    if job_levels_tag:
        job_levels = job_levels_tag.find_next('p').get_text(strip=True)

    languages = "Not specified"
    languages_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Languages')
    if languages_tag:
        languages = languages_tag.find_next('p').get_text(strip=True)
    
    assessment_length = "Not specified"
    assessment_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Assessment length')
    if assessment_tag:
        assessment_length = assessment_tag.find_next('p').get_text(strip=True)

    # Extract test type keys
    test_type = []
    keys = soup.find_all('span', class_='product-catalogue__key')
    for key in keys:
        test_type.append(key.get_text(strip=True))
    
    # Check for Remote Testing
    remote_testing = "No"
    remote_tag = soup.find('p', string="Remote Testing")
    if remote_tag and remote_tag.find('span', class_='catalogue__circle -yes'):
        remote_testing = "Yes"

    # Download link (if any)
    downloads = []
    download_links = soup.find_all('a', href=True)
    for link in download_links:
        if 'Fact Sheet' in link.get_text():
            downloads.append(link['href'])
    
    # If there are any downloads, download the PDF
    pdf_path = None
    pdf_content = None
    if downloads:
        pdf_path, pdf_content = download_pdf(downloads[0])
    
    return {
        'Description': description,
        'Job Levels': job_levels,
        'Languages': languages,
        'Assessment Length': assessment_length,
        'Test Type': ', '.join(test_type),
        'Remote Testing': remote_testing,
        'Downloads': ', '.join(downloads),
        'PDF Content': pdf_content
    }

# Function to download the PDF and extract text
def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    
    # If the request is successful, save the PDF file locally
    if response.status_code == 200:
        pdf_name = pdf_url.split("/")[-1]
        pdf_path = os.path.join("downloads", pdf_name)
        
        # Ensure the 'downloads' directory exists
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
        
        # Extract text from the downloaded PDF
        pdf_text = extract_pdf_text(pdf_path)
        
        # Return both the file path and the extracted text
        return pdf_path, pdf_text
    else:
        print(f"Failed to download PDF: {pdf_url}")
        return None, None

# Function to extract text from a PDF using PyMuPDF (fitz)
def extract_pdf_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text("text")
        return text
    except Exception as e:
        print(f"Failed to extract text from {pdf_path}: {e}")
        return None

# Function to save job data to a CSV file
def save_to_csv(job_solutions, filepath):
    fieldnames = ['Job Name', 'URL', 'Description', 'PDF Link', 'PDF Content', 'Languages', 'Remote Testing', 'Job Levels', 'Test Type', 'Assessment Length']

    with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for job in job_solutions:
            # Ensure the job dictionary has the correct structure
            job_data = {
                'Job Name': job.get('Job Name', ''),
                'URL': job.get('URL', ''),
                'Description': job.get('Description', ''),
                'PDF Link': job.get('Downloads', ''),
                'PDF Content': job.get('PDF Content', ''),
                'Languages': job.get('Languages', ''),
                'Remote Testing': job.get('Remote Testing', ''),
                'Job Levels': job.get('Job Levels', ''),
                'Test Type': job.get('Test Type', ''),
                'Assessment Length': job.get('Assessment Length', '')
            }
            writer.writerow(job_data)
