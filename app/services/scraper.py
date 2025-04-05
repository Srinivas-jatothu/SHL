# app/services/scraper.py
import httpx
from bs4 import BeautifulSoup

class URLScraperService:
    async def scrape_job_description(self, url: str) -> str:
        """Scrape job description from URL"""
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common job description containers
            # This is simplified - real implementation would need to handle various site layouts
            job_containers = soup.select('.job-description, .description, [class*=job], [class*=description]')
            
            if job_containers:
                return " ".join([container.get_text(strip=True) for container in job_containers])
            
            # Fallback to getting main content
            main_content = soup.select('main, article, .content')
            if main_content:
                return main_content[0].get_text(strip=True)
                
            # Last resort - get all text
            return soup.get_text(strip=True)