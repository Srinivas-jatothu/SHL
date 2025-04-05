import os
import sys
import requests
import csv
from bs4 import BeautifulSoup
import time
import fitz  

try:
    from jobcatalog import fetch_page, parse_job_catalog  # Use absolute import if jobcatalog is in the same directory
except ImportError:
    print("Error: 'jobcatalog' module not found. Ensure 'jobcatalog.py' is in the same directory or provide the correct path.")
    sys.exit(1)












# Main function to run the scraping and saving process
def main():
    # The URL of the product catalog page you want to scrape
    url = "https://www.shl.com/solutions/products/product-catalog"  
    
    # Fetch the main page content
    page_content = fetch_page(url)
    
    if page_content:
        # Parse the content of the main catalog page to extract job solution links
        job_solutions = parse_job_catalog(page_content)
        
        # Define the path where the CSV file will be saved
        filepath = r"C:\Users\jsrin\OneDrive\Desktop\SHL\Main\job_solutions_with_details.csv"
        
        # Save the job solution data to a CSV file
        save_to_csv(job_solutions, filepath)
        print(f"Data has been saved to {filepath}")
    else:
        print("Failed to retrieve the main page content.")

# Entry point for the script
if __name__ == "__main__":
    main()
