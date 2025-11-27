from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import api_key, settings
import google.generativeai as genai
from app.models.feedback_model import EnhanceFeedbackRequest,EnhanceFeedbackResponse


genai.configure(api_key=api_key)

llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

parser = PydanticOutputParser(pydantic_object=EnhanceFeedbackResponse)


template = """
You are an AI assistant specializing in refining interview feedback.

Your task is to take raw, potentially brief or unstructured notes from an interviewer and transform them into professional, detailed, and actionable feedback.

**Input Data:**
- **Context:** {context} (The specific section of the interview form)
- **Original Text:** {text}

**Instructions:**
1. **Expand & Clarify:** Turn brief bullet points into complete sentences.
2. **Professional Tone:** Ensure the language is objective and professional.
3. **Context Aware:**
   - If context is 'technicalSkills': Focus on depth of knowledge, specific technologies, and problem-solving.
   - If context is 'communication': Focus on clarity, listening, and articulation.
   - If context is 'culturalFit': Focus on values, teamwork, and adaptability.
4. **Maintain Meaning:** Do not invent facts. Only enhance how the existing observations are presented. If the input is very short, you may add generic bridging phrases but keep the core observation true to the input.

{format_instructions}

**Input:**
Context: {context}
Text: {text}

Answer strictly in JSON.
"""

prompt = PromptTemplate(
    input_variables=["text", "context"],
    template=template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)



chain = prompt | llm | parser


def enhance_feedback(request: EnhanceFeedbackRequest) -> EnhanceFeedbackResponse:
    if not request.text or not request.text.strip():
        return EnhanceFeedbackResponse(enhanced="")

    return chain.invoke({
        "text": request.text,
        "context": request.context or "general"
    })