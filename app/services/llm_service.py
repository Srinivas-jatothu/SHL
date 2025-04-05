# app/services/llm_service.py
import openai
from typing import List, Dict, Any
from app.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        openai.api_key = self.api_key
        
    async def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """
        Analyze job description using LLM to extract:
        - Required skills
        - Role category
        - Seniority level
        - Industry context
        - Key responsibilities
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
        
        Format as JSON.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a job analysis expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    async def generate_match_explanation(self, job_analysis: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """Generate explanation for why this assessment matches the job requirements"""
        # Implementation details...
        pass