"""
DeepSeek AI Analysis Helper for Resume-Job Matching
"""
import requests
import json
import os
from typing import Dict, Optional
from datetime import datetime


KEY = "sk-39d33f79efa643428aaec1f487e25546"

class DeepSeekAnalyzer:
    """Helper class for analyzing resume-job matches using DeepSeek AI"""
    
    def __init__(self, api_key: str = KEY):
        """
        Initialize the DeepSeek analyzer
        
        Args:
            api_key: DeepSeek API key. If not provided, will try to get from environment
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/chat/completions"
        
        if not self.api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass it to constructor.")
    
    def analyze_resume_match(self, job_description: str, resume_content: str) -> Dict[str, any]:
        """
        Analyze how well a resume matches a job description
        
        Args:
            job_description: The job description text
            resume_content: The extracted resume content
            
        Returns:
            Dict containing match score, reasoning, and analysis
        """
        try:
            # Prepare the prompt for DeepSeek
            prompt = self._create_analysis_prompt(job_description, resume_content)
            
            # Make the API call to DeepSeek
            response = self._call_deepseek_api(prompt)
            # return response
            
            # Parse and structure the response
            return self._parse_analysis_response(response)
            
        except Exception as e:
            print(e)
            return {
                "error": f"Analysis failed: {str(e)}",
                "match_score": 0,
                "reasoning": "Unable to analyze due to technical error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_analysis_prompt(self, job_description: str, resume_content: str) -> str:
        """Create the analysis prompt for DeepSeek"""
        return f"""
You are an expert HR recruiter and AI analyst. Your task is to analyze how well a candidate's resume matches a specific job description.

JOB DESCRIPTION:
{job_description}

RESUME CONTENT:
{resume_content}

Please analyze the match and provide:

1. A match score from 0-100 (where 100 is perfect match)
2. Detailed reasoning for the score
3. Key strengths of the candidate for this role
4. Areas where the candidate might need improvement
5. Overall recommendation (Strong Match, Good Match, Moderate Match, Weak Match, or Poor Match)

Format your response as JSON with the following structure:
{{
    "match_score": <number>,
    "reasoning": "<detailed explanation>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "improvement_areas": ["<area1>", "<area2>", ...],
    "recommendation": "<recommendation>",
    "summary": "<brief summary>"
}}

Be objective, thorough, and provide actionable insights.
"""
    
    def _call_deepseek_api(self, prompt: str) -> Dict:
        """Make the API call to DeepSeek"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "max_tokens": 2000,
            "top_p": 0.9
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(response)
        print(response.status_code)
        
        if response.status_code != 200:
            raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _parse_analysis_response(self, api_response: Dict) -> Dict[str, any]:
        """Parse and structure the DeepSeek API response"""
        try:
            # Extract the content from the API response
            content = api_response['choices'][0]['message']['content'].lstrip("```json").rstrip("```")
            
            # Try to parse the JSON response from DeepSeek
            analysis_data = json.loads(content)
            
            # Structure the final response
            return {
                "match_score": analysis_data.get("match_score", 0),
                "reasoning": analysis_data.get("reasoning", "No reasoning provided"),
                "strengths": analysis_data.get("strengths", []),
                "improvement_areas": analysis_data.get("improvement_areas", []),
                "recommendation": analysis_data.get("recommendation", "No recommendation"),
                "summary": analysis_data.get("summary", "No summary provided"),
                "timestamp": datetime.now().isoformat(),
                "error": None
            }
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # If parsing fails, return a structured error response
            return {
                "error": f"Failed to parse AI response: {str(e)}",
                "match_score": 0,
                "reasoning": "Unable to parse AI analysis",
                "strengths": [],
                "improvement_areas": [],
                "recommendation": "Unable to determine",
                "summary": "Analysis failed",
                "timestamp": datetime.now().isoformat(),
                "raw_response": api_response.get('choices', [{}])[0].get('message', {}).get('content', '')
            }

def analyze_resume_job_match(job_description: str, resume_content: str) -> Dict[str, any]:
    """
    Convenience function to analyze resume-job match using DeepSeek
    
    Args:
        job_description: The job description text
        resume_content: The extracted resume content
        api_key: Optional DeepSeek API key
        
    Returns:
        Dict containing match analysis results
    """
    analyzer = DeepSeekAnalyzer()
    return analyzer.analyze_resume_match(job_description, resume_content)
