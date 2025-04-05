import json
import os
import requests
from bs4 import BeautifulSoup
import time
import fitz  # PyMuPDF for PDF text extraction

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
# def fetch_job_details(url):
#     page_content = fetch_page(url)
#     if not page_content:
#         return {}
    
#     soup = BeautifulSoup(page_content, 'html.parser')
    
#     # Extract the description of the job
#     description_tag = soup.find('div', class_='product-catalogue-training-calendar__row')
#     description = description_tag.find('p').get_text(strip=True) if description_tag else "No description available"
    
#     # Extract other relevant information, e.g., job levels, languages, assessment length
#     job_levels = "Not specified"
#     job_levels_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Job levels')
#     if job_levels_tag:
#         job_levels = job_levels_tag.find_next('p').get_text(strip=True)

#     languages = "Not specified"
#     languages_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Languages')
#     if languages_tag:
#         languages = languages_tag.find_next('p').get_text(strip=True)
    
#     assessment_length = "Not specified"
#     assessment_tag = soup.find('div', class_='product-catalogue-training-calendar__row typ', string='Assessment length')
#     if assessment_tag:
#         assessment_length = assessment_tag.find_next('p').get_text(strip=True)

#     # Extract test type keys
#     test_type = []
#     keys = soup.find_all('span', class_='product-catalogue__key')
#     for key in keys:
#         test_type.append(key.get_text(strip=True))
    
#     # Check for Remote Testing
#     remote_testing = "No"
#     remote_tag = soup.find('p', string="Remote Testing")
#     if remote_tag and remote_tag.find('span', class_='catalogue__circle -yes'):
#         remote_testing = "Yes"

#     # Download link (if any)
#     downloads = []
#     download_links = soup.find_all('a', href=True)
#     for link in download_links:
#         if 'Fact Sheet' in link.get_text():
#             downloads.append(link['href'])
    
#     # If there are any downloads, download the PDFs and extract text
#     pdf_data = []
#     for download_url in downloads:
#         pdf_path, pdf_content = download_pdf(download_url)
#         if pdf_path and pdf_content:
#             pdf_data.append({
#                 'PDF Link': download_url,
#                 'PDF Path': pdf_path,
#                 'PDF Content': pdf_content  # Store the full content of the PDF here
#             })
    
#     return {
#         'Description': description,
#         'Job Levels': job_levels,
#         'Languages': languages,
#         'Assessment Length': assessment_length,
#         'Test Type': ', '.join(test_type),
#         'Remote Testing': remote_testing,
#         'Downloads': ', '.join(downloads),
#         'PDF Data': pdf_data  # Added PDF Data to include all PDFs and their full content
#     }

# Function to scrape detailed information from the job page
def fetch_job_details(url):
    page_content = fetch_page(url)
    if not page_content:
        return {}
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract the description of the job
    description_tag = soup.find('div', class_='product-catalogue-training-calendar__row')
    description = description_tag.find('p').get_text(strip=True) if description_tag else "No description available"
    
    # Extract Job Levels
    job_levels = "Not specified"
    job_levels_tag = soup.find('h4', string='Job levels')
    if job_levels_tag:
        job_levels = job_levels_tag.find_next('p').get_text(strip=True)
    
    # Extract Languages
    languages = "Not specified"
    languages_tag = soup.find('h4', string='Languages')
    if languages_tag:
        languages = languages_tag.find_next('p').get_text(strip=True)
    
    # Extract Assessment Length
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
    
    # If there are any downloads, download the PDFs and extract text
    pdf_data = []
    for download_url in downloads:
        pdf_path, pdf_content = download_pdf(download_url)
        if pdf_path and pdf_content:
            pdf_data.append({
                'PDF Link': download_url,
                'PDF Path': pdf_path,
                'PDF Content': pdf_content  # Store the full content of the PDF here
            })
    
    return {
        'Description': description,
        'Job Levels': job_levels,
        'Languages': languages,
        'Assessment Length': assessment_length,
        'Test Type': ', '.join(test_type),
        'Remote Testing': remote_testing,
        'Downloads': ', '.join(downloads),
        'PDF Data': pdf_data  # Added PDF Data to include all PDFs and their full content
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
            text += page.get_text("text")  # Extract full text from each page
        return text
    except Exception as e:
        print(f"Failed to extract text from {pdf_path}: {e}")
        return None

# Saving the results to a JSON
def save_to_json(job_solutions, filepath):
    with open(filepath, mode='w', encoding='utf-8') as jsonfile:
        json.dump(job_solutions, jsonfile, indent=4, ensure_ascii=False)

# Main function
def main():
    url = "https://www.shl.com/solutions/products/product-catalog"  # The main page URL
    page_content = fetch_page(url)
    
    if page_content:
        # Parse the main page for job solutions links
        job_solutions = parse_job_catalog(page_content)
        
        # Save the data to a JSON file
        filepath = r"C:\Users\jsrin\OneDrive\Desktop\SHL\Main\job_solutions_with_details.json"
        save_to_json(job_solutions, filepath)
        print(f"Data has been saved to {filepath}")

if __name__ == "__main__":
    main()
