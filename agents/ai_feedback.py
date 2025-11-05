import json
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import GoogleGenerativeAI
from app.models.feedback_model import FeedbackItem, FeedbackResponse
from config.Settings import api_key, settings
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel(settings.model)

llm = GoogleGenerativeAI(
    model=settings.model,
    google_api_key=api_key,
    temperature=settings.temperature,
    max_output_tokens=settings.max_output_tokens
)

parser = PydanticOutputParser(pydantic_object=FeedbackResponse)

template = """
You are an AI assistant that evaluates candidate feedback.

You will receive structured feedback input in JSON format.
The feedback list may contain ANY NUMBER of items, 
each with an "id", "content", and "keywords".

Analyze ALL the feedback items carefully.  

If the feedback is missing, incomplete, empty, or the content/keywords are insufficient for evaluation, 
return **all fields** with the value "Insufficient data".

Otherwise, generate a structured evaluation following this schema:

{format_instructions}

Input Feedback (variable length list):
{feedback}

Answer strictly in JSON.
"""


prompt = PromptTemplate(
    input_variables=["feedback"],
    template=template,
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser


def evaluate_feedback(feedback: list[FeedbackItem]) -> FeedbackResponse:
    feedback_json = json.dumps([item.dict() for item in feedback], indent=2)
    return chain.invoke({"feedback": feedback_json})
