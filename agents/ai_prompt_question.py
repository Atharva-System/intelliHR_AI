import re
import json
from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI
import logging
from config.Settings import settings
from app.models.resume_analyze_model import AIPromptQuestionRequest, AIPromptQuestionResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def clean_llm_output(output_text: str) -> str:
    """Clean and extract JSON from LLM output."""
    if not output_text:
        return ""
    
    # Remove markdown code blocks
    output_text = re.sub(r"^```(?:json)?\s*", "", output_text.strip())
    output_text = re.sub(r"\s*```$", "", output_text.strip())
    
    # Find JSON object
    json_match = re.search(r'\{[\s\S]*\}', output_text)
    if json_match:
        return json_match.group(0)
    
    return output_text.strip()


def generate_prompt_based_questions(request: AIPromptQuestionRequest) -> AIPromptQuestionResponse:
    """Generate interview questions based on user prompt."""
    
    # Empty prompt check
    if not request.prompt or request.prompt.strip() == "":
        return AIPromptQuestionResponse(questions_to_ask=[])
    
    # Initialize model
    llm = ChatOpenAI(
        model=settings.model,
        api_key=settings.openai_api_key,
        temperature=settings.temperature,
        max_tokens=settings.max_output_tokens
    )
    
    prompt = f"""You are an interview question generator.

USER PROMPT: {request.prompt}

RULES:
1. If the prompt is related to professional/interview topics (jobs, skills, technology, business, education), generate 5-15 relevant interview questions.
2. If the prompt is NOT related to professional/interview topics (casual chat, inappropriate content, random text, entertainment), return empty array.

VALID TOPICS: Technical skills, job roles, programming, management, soft skills, industry knowledge, education, business.

INVALID TOPICS: Casual conversation, jokes, recipes, entertainment, personal chat, inappropriate content, gibberish, random text,unique characters.

OUTPUT FORMAT (JSON only):
{{"questions_to_ask": ["question1", "question2", ...]}}

If invalid prompt, return:
{{"questions_to_ask": []}}

Return ONLY JSON, nothing else."""

    try:
        response = llm.invoke(prompt)
        
        if not response or not response.content:
            return AIPromptQuestionResponse(questions_to_ask=[])
        
        output_text = clean_llm_output(response.content)
        
        if not output_text:
            return AIPromptQuestionResponse(questions_to_ask=[])
        
        response_data = json.loads(output_text)
        return AIPromptQuestionResponse(**response_data)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON Error: {e}")
        return AIPromptQuestionResponse(questions_to_ask=[])
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return AIPromptQuestionResponse(questions_to_ask=[])


@router.post("/generate-prompt-questions", response_model=AIPromptQuestionResponse)
def ai_prompt_question_generator(request: AIPromptQuestionRequest):
    """Generate interview questions from user prompt."""
    try:
        return generate_prompt_based_questions(request)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))