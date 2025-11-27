from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from config.Settings import api_key, settings
import google.generativeai as genai
from app.models.evaluation_model import InterviewSummaryRequest, EvaluationResponse


genai.configure(api_key=api_key)

llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

parser = PydanticOutputParser(pydantic_object=EvaluationResponse)


template = """
You are an expert HR AI assistant. Analyze the interview feedback and provide a hiring recommendation.

**Interview Feedback:**

1. Technical Skills & Expertise: {technical_skills}
2. Communication & Collaboration: {communication_collaboration}
3. Cultural Fit & Values Alignment: {cultural_fit_values}
4. Problem-Solving & Critical Thinking: {problem_solving}
5. Key Strengths & Highlights: {key_strengths}
6. Additional Observations: {additional_observations}

**Recommendation Guidelines:**
- **strong_hire**: Exceptional candidate, exceeds expectations in most areas
- **hire**: Good candidate, meets expectations with minor gaps
- **maybe**: Mixed results, needs additional assessment
- **no_hire**: Does not meet requirements, significant concerns

{format_instructions}

Answer strictly in JSON.
"""

prompt = PromptTemplate(
    input_variables=[
        "technical_skills",
        "communication_collaboration",
        "cultural_fit_values",
        "problem_solving",
        "key_strengths",
        "additional_observations"
    ],
    template=template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser


def evaluate_interview(request: InterviewSummaryRequest) -> EvaluationResponse:
    def safe_text(value: str, default: str = "No information provided") -> str:
        return value.strip() if value and value.strip() else default
    
    return chain.invoke({
        "technical_skills": safe_text(request.technicalSkills),
        "communication_collaboration": safe_text(request.communicationCollaboration),
        "cultural_fit_values": safe_text(request.culturalFitValues),
        "problem_solving": safe_text(request.problemSolvingCriticalThinking),
        "key_strengths": safe_text(request.keyStrengthsHighlights),
        "additional_observations": safe_text(request.additionalObservations)
    })