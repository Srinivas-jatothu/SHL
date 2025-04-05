# app/main.py
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
import json
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="SHL Assessment Recommender")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Models
class Assessment(BaseModel):
    id: str
    name: str
    url: str
    remote_testing_support: bool
    adaptive_irt_support: bool
    duration: str
    test_type: str
    description: Optional[str] = None

class JobDescription(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    max_results: Optional[int] = 10

class RecommendationResult(BaseModel):
    assessment: Assessment
    score: float
    relevance_explanation: str

class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationResult]

# Load SHL assessment data
def load_assessments():
    with open("app/data/assessments.json", "r") as f:
        return json.load(f)

# LLM Service
class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        
    async def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """
        Analyze job description using LLM to extract key information
        """
        prompt = f"""
        Analyze the following job description and extract key information:
        
        {job_text}
        
        Please provide:
        1. Primary role category (e.g., Software Developer, Financial Analyst)
        2. Seniority level (e.g., Entry, Mid, Senior)
        3. Top 10 skills required
        4. Industry context if specified
        5. Key cognitive abilities needed
        
        Format your answer as JSON.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a job analysis expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def generate_match_explanation(self, job_analysis: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """Generate explanation for why this assessment matches the job requirements"""
        prompt = f"""
        Given a job analysis and an assessment description, explain why this assessment is relevant for the job.
        
        Job Analysis:
        {json.dumps(job_analysis, indent=2)}
        
        Assessment:
        {json.dumps(assessment, indent=2)}
        
        Provide a concise explanation of how this assessment evaluates skills needed for the job.
        Limit your response to 3-4 sentences.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",  # Using a smaller model for explanations to reduce costs
            messages=[
                {"role": "system", "content": "You are an expert in talent assessment and hiring."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

# Recommendation Service
class RecommendationService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.assessments = load_assessments()
        
    async def get_recommendations(self, job_text: str, max_results: int = 10) -> List[RecommendationResult]:
        """
        Get assessment recommendations based on job description
        """
        # Use LLM to analyze job description
        job_analysis = await self.llm_service.analyze_job_description(job_text)
        
        # Score assessments based on job analysis
        scored_assessments = await self._score_assessments(job_analysis)
        
        # Sort by score and limit results
        top_assessments = sorted(scored_assessments, key=lambda x: x["score"], reverse=True)[:max_results]
        
        # Generate explanations for top matches
        results = []
        for item in top_assessments:
            assessment = item["assessment"]
            explanation = await self.llm_service.generate_match_explanation(job_analysis, assessment)
            
            results.append(RecommendationResult(
                assessment=Assessment(**assessment),
                score=item["score"],
                relevance_explanation=explanation
            ))
        
        return results
    
    async def _score_assessments(self, job_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score assessments based on job analysis using LLM"""
        # Prepare a prompt to score assessments
        assessments_data = json.dumps([{
            "id": a["id"],
            "name": a["name"],
            "test_type": a["test_type"]
        } for a in self.assessments], indent=2)
        
        prompt = f"""
        Given a job analysis and a list of assessments, score each assessment on a scale of 0-100 
        based on how relevant it is for evaluating candidates for the job.
        
        Job Analysis:
        {json.dumps(job_analysis, indent=2)}
        
        Available Assessments:
        {assessments_data}
        
        Return the results as a JSON array of objects, each with "id" and "score" properties.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in talent assessment and hiring."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the LLM's response
        scores = json.loads(response.choices[0].message.content)
        
        # Map scores back to full assessment objects
        result = []
        for score_item in scores:
            assessment = next((a for a in self.assessments if a["id"] == score_item["id"]), None)
            if assessment:
                result.append({
                    "assessment": assessment,
                    "score": score_item["score"]
                })
        
        return result

# URL Scraper Service
class URLScraperService:
    async def scrape_job_description(self, url: str) -> str:
        """Scrape job description from URL"""
        import httpx
        from bs4 import BeautifulSoup
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Common job description containers
            job_containers = soup.select('.job-description, .description, [class*=job], [class*=description]')
            
            if job_containers:
                return " ".join([container.get_text(strip=True) for container in job_containers])
            
            # Fallback to getting main content
            main_content = soup.select('main, article, .content')
            if main_content:
                return main_content[0].get_text(strip=True)
                
            # Last resort - get all text
            return soup.get_text(strip=True)

# Initialize services
llm_service = LLMService()
recommendation_service = RecommendationService(llm_service)
scraper_service = URLScraperService()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(request: JobDescription):
    try:
        # Handle URL input
        if request.url and not request.text:
            job_text = await scraper_service.scrape_job_description(request.url)
        else:
            job_text = request.text
            
        if not job_text:
            raise HTTPException(status_code=400, detail="No job description provided")
            
        # Get recommendations
        recommendations = await recommendation_service.get_recommendations(
            job_text, 
            max_results=request.max_results or 10
        )
        
        return RecommendationsResponse(recommendations=recommendations)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations", response_class=HTMLResponse)
async def recommendations_form(
    request: Request,
    job_description: str = Form(None),
    job_url: str = Form(None)
):
    try:
        # Handle form input
        if job_url and not job_description:
            job_text = await scraper_service.scrape_job_description(job_url)
        else:
            job_text = job_description
            
        if not job_text:
            return templates.TemplateResponse(
                "index.html", 
                {"request": request, "error": "Please provide a job description or URL"}
            )
            
        # Get recommendations
        recommendations = await recommendation_service.get_recommendations(job_text)
        
        return templates.TemplateResponse(
            "recommendations.html", 
            {
                "request": request,
                "recommendations": recommendations,
                "job_text": job_text
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "index.html", 
            {"request": request, "error": str(e)}
        )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)