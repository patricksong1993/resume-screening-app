"""
Qwen-Plus AI Analysis Helper for Resume-Job Matching
"""
from openai import OpenAI
import json
import os
import time
import functools
import logging
import traceback
from typing import Dict, Optional
from datetime import datetime

# Configure logging for this module
logger = logging.getLogger(__name__)



def timing_wrapper(func):
    """Decorator to measure function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Add timing information to the result
            if isinstance(result, dict):
                result['processing_time'] = round(processing_time, 3)
                result['processing_time_ms'] = round(processing_time * 1000, 1)
                print(f"⏱️  Analysis completed in {processing_time:.3f}s ({processing_time * 1000:.1f}ms)")
            
            return result
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            print(f"❌ Analysis failed after {processing_time:.3f}s: {str(e)}")
            raise
    return wrapper


class QwenAnalyzer:
    """Helper class for analyzing resume-job matches using Alibaba Cloud Qwen-Plus"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Qwen-Plus analyzer
        
        Args:
            api_key: Alibaba Cloud API key. If not provided, will try to get from environment
        """
        self.api_key = os.environ["API_KEY"]
        
        # Initialize OpenAI client with custom base URL for Qwen
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        if not self.api_key:
            raise ValueError("Qwen API key is required. Set QWEN_API_KEY environment variable or pass it to constructor.")
    
    @timing_wrapper
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
            # Prepare the prompt for Qwen-Plus
            prompt = self._create_analysis_prompt(job_description, resume_content)
            
            # Make the API call to Qwen-Plus using OpenAI SDK
            response = self._call_qwen_api(prompt)
            
            # Parse and structure the response
            return self._parse_analysis_response(response)
            
        except Exception as e:
            print(f"Qwen analysis error: {e}")
            return {
                "error": f"Analysis failed: {str(e)}",
                "match_score": 0,
                "reasoning": "Unable to analyze due to technical error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_analysis_prompt(self, job_description: str, resume_content: str) -> str:
        """Create the analysis prompt for Qwen-Plus"""
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
    "candidate_name": "<candidate name if found>",
    "match_score": <number>,
    "reasoning": "<detailed explanation>",
    "strengths": ["<strength1>", "<strength2>", ...],
    "improvement_areas": ["<area1>", "<area2>", ...],
    "recommendation": "<recommendation>",
    "summary": "<brief summary>"
}}

Be objective, thorough, and provide actionable insights. Focus on specific skills, experience, and qualifications mentioned in both the job description and resume.
"""
    
    def _call_qwen_api(self, prompt: str) -> Dict:
        """Make the API call to Qwen-Plus using OpenAI SDK"""
        try:
            response = self.client.chat.completions.create(
                model="qwen-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000,
                top_p=0.9
            )
            
            print(f"Qwen API call successful")
            
            # Convert response to dict format for compatibility
            return {
                "choices": [
                    {
                        "message": {
                            "content": response.choices[0].message.content
                        }
                    }
                ]
            }
            
        except Exception as e:
            print(f"Qwen API error: {e}")
            raise Exception(f"Qwen API error: {str(e)}")
    
    def _parse_analysis_response(self, api_response: Dict) -> Dict[str, any]:
        """Parse and structure the Qwen API response"""
        try:
            # Extract the content from the API response (OpenAI SDK format)
            content = api_response['choices'][0]['message']['content']
            
            # Clean up potential JSON markers
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse the JSON response from Qwen
            analysis_data = json.loads(content)
            
            # Structure the final response
            return {
                "candidate_name": analysis_data.get("candidate_name", "Unknown"),
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
            print(f"Failed to parse Qwen response: {e}")
            raw_content = ""
            try:
                raw_content = api_response['choices'][0]['message']['content']
            except:
                raw_content = str(api_response)
                
            return {
                "candidate_name": "Unknown",
                "error": f"Failed to parse AI response: {str(e)}",
                "match_score": 0,
                "reasoning": "Unable to parse AI analysis",
                "strengths": [],
                "improvement_areas": [],
                "recommendation": "Unable to determine",
                "summary": "Analysis failed",
                "timestamp": datetime.now().isoformat(),
                "raw_response": raw_content
            }


@timing_wrapper
def analyze_resume_job_match_qwen(job_description: str, resume_content: str, api_key: str = None) -> Dict[str, any]:
    """
    Convenience function to analyze resume-job match using Qwen-Plus with timing
    
    Args:
        job_description: The job description text
        resume_content: The extracted resume content
        api_key: Optional Qwen API key
        
    Returns:
        Dict containing match analysis results with timing information
    """
    logger.info("🤖 Starting Qwen analysis")
    logger.debug(f"📊 Input lengths - Job: {len(job_description)} chars, Resume: {len(resume_content)} chars")
    
    try:
        analyzer = QwenAnalyzer(api_key=api_key)
        result = analyzer.analyze_resume_match(job_description, resume_content)
        
        logger.info(f"✅ Qwen analysis completed successfully")
        logger.debug(f"📊 Result summary - Candidate: {result.get('candidate_name', 'Unknown')}, Score: {result.get('match_score', 0)}")
        
        return result
    except Exception as e:
        logger.error(f"❌ Qwen analysis failed: {str(e)}")
        logger.error(f"🔍 Full traceback:")
        logger.error(traceback.format_exc())
        raise


def analyze_resume_job_match_qwen_with_detailed_timing(job_description: str, resume_content: str, api_key: str = None) -> Dict[str, any]:
    """
    Enhanced wrapper with detailed timing breakdown
    
    Args:
        job_description: The job description text
        resume_content: The extracted resume content
        api_key: Optional Qwen API key
        
    Returns:
        Dict containing match analysis results with detailed timing breakdown
    """
    overall_start = time.time()
    
    print(f"🚀 Starting detailed Qwen analysis...")
    print(f"📄 Job description: {len(job_description)} characters")
    print(f"📝 Resume content: {len(resume_content)} characters")
    
    # Initialize analyzer
    init_start = time.time()
    analyzer = QwenAnalyzer(api_key=api_key)
    init_time = time.time() - init_start
    print(f"⚡ Analyzer initialization: {init_time:.3f}s")
    
    # Prepare prompt
    prompt_start = time.time()
    prompt = analyzer._create_analysis_prompt(job_description, resume_content)
    prompt_time = time.time() - prompt_start
    prompt_length = len(prompt)
    print(f"📝 Prompt preparation: {prompt_time:.3f}s ({prompt_length} chars)")
    
    # API call
    api_start = time.time()
    try:
        api_response = analyzer._call_qwen_api(prompt)
        api_time = time.time() - api_start
        print(f"🌐 API call: {api_time:.3f}s")
    except Exception as e:
        api_time = time.time() - api_start
        print(f"❌ API call failed after {api_time:.3f}s: {str(e)}")
        raise
    
    # Parse response
    parse_start = time.time()
    try:
        result = analyzer._parse_analysis_response(api_response)
        parse_time = time.time() - parse_start
        print(f"🔍 Response parsing: {parse_time:.3f}s")
    except Exception as e:
        parse_time = time.time() - parse_start
        print(f"❌ Response parsing failed after {parse_time:.3f}s: {str(e)}")
        raise
    
    # Calculate total time
    total_time = time.time() - overall_start
    
    # Add detailed timing to result
    result.update({
        'timing_breakdown': {
            'initialization_time': round(init_time, 3),
            'prompt_preparation_time': round(prompt_time, 3),
            'api_call_time': round(api_time, 3),
            'response_parsing_time': round(parse_time, 3),
            'total_time': round(total_time, 3)
        },
        'processing_time': round(total_time, 3),
        'processing_time_ms': round(total_time * 1000, 1),
        'prompt_length': prompt_length
    })
    
    print(f"🎉 Total analysis time: {total_time:.3f}s ({total_time * 1000:.1f}ms)")
    print(f"📊 Match score: {result.get('match_score', 0)}%")
    
    return result
