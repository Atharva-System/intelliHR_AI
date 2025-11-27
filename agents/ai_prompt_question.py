import re
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException
import google.generativeai as genai
import logging
from config.Settings import api_key, settings
from app.models.resume_analyze_model import AIPromptQuestionRequest, AIPromptQuestionResponse

logger = logging.getLogger(__name__)

genai.configure(api_key=api_key)

router = APIRouter()

BLOCKED_KEYWORDS = [
    "porn", "sex", "nude", "xxx", "kill", "murder", "drug", "cocaine",
    "hack", "crack", "pirate", "torrent", "illegal", "bomb", "weapon",
    "suicide", "self-harm", "abuse", "racist", "hate"
]


def clean_llm_output(output_text: str) -> str:
    """Clean and extract JSON from LLM output."""
    if not output_text:
        return ""
    
    output_text = re.sub(r"^```(?:json)?\s*", "", output_text.strip())
    output_text = re.sub(r"\s*```$", "", output_text.strip())
    
    json_match = re.search(r'\{[\s\S]*\}', output_text)
    if json_match:
        return json_match.group(0)
    
    return output_text.strip()


def is_blocked_content(prompt: str) -> bool:
    """Check if prompt contains blocked keywords."""
    prompt_lower = prompt.lower()
    return any(keyword in prompt_lower for keyword in BLOCKED_KEYWORDS)


def is_gibberish(prompt: str) -> bool:
    if len(prompt) < 5:
        if any(c.isalpha() for c in prompt):
            return False
            
    alpha_count = sum(1 for c in prompt if c.isalpha())
    if len(prompt) > 0 and alpha_count / len(prompt) < 0.3:
        return True
    
    if re.match(r'^(.)\1+$', prompt.strip()):
        return True
    
    return False


def generate_prompt_based_questions(request: AIPromptQuestionRequest) -> AIPromptQuestionResponse:
    if not request.prompt or request.prompt.strip() == "":
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message="Please provide a valid prompt to generate questions."
        )
    
    prompt_text = request.prompt.strip()

    if len(prompt_text) < 3:
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message="Prompt is too short. Please provide a meaningful topic."
        )
    
    if is_blocked_content(prompt_text):
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message="The prompt contains inappropriate content. Please provide a professional topic."
        )
    
    if is_gibberish(prompt_text):
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message="The prompt appears to be invalid. Please provide a clear topic."
        )
    
    model = genai.GenerativeModel(
        model_name=settings.model,
        generation_config={
            "temperature": getattr(settings, 'temperature', 0.7),
            "max_output_tokens": getattr(settings, 'max_output_tokens', 2048),
        }
    )
    
    prompt = f"""You are an intelligent interview question generator.

CRITICAL VALIDATION RULES:
First, determine if the user prompt is related to professional/interview topics.

VALID TOPICS (Generate questions for these):
- Technical skills (programming, software, databases, cloud, etc.)
- Job roles (developer, manager, analyst, designer, etc.)
- Professional domains (IT, healthcare, finance, marketing, HR, etc.)
- Soft skills (communication, leadership, problem-solving)
- Educational subjects (mathematics, science, languages, etc.)
- Business topics (management, strategy, operations)
- Industry knowledge

INVALID TOPICS (Return empty questions for these):
- Casual conversation (hi, hello, how are you, etc.)
- Personal questions unrelated to work
- Entertainment (movies, games, jokes, recipes)
- Random or meaningless text
- Inappropriate content
- Questions about yourself as an AI
- General knowledge trivia unrelated to professional skills

USER PROMPT: {prompt_text}

INSTRUCTIONS:
1. If the prompt is VALID (professional/interview related):
   - Generate 5-15 relevant interview questions
   - Questions should assess knowledge, skills, and experience
   - Include technical, behavioral, and situational questions
   
2. If the prompt is INVALID (not professional/interview related):
   - Return empty questions array
   - Set is_valid_prompt to false
   - Provide a helpful message

OUTPUT FORMAT (JSON only, no other text):
{{"questions_to_ask": ["q1", "q2", ...], "is_valid_prompt": true/false, "message": "appropriate message"}}"""

    output_text = ""
    
    try:
        logger.info(f"Processing prompt: {prompt_text[:100]}...")
        
        response = model.generate_content(prompt)
        
        try:
            text = response.text
        except ValueError:
            return AIPromptQuestionResponse(
                questions_to_ask=[],
                is_valid_prompt=False,
                message="The prompt triggered safety filters. Please try a different topic."
            )

        if not response or not text:
            return AIPromptQuestionResponse(
                questions_to_ask=[],
                is_valid_prompt=False,
                message="Failed to generate questions. Please try again."
            )
        
        output_text = clean_llm_output(text)
        
        if not output_text:
            return AIPromptQuestionResponse(
                questions_to_ask=[],
                is_valid_prompt=False,
                message="Failed to process the prompt."
            )
        
        response_data = json.loads(output_text)
        validated_response = AIPromptQuestionResponse(**response_data)
        
        logger.info(f"Response: valid={validated_response.is_valid_prompt}, questions={len(validated_response.questions_to_ask or [])}")
        
        return validated_response
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Error: {e}, Output: '{output_text}'")
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message="Failed to parse response. Please try again."
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return AIPromptQuestionResponse(
            questions_to_ask=[],
            is_valid_prompt=False,
            message=f"An error occurred: {str(e)}"
        )


@router.post("/generate-prompt-questions", response_model=AIPromptQuestionResponse)
def ai_prompt_question_generator(request: AIPromptQuestionRequest):
    """API endpoint to generate interview questions based on user prompt."""
    try:
        return generate_prompt_based_questions(request)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))