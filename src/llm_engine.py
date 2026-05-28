#import dependencies
import os
import json
import logging
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from src.models.review_schema import AIReviewResult

logger = logging.getLogger("llm_engine")

# Load .env
load_dotenv(override=True)

class LLMEngine:
    def __init__(self):
        # 1. READ THE NEW VARIABLE NAME
        self.api_key = os.getenv("MY_NEW_GEMINI_KEY")
        
        if not self.api_key:
            logger.error("MY_NEW_GEMINI_KEY is missing in .env!")
        
        # 2. Configure the STABLE library
        if self.api_key:
            genai.configure(api_key=self.api_key)
            
        # 3. USE A MODEL FROM YOUR LIST
        # We are using "gemini-2.0-flash" because your script proved you have it.
        self.model = genai.GenerativeModel('gemini-flash-latest')

    async def analyze_code(self, diff: str, persona: str, mode: str) -> AIReviewResult:
        logger.info(f"Gemini: Analyzing {len(diff)} chars (Persona: {persona})")

        persona_map = {
            "security": "You are a Security Engineer. Focus on OWASP, secrets, and auth.",
            "developer": "You are a Senior Python Dev. Focus on bugs and clean code.",
        }
        
        # We put instructions in the prompt to avoid API complexity
        full_prompt = f"""
        ROLE: {persona_map.get(persona, "developer")}
        
        TASK:
        Analyze the provided Git Diff.
        
        STRICT OUTPUT FORMAT:
        You must return ONLY valid JSON. Do not use markdown blocks (```json).
        The JSON must match this structure exactly:
        {{
            "summary": "High-level summary...",
            "findings": [
                {{
                    "file_path": "path/to/file.py",
                    "line_start": 10,
                    "line_end": 12,
                    "severity": "CRITICAL",
                    "category": "SECURITY",
                    "suggestion": "Fix advice...",
                    "code_snippet": "code"
                }}
            ],
            "security_score": 85,
            "is_blocking": false
        }}

        GIT DIFF:
        {diff}
        """

        try:
            # 3. Call Gemini (Async Wrapper)
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            # 4. Parse Response
            raw_text = response.text.strip()
            
            # Clean up markdown if present
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            return AIReviewResult.model_validate_json(raw_text)

        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return AIReviewResult(
                summary=f"Analysis Failed: {str(e)}",
                security_score=0,
                is_blocking=False,
                findings=[]
            )